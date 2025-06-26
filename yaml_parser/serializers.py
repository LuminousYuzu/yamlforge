from rest_framework import serializers
from .models import Repository, YAMLFile

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['id', 'workspace', 'repository', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class YAMLFileSerializer(serializers.ModelSerializer):
    repository_info = RepositorySerializer(source='repository', read_only=True)
    
    class Meta:
        model = YAMLFile
        fields = ['id', 'repository', 'repository_info', 'file_path', 'content', 'parsed_data', 'created_at']
        read_only_fields = ['id', 'content', 'parsed_data', 'created_at']

class RepositoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['workspace', 'repository', 'access_token'] 