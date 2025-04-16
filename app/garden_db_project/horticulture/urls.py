from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import BulkImportView
from .task_views import TaskStatusView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'regions', views.RegionViewSet, basename='region')
router.register(r'soil-profiles', views.SoilProfileViewSet, basename='soilprofile') # Use hyphenated URL
router.register(r'fertilizers', views.FertilizerViewSet, basename='fertilizer')
router.register(r'pests', views.PestViewSet, basename='pest')
router.register(r'diseases', views.DiseaseViewSet, basename='disease')
router.register(r'plants', views.PlantViewSet, basename='plant')
router.register(r'seeds', views.SeedViewSet, basename='seed')
router.register(r'companionships', views.CompanionshipViewSet, basename='companionship')
router.register(r'plant-pests', views.PlantPestViewSet, basename='plantpest')
router.register(r'plant-diseases', views.PlantDiseaseViewSet, basename='plantdisease')
router.register(r'user-contributions', views.UserContributionViewSet, basename='usercontribution')
router.register(r'companion-interactions', views.CompanionPlantingInteractionViewSet, basename='companioninteraction')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('bulk-import/', BulkImportView.as_view(), name='bulk-import'),
    path('tasks/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    path('', include(router.urls)), # Keep router include last
]