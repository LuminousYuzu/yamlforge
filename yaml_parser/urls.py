from django.urls import path
from . import views

urlpatterns = [
    path('repositories/', views.RepositoryListCreateView.as_view(), name='repository-list-create'),
    path('repositories/<int:pk>/', views.RepositoryDetailView.as_view(), name='repository-detail'),
    path('repositories/<int:pk>/delete/', views.RepositoryDeleteView.as_view(), name='repository-delete'),
    path('repositories/<int:repository_id>/files/', views.get_repository_files, name='repository-files'),
    path('parse-repository/', views.parse_repository, name='parse-repository'),
    path('yaml-files/', views.YAMLFileListView.as_view(), name='yaml-file-list'),
    path('service-catalog/', views.get_service_catalog, name='service-catalog'),
    path('extract-services/', views.extract_services_from_yaml, name='extract-services'),
] 