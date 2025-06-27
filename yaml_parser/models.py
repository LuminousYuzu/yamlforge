from django.db import models
from django.utils import timezone

class Repository(models.Model):
    """Model to store repository information"""
    workspace = models.CharField(max_length=100)
    repository = models.CharField(max_length=100)
    access_token = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Repositories"

    def __str__(self):
        return f"{self.workspace}/{self.repository}"

class YAMLFile(models.Model):
    """Model to store YAML file information"""
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='yaml_files')
    file_path = models.CharField(max_length=255)
    content = models.TextField()
    parsed_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.repository} - {self.file_path}"

class Service(models.Model):
    """Model to store extracted service information from YAML files"""
    yaml_file = models.ForeignKey(YAMLFile, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=255)
    dependent_services = models.JSONField(null=True, blank=True, help_text="List of dependent services")
    dependent_infrastructure = models.JSONField(null=True, blank=True, help_text="List of dependent infrastructure")
    port = models.CharField(max_length=10, null=True, blank=True)
    protocol = models.CharField(max_length=20, null=True, blank=True)
    additional_data = models.JSONField(null=True, blank=True, help_text="Additional service data")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Services"
        ordering = ['service_name']

    def __str__(self):
        return f"{self.service_name} - {self.yaml_file.file_path}"
