from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action # Added
from rest_framework.response import Response # Added
from rest_framework.permissions import IsAdminUser # Added
from rest_framework.views import APIView # Added import
from django.utils import timezone # Added
from django.db import transaction # New import
from rest_framework import status # New import

from .models import (
    Region, SoilProfile, Plant, Fertilizer, Pest, Disease, Seed,
    Companionship, PlantPest, PlantDisease, UserContribution,
    CompanionPlantingInteraction
)
from .serializers import (
    RegionSerializer, SoilProfileSerializer, PlantSerializer, UserSerializer,
    FertilizerSerializer, PestSerializer, DiseaseSerializer, SeedSerializer,
    CompanionshipSerializer, PlantPestSerializer, PlantDiseaseSerializer,
    UserContributionSerializer, CompanionPlantingInteractionSerializer
)
from .permissions import IsAuthenticatedCreateOrAdminReadUpdateDelete # Import the new class

# Create your views here.

class RegionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows regions to be viewed or edited.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    # Add permission_classes later if needed

class SoilProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows soil profiles to be viewed or edited.
    """
    queryset = SoilProfile.objects.all()
    serializer_class = SoilProfileSerializer
    # Add permission_classes later if needed

class PlantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows plants to be viewed or edited.
    """
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    # Add permission_classes later if needed

# --- Added ViewSets ---

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Add permission_classes later if needed

class FertilizerViewSet(viewsets.ModelViewSet):
    queryset = Fertilizer.objects.all()
    serializer_class = FertilizerSerializer
    # Add permission_classes later if needed

class PestViewSet(viewsets.ModelViewSet):
    queryset = Pest.objects.all()
    serializer_class = PestSerializer
    # Add permission_classes later if needed

class DiseaseViewSet(viewsets.ModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    # Add permission_classes later if needed

class SeedViewSet(viewsets.ModelViewSet):
    queryset = Seed.objects.all()
    serializer_class = SeedSerializer
    # Add permission_classes later if needed

class CompanionshipViewSet(viewsets.ModelViewSet):
    queryset = Companionship.objects.all()
    serializer_class = CompanionshipSerializer
    # Add permission_classes later if needed

class PlantPestViewSet(viewsets.ModelViewSet):
    queryset = PlantPest.objects.all()
    serializer_class = PlantPestSerializer
    # Add permission_classes later if needed

class PlantDiseaseViewSet(viewsets.ModelViewSet):
    queryset = PlantDisease.objects.all()
    serializer_class = PlantDiseaseSerializer
    # Add permission_classes later if needed

class UserContributionViewSet(viewsets.ModelViewSet):
    queryset = UserContribution.objects.all()
    serializer_class = UserContributionSerializer
    permission_classes = [IsAuthenticatedCreateOrAdminReadUpdateDelete] # Apply specific permission

    @action(detail=True, methods=['put'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        contribution = self.get_object()
        contribution.status = 'approved'
        contribution.reviewed_at = timezone.now()
        contribution.reviewed_by = request.user
        contribution.save()
        return Response({'status': 'contribution approved'})

    @action(detail=True, methods=['put'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        contribution = self.get_object()
        contribution.status = 'rejected'
        contribution.reviewed_at = timezone.now()
        contribution.reviewed_by = request.user
        # Optionally update admin_notes
        admin_notes = request.data.get('admin_notes')
        if admin_notes:
            contribution.admin_notes = admin_notes
        contribution.save()
        return Response({'status': 'contribution rejected'})

class CompanionPlantingInteractionViewSet(viewsets.ModelViewSet):
    queryset = CompanionPlantingInteraction.objects.all()
    serializer_class = CompanionPlantingInteractionSerializer
    # Add permission_classes later if needed

# --- Added Bulk Import View ---

from .tasks import process_bulk_import

class BulkImportView(APIView):
    """
    View to handle bulk import of data via JSON upload.
    Restricted to admin users.
    Handles imports for all entity types using Celery for large imports.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        if not isinstance(request.data, dict) or 'entity_type' not in request.data or 'data' not in request.data:
            return Response({
                "error": "Expected a JSON object with 'entity_type' and 'data' fields.",
                "example": {
                    "entity_type": "plant",
                    "data": [{"field1": "value1", "field2": "value2"}]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        entity_type = request.data['entity_type'].lower()
        data_list = request.data['data']

        if not isinstance(data_list, list):
            return Response({"error": "The 'data' field must be a list of objects."}, status=status.HTTP_400_BAD_REQUEST)

        # List of supported entity types
        supported_types = [
            'plant', 'seed', 'fertilizer', 'region', 'soilprofile',
            'pest', 'disease', 'companionship', 'companioninteraction'
        ]

        if entity_type not in supported_types:
            return Response({
                "error": f"Unknown entity type: {entity_type}",
                "supported_types": supported_types
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if this is a large import that should use Celery
        use_celery = len(data_list) > 10  # Use Celery for imports with more than 10 items

        if use_celery:
            # Process in background with Celery
            user_id = str(request.user.id) if request.user.is_authenticated else None
            task = process_bulk_import.delay(entity_type, data_list, user_id)

            return Response({
                "message": f"Bulk import of {len(data_list)} {entity_type} records started.",
                "task_id": task.id,
                "status": "processing"
            }, status=status.HTTP_202_ACCEPTED)
        else:
            # For small imports, process synchronously
            from .tasks import process_bulk_import as sync_import
            result = sync_import(entity_type, data_list)

            if result['success']:
                return Response({
                    "message": result['message'],
                    "details": result['details']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "message": result['message'],
                    "errors": result.get('errors', []),
                    "exception": result.get('exception', '')
                }, status=status.HTTP_400_BAD_REQUEST)
