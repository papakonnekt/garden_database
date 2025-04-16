"""
URL configuration for garden_db_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt # Added for GraphQL
from graphene_django.views import GraphQLView # Added for GraphQL
from rest_framework.authtoken import views as authtoken_views # Added for DRF token auth
from django.conf import settings
from django.conf.urls.static import static
from horticulture.web_views import (
    HomeView, AboutView, ApiDocsView, PlantListView, PlantDetailView,
    SeedListView, SeedDetailView, PestListView, PestDetailView,
    DiseaseListView, DiseaseDetailView, CompanionListView, SearchView,
    BulkImportView
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # API endpoints
    path('api/v1/', include('horticulture.urls')),
    path('api/v1/auth/token/', authtoken_views.obtain_auth_token), # Added DRF token auth endpoint
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))), # Added GraphQL endpoint

    # Web UI endpoints
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('api-docs/', ApiDocsView.as_view(), name='api_docs'),
    path('search/', SearchView.as_view(), name='search'),

    path('plants/', PlantListView.as_view(), name='plant_list'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant_detail'),

    path('seeds/', SeedListView.as_view(), name='seed_list'),
    path('seeds/<int:pk>/', SeedDetailView.as_view(), name='seed_detail'),

    path('pests/', PestListView.as_view(), name='pest_list'),
    path('pests/<int:pk>/', PestDetailView.as_view(), name='pest_detail'),

    path('diseases/', DiseaseListView.as_view(), name='disease_list'),
    path('diseases/<int:pk>/', DiseaseDetailView.as_view(), name='disease_detail'),

    path('companion-planting/', CompanionListView.as_view(), name='companion_list'),

    path('bulk-import/', BulkImportView.as_view(), name='bulk_import'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
