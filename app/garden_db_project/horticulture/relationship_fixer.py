"""
Relationship Fixer for Garden Database

This module provides functions to fix relationships between plants, pests, and diseases.
"""

import logging
import json
from django.db import transaction
from django.db.models import Q

from .models import (
    Plant, Pest, Disease, PlantPest, PlantDisease
)

logger = logging.getLogger(__name__)

def fix_plant_pest_relationships():
    """
    Fix relationships between plants and pests.
    This function will scan all pests and ensure they are properly linked to plants.
    """
    logger.info("Starting to fix plant-pest relationships")

    # Get all pests
    pests = Pest.objects.all()
    logger.info(f"Found {pests.count()} pests in the database")

    fixed_count = 0
    error_count = 0

    for pest in pests:
        try:
            # Get all plants linked to this pest
            linked_plants = pest.plants.all()
            logger.info(f"Pest '{pest.common_name}' is linked to {linked_plants.count()} plants")

            # If the pest has no linked plants, try to find plants by scientific name
            if linked_plants.count() == 0:
                logger.info(f"Attempting to find plants for pest '{pest.common_name}'")

                # Try to find plants by common name or scientific name
                potential_plants = Plant.objects.filter(
                    Q(common_name__icontains=pest.common_name) |
                    Q(scientific_name__icontains=pest.common_name)
                )

                if potential_plants.exists():
                    logger.info(f"Found {potential_plants.count()} potential plants for pest '{pest.common_name}'")

                    # Link the pest to these plants
                    for plant in potential_plants:
                        PlantPest.objects.get_or_create(plant=plant, pest=pest)
                        logger.info(f"Linked pest '{pest.common_name}' to plant '{plant.scientific_name}'")
                        fixed_count += 1
                else:
                    logger.warning(f"No potential plants found for pest '{pest.common_name}'")
        except Exception as e:
            logger.error(f"Error fixing relationships for pest '{pest.common_name}': {e}")
            error_count += 1

    logger.info(f"Fixed {fixed_count} plant-pest relationships with {error_count} errors")
    return fixed_count, error_count

def fix_plant_disease_relationships():
    """
    Fix relationships between plants and diseases.
    This function will scan all diseases and ensure they are properly linked to plants.
    """
    logger.info("Starting to fix plant-disease relationships")

    # Get all diseases
    diseases = Disease.objects.all()
    logger.info(f"Found {diseases.count()} diseases in the database")

    fixed_count = 0
    error_count = 0

    for disease in diseases:
        try:
            # Get all plants linked to this disease
            linked_plants = disease.plants.all()
            logger.info(f"Disease '{disease.common_name}' is linked to {linked_plants.count()} plants")

            # If the disease has no linked plants, try to find plants by scientific name
            if linked_plants.count() == 0:
                logger.info(f"Attempting to find plants for disease '{disease.common_name}'")

                # Try to find plants by common name or scientific name
                potential_plants = Plant.objects.filter(
                    Q(common_name__icontains=disease.common_name) |
                    Q(scientific_name__icontains=disease.common_name)
                )

                if potential_plants.exists():
                    logger.info(f"Found {potential_plants.count()} potential plants for disease '{disease.common_name}'")

                    # Link the disease to these plants
                    for plant in potential_plants:
                        PlantDisease.objects.get_or_create(plant=plant, disease=disease)
                        logger.info(f"Linked disease '{disease.common_name}' to plant '{plant.scientific_name}'")
                        fixed_count += 1
                else:
                    logger.warning(f"No potential plants found for disease '{disease.common_name}'")
        except Exception as e:
            logger.error(f"Error fixing relationships for disease '{disease.common_name}': {e}")
            error_count += 1

    logger.info(f"Fixed {fixed_count} plant-disease relationships with {error_count} errors")
    return fixed_count, error_count

def fix_relationships_from_json(json_file_path=None, json_data=None):
    """
    Fix relationships between plants, pests, and diseases based on a JSON file or data.

    Args:
        json_file_path: Path to the JSON file (optional)
        json_data: JSON data as a dictionary (optional)

    Note: Either json_file_path or json_data must be provided.
    """
    if json_file_path:
        logger.info(f"Starting to fix relationships from JSON file: {json_file_path}")

        try:
            # Read the JSON file
            with open(json_file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
            return 0, 0
    elif json_data:
        logger.info("Starting to fix relationships from provided JSON data")
        data = json_data
    else:
        logger.error("No JSON file path or data provided")
        return 0, 0

    try:

        # Process plants
        plants_data = data.get('plants', [])
        logger.info(f"Found {len(plants_data)} plants in the JSON file")

        # Create a mapping of scientific names to plant objects
        plant_map = {}
        for plant_data in plants_data:
            scientific_name = plant_data.get('scientific_name')
            if scientific_name:
                # Try to find the plant in the database
                plant = Plant.objects.filter(scientific_name=scientific_name).first()
                if plant:
                    plant_map[scientific_name] = plant
                    logger.info(f"Found plant '{scientific_name}' in the database")
                else:
                    logger.warning(f"Plant '{scientific_name}' not found in the database")

        # Process pests
        pests_data = data.get('pests', [])
        logger.info(f"Found {len(pests_data)} pests in the JSON file")

        pest_fixed_count = 0
        for pest_data in pests_data:
            common_name = pest_data.get('common_name')
            affected_plants = pest_data.get('affected_plants', [])

            if common_name and affected_plants:
                # Try to find the pest in the database
                pest = Pest.objects.filter(common_name=common_name).first()
                if pest:
                    logger.info(f"Found pest '{common_name}' in the database")

                    # Link the pest to the affected plants
                    for plant_name in affected_plants:
                        plant = plant_map.get(plant_name)
                        if plant:
                            PlantPest.objects.get_or_create(plant=plant, pest=pest)
                            logger.info(f"Linked pest '{common_name}' to plant '{plant_name}'")
                            pest_fixed_count += 1
                        else:
                            # Try to find the plant by scientific name
                            plant = Plant.objects.filter(scientific_name=plant_name).first()
                            if plant:
                                PlantPest.objects.get_or_create(plant=plant, pest=pest)
                                logger.info(f"Linked pest '{common_name}' to plant '{plant_name}'")
                                pest_fixed_count += 1
                            else:
                                logger.warning(f"Plant '{plant_name}' not found for pest '{common_name}'")
                else:
                    logger.warning(f"Pest '{common_name}' not found in the database")

        # Process diseases
        diseases_data = data.get('diseases', [])
        logger.info(f"Found {len(diseases_data)} diseases in the JSON file")

        disease_fixed_count = 0
        for disease_data in diseases_data:
            common_name = disease_data.get('common_name')
            affected_plants = disease_data.get('affected_plants', [])

            if common_name and affected_plants:
                # Try to find the disease in the database
                disease = Disease.objects.filter(common_name=common_name).first()
                if disease:
                    logger.info(f"Found disease '{common_name}' in the database")

                    # Link the disease to the affected plants
                    for plant_name in affected_plants:
                        plant = plant_map.get(plant_name)
                        if plant:
                            PlantDisease.objects.get_or_create(plant=plant, disease=disease)
                            logger.info(f"Linked disease '{common_name}' to plant '{plant_name}'")
                            disease_fixed_count += 1
                        else:
                            # Try to find the plant by scientific name
                            plant = Plant.objects.filter(scientific_name=plant_name).first()
                            if plant:
                                PlantDisease.objects.get_or_create(plant=plant, disease=disease)
                                logger.info(f"Linked disease '{common_name}' to plant '{plant_name}'")
                                disease_fixed_count += 1
                            else:
                                logger.warning(f"Plant '{plant_name}' not found for disease '{common_name}'")
                else:
                    logger.warning(f"Disease '{common_name}' not found in the database")

        logger.info(f"Fixed {pest_fixed_count} plant-pest relationships and {disease_fixed_count} plant-disease relationships from JSON file")
        return pest_fixed_count, disease_fixed_count

    except Exception as e:
        logger.error(f"Error fixing relationships from JSON: {e}")
        return 0, 0

def fix_all_relationships():
    """
    Fix all relationships between plants, pests, and diseases.
    """
    with transaction.atomic():
        pest_count, pest_errors = fix_plant_pest_relationships()
        disease_count, disease_errors = fix_plant_disease_relationships()

    return {
        'pest_fixed_count': pest_count,
        'pest_error_count': pest_errors,
        'disease_fixed_count': disease_count,
        'disease_error_count': disease_errors
    }
