from django.views.generic import ListView
from django.core.paginator import Paginator
from django.shortcuts import render
from apps.logger.models.logs import AuditLog

class AdminDashboardView(ListView):
    model = AuditLog
    template_name = "admin_dashboard.html"
    context_object_name = "page_obj"
    paginate_by = 20

    def get_queryset(self):
        user_groups = self.request.user.groups.values_list('name', flat=True)
        filters = {
            "action__icontains": self.request.GET.get("action", ""),
            "user__username__icontains": self.request.GET.get("user", ""),
        }

        if 'Admin' in user_groups:
            return AuditLog.fetch_logs(filters={k: v for k, v in filters.items() if v})
        else:
            return AuditLog.fetch_logs(filters={"user": self.request.user})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context