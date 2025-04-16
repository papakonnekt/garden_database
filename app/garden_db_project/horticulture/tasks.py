from celery import shared_task
from django.db import transaction
from django.utils import timezone
import logging

from .models import Plant, Seed, Fertilizer, Region, SoilProfile, Pest, Disease, Companionship, CompanionPlantingInteraction
from .serializers import (
    PlantSerializer, SeedSerializer, FertilizerSerializer, RegionSerializer, SoilProfileSerializer,
    PestSerializer, DiseaseSerializer, CompanionshipSerializer, CompanionPlantingInteractionSerializer
)

logger = logging.getLogger(__name__)

@shared_task
def process_bulk_import(entity_type, data_list, user_id=None):
    """
    Process bulk import of data in a background task.
    
    Args:
        entity_type (str): The type of entity to import (plant, seed, etc.)
        data_list (list): List of dictionaries containing the data to import
        user_id (str, optional): ID of the user who initiated the import
        
    Returns:
        dict: Results of the import operation
    """
    logger.info(f"Starting bulk import of {len(data_list)} {entity_type} records")
    
    # Map entity types to their serializers
    serializer_map = {
        'plant': PlantSerializer,
        'seed': SeedSerializer,
        'fertilizer': FertilizerSerializer,
        'region': RegionSerializer,
        'soilprofile': SoilProfileSerializer,
        'pest': PestSerializer,
        'disease': DiseaseSerializer,
        'companionship': CompanionshipSerializer,
        'companioninteraction': CompanionPlantingInteractionSerializer,
    }
    
    if entity_type not in serializer_map:
        return {
            "success": False,
            "message": f"Unknown entity type: {entity_type}",
            "timestamp": timezone.now().isoformat()
        }
    
    serializer_class = serializer_map[entity_type]
    success_count = 0
    errors = []
    results = []
    
    try:
        with transaction.atomic():
            for index, item_data in enumerate(data_list):
                serializer = serializer_class(data=item_data)
                if serializer.is_valid():
                    try:
                        instance = serializer.save()
                        success_count += 1
                        results.append({
                            "index": index,
                            "id": instance.pk,
                            "status": "success"
                        })
                    except Exception as e:
                        logger.error(f"Error saving {entity_type} record at index {index}: {str(e)}")
                        errors.append({
                            "index": index,
                            "error": f"Error saving record: {str(e)}"
                        })
                else:
                    logger.error(f"Validation error for {entity_type} record at index {index}: {serializer.errors}")
                    errors.append({
                        "index": index,
                        "error": serializer.errors
                    })
            
            # If any errors occurred, roll back the transaction
            if errors:
                raise Exception("Validation or save errors occurred during bulk import")
        
        # If transaction completes without raising exception
        logger.info(f"Successfully imported {success_count} {entity_type} records")
        return {
            "success": True,
            "message": f"Successfully imported {success_count} {entity_type} records",
            "details": results,
            "timestamp": timezone.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Bulk import failed: {str(e)}")
        return {
            "success": False,
            "message": "Bulk import failed. Transaction rolled back.",
            "errors": errors,
            "exception": str(e),
            "timestamp": timezone.now().isoformat()
        }
