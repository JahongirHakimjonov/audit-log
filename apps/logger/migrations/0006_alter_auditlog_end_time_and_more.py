# Generated by Django 5.0.8 on 2025-01-26 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("logger", "0005_testdata"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditlog",
            name="end_time",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="auditlog",
            name="execution_time",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="auditlog",
            name="start_time",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
