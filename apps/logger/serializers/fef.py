from rest_framework import serializers

from apps.logger.models.rgrg import TestData


class TestDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestData
        fields = "__all__"
