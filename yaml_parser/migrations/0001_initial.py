# Generated by Django 4.2.7 on 2025-06-26 22:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Repository",
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
                ("workspace", models.CharField(max_length=100)),
                ("repository", models.CharField(max_length=100)),
                ("access_token", models.CharField(max_length=500)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Repositories",
            },
        ),
        migrations.CreateModel(
            name="YAMLFile",
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
                ("file_path", models.CharField(max_length=255)),
                ("content", models.TextField()),
                ("parsed_data", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "repository",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="yaml_files",
                        to="yaml_parser.repository",
                    ),
                ),
            ],
        ),
    ]
