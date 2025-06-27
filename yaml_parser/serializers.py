from rest_framework import serializers
from .models import Repository, YAMLFile, Service

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

class ServiceSerializer(serializers.ModelSerializer):
    yaml_file_info = YAMLFileSerializer(source='yaml_file', read_only=True)
    repository_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'yaml_file', 'yaml_file_info', 'repository_info', 'service_name', 'dependent_services', 
                 'dependent_infrastructure', 'port', 'protocol', 'additional_data', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_repository_info(self, obj):
        if obj.yaml_file and obj.yaml_file.repository:
            return {
                'id': obj.yaml_file.repository.id,
                'workspace': obj.yaml_file.repository.workspace,
                'repository': obj.yaml_file.repository.repository
            }
        return None 