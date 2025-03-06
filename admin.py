from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AuditLog

# Change Admin Header and Title
admin.site.site_header = _("Home-Run Admin")  # Title on top left
admin.site.site_title = _("Home-Run Admin")  # Title on browser tab
admin.site.index_title = _("Welcome to Home-Run")  # Index title on dashboard


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'record_id', 'action', 'performed_by', 'timestamp')
    list_filter = ('table_name', 'action', 'performed_by')
    search_fields = ('record_id',)

admin.site.register(AuditLog, AuditLogAdmin)
