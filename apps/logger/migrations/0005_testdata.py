# Generated by Django 5.0.8 on 2025-01-26 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("logger", "0004_auditlog_changed_fields_auditlog_end_time_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TestData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Test Data",
                "verbose_name_plural": "Test Data",
            },
        ),
    ]
