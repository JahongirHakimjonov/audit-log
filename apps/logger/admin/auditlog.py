from django.contrib import admin

from apps.logger.models.logs import AuditLog
from apps.logger.utils.admin import get_admin_model

ModelAdmin = get_admin_model(name="unfold")


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ("user", "action", "model_name", "object_id", "ip_address", "timestamp", "user_agent")
    search_fields = ("user__username", "action", "model_name", "object_id")
    list_filter = ("timestamp", "action")
    ordering = ("-timestamp",)
    autocomplete_fields = ("user",)
