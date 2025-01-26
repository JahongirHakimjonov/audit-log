from json import JSONEncoder

from django.contrib.auth.models import User
from django.db import models

from apps.shared.models import AbstractBaseModel


class PrettyJSONEncoder(JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)


class AuditLog(AbstractBaseModel):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=255, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    details = models.JSONField(null=True, blank=True, encoder=PrettyJSONEncoder)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    request_data = models.JSONField(null=True, blank=True, encoder=PrettyJSONEncoder)
    response_data = models.JSONField(null=True, blank=True, encoder=PrettyJSONEncoder)
    errors = models.JSONField(null=True, blank=True, encoder=PrettyJSONEncoder)
    old_data = models.JSONField(null=True, blank=True, encoder=PrettyJSONEncoder)
    new_data = models.JSONField(null=True, blank=True, encoder=PrettyJSONEncoder)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["user", "action"]),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"

    @classmethod
    def fetch_logs(cls, filters=None, limit=100):
        queryset = cls.objects.select_related("user").order_by("-timestamp")
        if filters:
            queryset = queryset.filter(**filters)
        return queryset[:limit]
