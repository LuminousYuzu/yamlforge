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
