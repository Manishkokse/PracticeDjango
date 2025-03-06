from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import json

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)  # Integer primary key
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        abstract = True  # Ensures this model is used as a base class only

# Audit Log Model
class AuditLog(models.Model):
    table_name = models.CharField(max_length=255)
    record_id = models.IntegerField()  # Assuming ID is Integer, adjust for UUID if needed
    action = models.CharField(max_length=10, choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')])
    changed_data = models.JSONField()  # This field must not be null
    performed_by = models.CharField(max_length=255, blank=True, null=True)  # Store username or system ID
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} - {self.table_name} - {self.record_id}"

# Signal for tracking Create and Update
@receiver(post_save)
def track_create_update(sender, instance, created, **kwargs):
    if not issubclass(sender, BaseModel):  # Ensure it's only applied to BaseModel subclasses
        return
    
    action = 'CREATE' if created else 'UPDATE'
    
    # Prepare changed_data: exclude internal fields like '_state'
    changed_data = {key: value for key, value in instance.__dict__.items() if not key.startswith('_')}
    changed_data.pop('_state', None)  # Remove internal state field that can't be serialized
    
    # If the changed_data is still empty, provide a default value
    if not changed_data:
        changed_data = {"default": "no_changes"}  # A default value when no changes are detected
    
    # Create the AuditLog entry
    AuditLog.objects.create(
        table_name=sender.__name__,
        record_id=instance.id,
        action=action,
        changed_data=changed_data,  # Valid JSON object
        performed_by=getattr(instance, 'updated_by', None)  # Capture user if available
    )

# Signal for tracking Delete
@receiver(pre_delete)
def track_delete(sender, instance, **kwargs):
    if not issubclass(sender, BaseModel):  # Ensure it's only applied to BaseModel subclasses
        return

    # Prepare changed_data: exclude internal fields like '_state'
    changed_data = {key: value for key, value in instance.__dict__.items() if not key.startswith('_')}
    changed_data.pop('_state', None)  # Remove internal state field that can't be serialized

    # If the changed_data is still empty, provide a default value
    if not changed_data:
        changed_data = {"default": "deleted"}  # A default value when no changes are detected
    
    # Create the AuditLog entry
    AuditLog.objects.create(
        table_name=sender.__name__,
        record_id=instance.id,
        action='DELETE',
        changed_data=changed_data,  # Valid JSON object
        performed_by=getattr(instance, 'updated_by', None)  # Capture user if available
    )
