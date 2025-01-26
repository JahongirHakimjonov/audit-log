from django.core.management.base import BaseCommand
import apps.logger.models.logs
from apps.logger.utils.data_deletion import delete_model


class Command(BaseCommand):
    help = "Clears silk's log of requests."

    def handle(self, *args, **options):
        # Django takes a long time to traverse foreign key relations,
        # so delete in the order that makes it easy.
        delete_model(apps.logger.models.logs.AuditLog)
