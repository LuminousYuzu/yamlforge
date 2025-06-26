from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404
from .models import Repository, YAMLFile
from .serializers import RepositorySerializer, YAMLFileSerializer, RepositoryCreateSerializer
from .bitbucket_reader import BitbucketYAMLReader
import json

# Create your views here.

class RepositoryListCreateView(ListCreateAPIView):
    """API view for listing and creating repositories"""
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RepositoryCreateSerializer
        return RepositorySerializer

class RepositoryDetailView(RetrieveAPIView):
    """API view for retrieving repository details"""
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

class YAMLFileListView(ListCreateAPIView):
    """API view for listing YAML files"""
    queryset = YAMLFile.objects.all()
    serializer_class = YAMLFileSerializer

@api_view(['POST'])
def parse_repository(request):
    """API endpoint to parse YAML files from a repository"""
    try:
        # Get repository data from request
        workspace = request.data.get('workspace')
        repository = request.data.get('repository')
        access_token = request.data.get('access_token')

        if not all([workspace, repository, access_token]):
            return Response({
                'error': 'Missing required fields: workspace, repository, access_token'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create or get repository
        repo_obj, created = Repository.objects.get_or_create(
            workspace=workspace,
            repository=repository,
            defaults={'access_token': access_token}
        )
        
        if not created:
            repo_obj.access_token = access_token
            repo_obj.save()

        # Initialize Bitbucket reader
        reader = BitbucketYAMLReader(access_token, workspace, repository)
        
        # Get YAML files
        yaml_files = reader.list_yaml_files()
        
        if not yaml_files:
            return Response({
                'message': 'No YAML files found in the repository',
                'repository_id': repo_obj.id
            }, status=status.HTTP_200_OK)

        parsed_files = []
        
        # Parse each YAML file
        for file_path in yaml_files:
            content = reader.get_file_content(file_path)
            if content:
                parsed_data = reader.parse_yaml_content(content)
                
                # Create or update YAML file record
                yaml_file, created = YAMLFile.objects.get_or_create(
                    repository=repo_obj,
                    file_path=file_path,
                    defaults={
                        'content': content,
                        'parsed_data': parsed_data
                    }
                )
                
                if not created:
                    yaml_file.content = content
                    yaml_file.parsed_data = parsed_data
                    yaml_file.save()

                parsed_files.append({
                    'file_path': file_path,
                    'parsed_data': parsed_data
                })

        return Response({
            'message': f'Successfully parsed {len(parsed_files)} YAML files',
            'repository_id': repo_obj.id,
            'files': parsed_files
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Error parsing repository: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_repository_files(request, repository_id):
    """API endpoint to get all YAML files for a specific repository"""
    try:
        repository = get_object_or_404(Repository, id=repository_id)
        yaml_files = YAMLFile.objects.filter(repository=repository)
        serializer = YAMLFileSerializer(yaml_files, many=True)
        
        return Response({
            'repository': RepositorySerializer(repository).data,
            'files': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error retrieving files: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
