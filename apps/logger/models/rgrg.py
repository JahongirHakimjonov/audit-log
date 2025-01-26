from django.db import models

from apps.shared.models import AbstractBaseModel


class TestData(AbstractBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Test Data"
        verbose_name_plural = "Test Data"

    def __str__(self):
        return self.name
