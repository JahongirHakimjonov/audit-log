from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.logger.views.auditlog import AdminDashboardView
from apps.logger.views.ef import TestDataViewSet
app_name = "logger"

router = DefaultRouter()
router.register(r'test-data', TestDataViewSet, basename='testdata')

urlpatterns = [
    path("admin-dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

]
