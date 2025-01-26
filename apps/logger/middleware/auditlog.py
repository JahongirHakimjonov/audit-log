import json
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from apps.logger.models.logs import AuditLog
from apps.logger.utils.auditlog import get_client_ip


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_data = self._parse_request_data(request)
        old_data = self._get_old_data(request) if request.method in ["PUT", "PATCH"] else None

        response = self.get_response(request)

        if request.user.is_authenticated:
            action = self._detect_action(request)
            if action:
                response_data, errors = self._parse_response_data(response)
                self._create_audit_log(request, action, request_data, response_data, errors, old_data)

        return response

    @staticmethod
    def _parse_request_data(request):
        try:
            return json.loads(request.body.decode("utf-8")) if request.body else {}
        except json.JSONDecodeError:
            return {"error": "Invalid request data."}

    @staticmethod
    def _parse_response_data(response):
        try:
            return json.loads(response.content.decode("utf-8")), None
        except json.JSONDecodeError:
            return {}, {"error": "Invalid response data."}

    def _get_old_data(self, request):
        model = request.resolver_match.func.view_class.queryset.model
        obj = get_object_or_404(model, pk=request.resolver_match.kwargs.get("pk"))
        return obj

    @staticmethod
    def _detect_action(request):
        if request.method == "POST":
            return "CREATE"
        elif request.method in ["PUT", "PATCH"]:
            return "UPDATE"
        elif request.method == "DELETE":
            return "DELETE"
        return None

    def _create_audit_log(self, request, action, request_data, response_data, errors, old_data):
        AuditLog.objects.create(
            user=request.user,
            action=action,
            model_name=request.resolver_match.app_name,
            object_id=request.resolver_match.kwargs.get("pk", None),
            details=request.POST.dict() if action != "DELETE" else {},
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "Unknown"),
            timestamp=now(),
            request_data=request_data,
            response_data=response_data,
            errors=errors,
            old_data=old_data,
            new_data=request.POST.dict() if action in ["CREATE", "UPDATE"] else None
        )
