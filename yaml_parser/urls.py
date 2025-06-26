from django.urls import path
from . import views

urlpatterns = [
    path('api/repositories/', views.RepositoryListCreateView.as_view(), name='repository-list-create'),
    path('api/repositories/<int:pk>/', views.RepositoryDetailView.as_view(), name='repository-detail'),
    path('api/yaml-files/', views.YAMLFileListView.as_view(), name='yaml-file-list'),
    path('api/parse-repository/', views.parse_repository, name='parse-repository'),
    path('api/repositories/<int:repository_id>/files/', views.get_repository_files, name='get-repository-files'),
] 