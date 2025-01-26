from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from apps.logger.models.rgrg import TestData
from apps.logger.serializers.fef import TestDataSerializer


class TestDataViewSet(ModelViewSet):
    serializer_class = TestDataSerializer
    queryset = TestData.objects.all()
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']
