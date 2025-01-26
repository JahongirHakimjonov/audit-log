import json
import time

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from apps.logger.models.logs import AuditLog
from apps.logger.utils.auditlog import get_client_ip

# Configuration settings
LOG_LEVEL = getattr(settings, 'AUDIT_LOG_LEVEL', 'INFO')
LOG_FORMAT = getattr(settings, 'AUDIT_LOG_FORMAT',
                     '{timestamp} {user} {action} {model_name} {object_id} {details} {ip_address} {user_agent} {request_data} {response_data} {errors} {old_data} {new_data} {changed_fields} {headers} {start_time} {end_time} {execution_time}')
LOG_STATUS_CODES = getattr(settings, 'AUDIT_LOG_STATUS_CODES', [200, 201, 204])
ENABLE_LOGGING = getattr(settings, 'AUDIT_LOG_ENABLE', True)
LOG_IP_ADDRESS = getattr(settings, 'AUDIT_LOG_IP_ADDRESS', True)
LOG_USER_AGENT = getattr(settings, 'AUDIT_LOG_USER_AGENT', True)
LOG_HEADERS = getattr(settings, 'AUDIT_LOG_HEADERS', True)
MAX_LOG_LENGTH = getattr(settings, 'AUDIT_LOG_MAX_LENGTH', 1000)

try:
    EXCLUDE_URLS = [url for url in settings.AUDIT_LOG_EXCLUDE_URLS if url] if settings.AUDIT_LOG_EXCLUDE_URLS else []
except ImproperlyConfigured:
    EXCLUDE_URLS = []


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not ENABLE_LOGGING or any(request.path.startswith(url) for url in EXCLUDE_URLS):
            return self.get_response(request)

        # Record start time
        request.start_time = time.time()

        request_data = self._parse_request_data(request)
        old_data = self._get_old_data(request) if request.method in ["PUT", "PATCH"] else None

        response = self.get_response(request)

        # Record end time and calculate execution time
        request.end_time = time.time()
        execution_time = request.end_time - request.start_time

        if request.user.is_authenticated:
            action = self._detect_action(request)
            if action and response.status_code in LOG_STATUS_CODES:
                response_data, errors = self._parse_response_data(response)
                self._create_audit_log(request, action, request_data, response_data, errors, old_data, execution_time)
        else:
            self._log_failed_authentication_attempt(request, execution_time)

        return response

    @staticmethod
    def _parse_request_data(request):
        try:
            data = json.loads(request.body.decode("utf-8")) if request.body else {}
            return {k: (v[:MAX_LOG_LENGTH] + '...') if isinstance(v, str) and len(v) > MAX_LOG_LENGTH else v for k, v in
                    data.items()}
        except json.JSONDecodeError:
            return {"error": "Invalid request data."}

    @staticmethod
    def _parse_response_data(response):
        try:
            data = json.loads(response.content.decode("utf-8"))
            return {k: (v[:MAX_LOG_LENGTH] + '...') if isinstance(v, str) and len(v) > MAX_LOG_LENGTH else v for k, v in
                    data.items()}, None
        except json.JSONDecodeError:
            return {}, {"error": "Invalid response data."}

    def _get_old_data(self, request):
        if request.resolver_match and hasattr(request.resolver_match.func, 'view_class'):
            model = request.resolver_match.func.view_class.queryset.model
            return get_object_or_404(model, pk=request.resolver_match.kwargs.get("pk"))
        return None

    @staticmethod
    def _detect_action(request):
        actions = {
            "POST": "POST",
            "PUT": "PUT",
            "PATCH": "PATCH",
            "DELETE": "DELETE"
        }
        return actions.get(request.method)

    def _create_audit_log(self, request, action, request_data, response_data, errors, old_data, execution_time):
        new_data = request.POST.dict() if action in ["CREATE", "UPDATE"] else None
        changed_fields = {}
        if old_data and new_data:
            changed_fields = {field: (getattr(old_data, field), new_data[field]) for field in new_data if
                              getattr(old_data, field) != new_data[field]}

        log_entry = LOG_FORMAT.format(
            timestamp=now().isoformat(),
            user=request.user,
            action=action,
            model_name=request.resolver_match.app_name,
            object_id=request.resolver_match.kwargs.get("pk"),
            details=request.POST.dict() if action != "DELETE" else {},
            ip_address=get_client_ip(request) if LOG_IP_ADDRESS else 'Disabled',
            user_agent=request.META.get("HTTP_USER_AGENT", "Unknown") if LOG_USER_AGENT else 'Disabled',
            request_data=request_data,
            response_data=response_data,
            errors=errors,
            old_data=old_data,
            new_data=new_data,
            changed_fields=changed_fields,
            headers={k: (v[:MAX_LOG_LENGTH] + '...') if len(v) > MAX_LOG_LENGTH else v for k, v in
                     request.headers.items()} if LOG_HEADERS else 'Disabled',
            start_time=request.start_time,
            end_time=request.end_time,
            execution_time=execution_time
        )

        if self._should_log(log_entry):
            AuditLog.objects.create(
                user=request.user,
                action=action,
                model_name=request.resolver_match.app_name,
                object_id=request.resolver_match.kwargs.get("pk"),
                details=request.POST.dict() if action != "DELETE" else {},
                ip_address=get_client_ip(request) if LOG_IP_ADDRESS else 'Disabled',
                user_agent=request.META.get("HTTP_USER_AGENT", "Unknown") if LOG_USER_AGENT else 'Disabled',
                timestamp=now().isoformat(),
                request_data=request_data,
                response_data=response_data,
                errors=errors,
                old_data=old_data,
                new_data=new_data,
                changed_fields=changed_fields,
                headers={k: (v[:MAX_LOG_LENGTH] + '...') if len(v) > MAX_LOG_LENGTH else v for k, v in
                         request.headers.items()} if LOG_HEADERS else 'Disabled',
                start_time=request.start_time,
                end_time=request.end_time,
                execution_time=execution_time,
                log_entry=log_entry
            )

    def _log_failed_authentication_attempt(self, request, execution_time):
        if request.method == "POST" and "login" in request.path.lower():
            log_entry = LOG_FORMAT.format(
                timestamp=now(),
                user=None,
                action="FAILED_AUTHENTICATION",
                model_name="auth",
                object_id=None,
                details={"username": request.POST.get("username")},
                ip_address=get_client_ip(request) if LOG_IP_ADDRESS else 'Disabled',
                user_agent=request.META.get("HTTP_USER_AGENT", "Unknown") if LOG_USER_AGENT else 'Disabled',
                request_data=self._parse_request_data(request),
                response_data={},
                errors={"error": "Failed authentication attempt."},
                old_data=None,
                new_data=None,
                changed_fields=None,
                headers={k: (v[:MAX_LOG_LENGTH] + '...') if len(v) > MAX_LOG_LENGTH else v for k, v in
                         request.headers.items()} if LOG_HEADERS else 'Disabled',
                start_time=request.start_time,
                end_time=request.end_time,
                execution_time=execution_time
            )
            if self._should_log(log_entry):
                AuditLog.objects.create(
                    user=None,
                    action="FAILED_AUTHENTICATION",
                    model_name="auth",
                    object_id=None,
                    details={"username": request.POST.get("username")},
                    ip_address=get_client_ip(request) if LOG_IP_ADDRESS else 'Disabled',
                    user_agent=request.META.get("HTTP_USER_AGENT", "Unknown") if LOG_USER_AGENT else 'Disabled',
                    timestamp=now(),
                    request_data=self._parse_request_data(request),
                    response_data={},
                    errors={"error": "Failed authentication attempt."},
                    old_data=None,
                    new_data=None,
                    changed_fields=None,
                    headers={k: (v[:MAX_LOG_LENGTH] + '...') if len(v) > MAX_LOG_LENGTH else v for k, v in
                             request.headers.items()} if LOG_HEADERS else 'Disabled',
                    start_time=request.start_time,
                    end_time=request.end_time,
                    execution_time=execution_time,
                    log_entry=log_entry
                )

    def _should_log(self, log_entry):
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        return levels.index(LOG_LEVEL) <= levels.index('INFO')  # Adjust this condition as needed
