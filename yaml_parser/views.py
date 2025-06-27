from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, DestroyAPIView
from django.shortcuts import get_object_or_404
from .models import Repository, YAMLFile, Service
from .serializers import RepositorySerializer, YAMLFileSerializer, RepositoryCreateSerializer, ServiceSerializer
from .bitbucket_reader import BitbucketYAMLReader
from .service_extractor import SpringBootServiceExtractor
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

class RepositoryDeleteView(DestroyAPIView):
    """API view for deleting repositories"""
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    def destroy(self, request, *args, **kwargs):
        repository = self.get_object()
        
        # Delete all related services first
        services_deleted = 0
        for yaml_file in repository.yaml_files.all():
            services_deleted += yaml_file.services.count()
            yaml_file.services.all().delete()
        
        # Delete all YAML files
        yaml_files_deleted = repository.yaml_files.count()
        repository.yaml_files.all().delete()
        
        # Delete the repository
        repository_name = f"{repository.workspace}/{repository.repository}"
        repository.delete()
        
        return Response({
            'message': f'Successfully deleted repository {repository_name}',
            'deleted_items': {
                'repository': 1,
                'yaml_files': yaml_files_deleted,
                'services': services_deleted
            }
        }, status=status.HTTP_200_OK)

class YAMLFileListView(ListCreateAPIView):
    """API view for listing YAML files"""
    queryset = YAMLFile.objects.all()
    serializer_class = YAMLFileSerializer

class ServiceListView(ListCreateAPIView):
    """API view for listing services"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

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
        extracted_services = []
        
        # Initialize service extractor
        service_extractor = SpringBootServiceExtractor()
        
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

                # Extract services from the YAML data
                if parsed_data:
                    service_info = service_extractor.extract_service_info(parsed_data)
                    
                    # Create service record if service name is found
                    if service_info.get('service_name') and service_info['service_name'].get('value'):
                        service_name = service_info['service_name']['value']
                        
                        # Create or update service
                        service, service_created = Service.objects.get_or_create(
                            yaml_file=yaml_file,
                            service_name=service_name,
                            defaults={
                                'dependent_services': service_info.get('dependent_services', []),
                                'dependent_infrastructure': service_info.get('dependent_infrastructure', []),
                                'port': service_info.get('port', {}).get('value') if service_info.get('port') else None,
                                'protocol': service_info.get('protocol', {}).get('value') if service_info.get('protocol') else None,
                                'additional_data': service_info.get('additional_data', {})
                            }
                        )
                        
                        if not service_created:
                            # Update existing service
                            service.dependent_services = service_info.get('dependent_services', [])
                            service.dependent_infrastructure = service_info.get('dependent_infrastructure', [])
                            service.port = service_info.get('port', {}).get('value') if service_info.get('port') else None
                            service.protocol = service_info.get('protocol', {}).get('value') if service_info.get('protocol') else None
                            service.additional_data = service_info.get('additional_data', {})
                            service.save()
                        
                        extracted_services.append({
                            'service_name': service_name,
                            'port': service.port,
                            'protocol': service.protocol,
                            'dependent_services': service.dependent_services,
                            'dependent_infrastructure': service.dependent_infrastructure,
                            'extraction_confidence': service_info['service_name'].get('confidence', 0)
                        })

                parsed_files.append({
                    'file_path': file_path,
                    'parsed_data': parsed_data,
                    'services_extracted': len(extracted_services) if file_path == yaml_files[-1] else 0
                })

        return Response({
            'message': f'Successfully parsed {len(parsed_files)} YAML files and extracted {len(extracted_services)} services',
            'repository_id': repo_obj.id,
            'files': parsed_files,
            'services': extracted_services
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

@api_view(['GET'])
def get_service_catalog(request):
    """API endpoint to get all services for the service catalog"""
    try:
        services = Service.objects.all().select_related('yaml_file__repository')
        serializer = ServiceSerializer(services, many=True)
        
        return Response({
            'services': serializer.data,
            'total_count': len(services)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error retrieving services: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def extract_services_from_yaml(request):
    """API endpoint to extract services from existing YAML files"""
    try:
        yaml_file_id = request.data.get('yaml_file_id')
        
        if not yaml_file_id:
            return Response({
                'error': 'Missing yaml_file_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        yaml_file = get_object_or_404(YAMLFile, id=yaml_file_id)
        
        if not yaml_file.parsed_data:
            return Response({
                'error': 'YAML file has no parsed data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize service extractor
        service_extractor = SpringBootServiceExtractor()
        
        # Extract services
        service_info = service_extractor.extract_service_info(yaml_file.parsed_data)
        
        # Create service record if service name is found
        if service_info.get('service_name') and service_info['service_name'].get('value'):
            service_name = service_info['service_name']['value']
            
            service, created = Service.objects.get_or_create(
                yaml_file=yaml_file,
                service_name=service_name,
                defaults={
                    'dependent_services': service_info.get('dependent_services', []),
                    'dependent_infrastructure': service_info.get('dependent_infrastructure', []),
                    'port': service_info.get('port', {}).get('value') if service_info.get('port') else None,
                    'protocol': service_info.get('protocol', {}).get('value') if service_info.get('protocol') else None,
                    'additional_data': service_info.get('additional_data', {})
                }
            )
            
            if not created:
                # Update existing service
                service.dependent_services = service_info.get('dependent_services', [])
                service.dependent_infrastructure = service_info.get('dependent_infrastructure', [])
                service.port = service_info.get('port', {}).get('value') if service_info.get('port') else None
                service.protocol = service_info.get('protocol', {}).get('value') if service_info.get('protocol') else None
                service.additional_data = service_info.get('additional_data', {})
                service.save()
            
            serializer = ServiceSerializer(service)
            
            return Response({
                'message': f'Successfully extracted service: {service_name}',
                'service': serializer.data,
                'extraction_info': service_info
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'No service name found in YAML file',
                'extraction_info': service_info
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'error': f'Error extracting services: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
