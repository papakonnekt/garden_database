from celery import shared_task
from django.db import transaction
from django.utils import timezone
import logging

import re # Added for parsing scientific name
from .models import (
    Plant, Seed, Fertilizer, Region, SoilProfile, Pest, Disease, Companionship,
    CompanionPlantingInteraction, PlantPest, PlantDisease
)
# Import serializers for simple import case
from .serializers import (
    PlantSerializer, SeedSerializer, FertilizerSerializer, RegionSerializer, SoilProfileSerializer,
    PestSerializer, DiseaseSerializer, CompanionshipSerializer, CompanionPlantingInteractionSerializer
)

logger = logging.getLogger(__name__)

def parse_scientific_name(name_str):
    """Parses scientific name potentially containing cultivar."""
    if not name_str:
        return name_str, None
    # Simple regex: look for single quotes or "var."/"cv."
    match = re.match(r"^(.*?)\s+(['\"].*?['\"]|var\.\s*\S+|cv\.\s*\S+)\s*$", name_str.strip())
    if match:
        base_name = match.group(1).strip()
        cultivar = match.group(2).strip().strip("'\"") # Remove quotes
        return base_name, cultivar
    return name_str.strip(), None

@shared_task
def process_bulk_import(entity_type, data_list, user_id=None):
    """
    Process bulk import of data in a background task.
    Handles simple lists or complex structures like beefsteak.json for 'plant' type.
    """
    logger.info(f"Starting bulk import task for entity type '{entity_type}' with {len(data_list)} top-level item(s)")

    # --- Handle Complex Plant Import (like beefsteak.json) ---
    # Check if data_list looks like the complex structure (has 'plants' key)
    is_complex_plant_import = (
        entity_type == 'plant' and
        isinstance(data_list, list) and len(data_list) == 1 and
        isinstance(data_list[0], dict) and
        'plants' in data_list[0] # Key indicator
    )

    if is_complex_plant_import:
        logger.info("Detected complex plant import structure (like beefsteak.json).")
        complex_data = data_list[0] # The single item in the list is the dict with 'plants', 'pests', etc.
        plants_data = complex_data.get('plants', [])
        companions_data = complex_data.get('companion_relationships', [])
        pests_data = complex_data.get('pests', [])
        diseases_data = complex_data.get('diseases', [])

        created_plants = {} # Store created plants by scientific name for linking
        created_pests = {} # Store created pests by scientific name
        created_diseases = {} # Store created diseases by scientific name
        created_interactions = {} # Store created interactions by code/description hash
        errors = []
        success_counts = {'plant': 0, 'pest': 0, 'disease': 0, 'companionship': 0, 'interaction': 0, 'plant_pest': 0, 'plant_disease': 0}

        try:
            with transaction.atomic():
                # 1. Process Plants
                logger.info(f"Processing {len(plants_data)} plants...")
                for plant_item in plants_data:
                    sci_name_raw = plant_item.get('scientific_name')
                    if not sci_name_raw:
                        errors.append({"type": "plant", "error": "Missing scientific_name", "data": plant_item})
                        continue

                    base_sci_name, cultivar = parse_scientific_name(sci_name_raw)

                    plant_defaults = {
                        'common_name': plant_item.get('common_name'),
                        'description': plant_item.get('description'),
                        'family': plant_item.get('family'),
                        'genus': plant_item.get('genus'),
                        'species': plant_item.get('species'),
                        'subspecies_cultivar': cultivar, # Parsed cultivar
                        'lifecycle_type': plant_item.get('lifecycle_type'),
                        'growth_habit': plant_item.get('growth_habit'),
                        'avg_height_inches': plant_item.get('avg_height_inches'),
                        'avg_spread_inches': plant_item.get('avg_spread_inches'),
                        'days_to_maturity_min': plant_item.get('days_to_maturity_min'),
                        'days_to_maturity_max': plant_item.get('days_to_maturity_max'),
                        'sunlight_requirements': plant_item.get('sunlight_requirements'),
                        'moisture_requirements': plant_item.get('moisture_requirements'),
                        'soil_ph_min': plant_item.get('soil_ph_min'),
                        'soil_ph_max': plant_item.get('soil_ph_max'),
                        'temperature_tolerance_min_f': plant_item.get('temperature_tolerance_min_f'),
                        'temperature_tolerance_max_f': plant_item.get('temperature_tolerance_max_f'),
                        'npk_preference': plant_item.get('npk_preference'),
                        'root_system_type': plant_item.get('root_system_type'),
                        'harvest_seasonality': plant_item.get('harvest_seasonality'),
                        'yield_estimates': plant_item.get('yield_estimates'),
                        'common_names_list': plant_item.get('common_names_list', []),
                        # Add other fields if needed, ensure they exist in model
                    }
                    # Remove None values to avoid overwriting existing data with None during update
                    plant_defaults = {k: v for k, v in plant_defaults.items() if v is not None}

                    try:
                        plant_obj, created = Plant.objects.update_or_create(
                            scientific_name=base_sci_name, # Use base name for lookup
                            defaults=plant_defaults
                        )
                        created_plants[sci_name_raw] = plant_obj # Store using original name from JSON for lookup
                        if created:
                            success_counts['plant'] += 1
                        logger.debug(f"Processed plant: {plant_obj.scientific_name} (Created: {created})")
                    except Exception as e:
                        logger.error(f"Error creating/updating plant '{sci_name_raw}': {e}")
                        errors.append({"type": "plant", "name": sci_name_raw, "error": str(e)})

                # 2. Process Pests (Create Pest records first)
                logger.info(f"Processing {len(pests_data)} pests...")
                for pest_item in pests_data:
                    sci_name = pest_item.get('scientific_name')
                    common_name = pest_item.get('common_name')
                    if not common_name: # Use common name as primary identifier if sci_name missing
                         errors.append({"type": "pest", "error": "Missing common_name", "data": pest_item})
                         continue

                    pest_defaults = {
                        'scientific_name': sci_name,
                        'description': pest_item.get('description'),
                        'category': pest_item.get('category'),
                        'symptoms': pest_item.get('symptoms'),
                        # Assuming control/prevention are JSON fields in model now
                        'treatment_strategies': pest_item.get('control_methods', []), # Map JSON key to model field
                        'prevention_strategies': [], # Add if present in JSON
                        # Add other fields
                    }
                    pest_defaults = {k: v for k, v in pest_defaults.items() if v is not None}

                    try:
                        pest_obj, created = Pest.objects.update_or_create(
                            common_name=common_name, # Use common name for lookup
                            defaults=pest_defaults
                        )
                        created_pests[sci_name or common_name] = pest_obj # Store by sci_name if available, else common
                        if created:
                            success_counts['pest'] += 1
                        logger.debug(f"Processed pest: {pest_obj.common_name} (Created: {created})")
                    except Exception as e:
                        logger.error(f"Error creating/updating pest '{common_name}': {e}")
                        errors.append({"type": "pest", "name": common_name, "error": str(e)})

                # 3. Process Diseases (Create Disease records)
                logger.info(f"Processing {len(diseases_data)} diseases...")
                for disease_item in diseases_data:
                    sci_name = disease_item.get('scientific_name')
                    common_name = disease_item.get('common_name')
                    if not common_name: # Use common name as primary identifier if sci_name missing
                         errors.append({"type": "disease", "error": "Missing common_name", "data": disease_item})
                         continue

                    disease_defaults = {
                        'scientific_name': sci_name,
                        'description': disease_item.get('description'),
                        'category': disease_item.get('category'),
                        'cause': disease_item.get('cause'),
                        'symptoms': disease_item.get('symptoms'),
                        # Assuming treatment/prevention are JSON fields in model
                        'treatment_strategies': disease_item.get('treatment_methods', []), # Map JSON key to model field
                        'prevention_strategies': disease_item.get('prevention_methods', []), # Add if present in JSON
                        # Add other fields
                    }
                    disease_defaults = {k: v for k, v in disease_defaults.items() if v is not None}

                    try:
                        disease_obj, created = Disease.objects.update_or_create(
                            common_name=common_name, # Use common name for lookup
                            defaults=disease_defaults
                        )
                        created_diseases[sci_name or common_name] = disease_obj # Store by sci_name if available, else common
                        if created:
                            success_counts['disease'] += 1
                        logger.debug(f"Processed disease: {disease_obj.common_name} (Created: {created})")
                    except Exception as e:
                        logger.error(f"Error creating/updating disease '{common_name}': {e}")
                        errors.append({"type": "disease", "name": common_name, "error": str(e)})

                # 4. Process Companion Relationships
                logger.info(f"Processing {len(companions_data)} companion relationships...")
                for comp_item in companions_data:
                    subject_name = comp_item.get('plant_subject')
                    object_name = comp_item.get('plant_object')
                    interactions_data = comp_item.get('interactions', [])
                    notes = comp_item.get('notes')

                    subject_plant = created_plants.get(subject_name)
                    object_plant = created_plants.get(object_name)

                    if not subject_plant or not object_plant:
                        errors.append({
                            "type": "companionship",
                            "error": f"Could not find plants for relationship: '{subject_name}' -> '{object_name}'",
                            "data": comp_item
                        })
                        continue

                    interaction_objs = []
                    for inter_item in interactions_data:
                        inter_type = inter_item.get('interaction_type')
                        inter_desc = inter_item.get('mechanism_description')
                        # Removed hash-based key generation

                        if inter_type and inter_desc:
                            try:
                                # Generate a simple code first
                                inter_code = f"{inter_type}_{inter_desc[:20]}".replace(" ", "_").upper()

                                # Check cache using the generated inter_code
                                if inter_code in created_interactions:
                                    interaction_objs.append(created_interactions[inter_code])
                                else:
                                    # Use interaction_code for lookup, others in defaults
                                    interaction_obj, created = CompanionPlantingInteraction.objects.get_or_create(
                                        interaction_code=inter_code,
                                        defaults={
                                            'interaction_type': inter_type,
                                            'mechanism_description': inter_desc
                                        }
                                    )
                                    # Add to cache using inter_code as key
                                    created_interactions[inter_code] = interaction_obj
                                interaction_objs.append(interaction_obj)
                                if created:
                                    success_counts['interaction'] += 1
                                logger.debug(f"Processed interaction: {interaction_obj.interaction_code} (Created: {created})")
                            except Exception as e:
                                logger.error(f"Error creating/getting interaction '{inter_type}': {e}")
                                errors.append({"type": "interaction", "data": inter_item, "error": str(e)})

                    if interaction_objs:
                        try:
                            comp_obj, created = Companionship.objects.get_or_create(
                                plant_subject=subject_plant,
                                plant_object=object_plant,
                                defaults={'notes': notes} # Add other defaults if needed
                            )
                            comp_obj.interactions.add(*interaction_objs) # Add interactions
                            if created:
                                success_counts['companionship'] += 1
                            logger.debug(f"Processed companionship: {subject_plant} -> {object_plant} (Created: {created})")
                        except Exception as e:
                            logger.error(f"Error creating/updating companionship '{subject_name}' -> '{object_name}': {e}")
                            errors.append({"type": "companionship", "subject": subject_name, "object": object_name, "error": str(e)})

                # 5. Link Pests to Plants (using affected_plants field in pest data)
                logger.info(f"Linking {len(pests_data)} pests to affected plants...")
                for pest_item in pests_data:
                    pest_name = pest_item.get('scientific_name') or pest_item.get('common_name')
                    pest_obj = created_pests.get(pest_name)
                    affected_plants_names = pest_item.get('affected_plants', [])

                    if not pest_obj:
                        # Error already logged during pest creation
                        continue

                    for plant_name in affected_plants_names:
                        plant_obj = created_plants.get(plant_name)
                        # Logging removed - issue is earlier
                        if plant_obj and pest_obj:
                            try:
                                _, created = PlantPest.objects.get_or_create(
                                    plant=plant_obj,
                                    pest=pest_obj
                                )
                                # Logging removed
                                if created:
                                     success_counts['plant_pest'] += 1
                                logger.debug(f"Linked pest '{pest_name}' to plant '{plant_name}' (Created: {created})") # Restore original debug log

                            except Exception as e:
                                # Logging removed
                                logger.error(f"Error linking pest '{pest_name}' to plant '{plant_name}': {e}")
                                errors.append({"type": "plant_pest_link", "pest": pest_name, "plant": plant_name, "error": str(e)})
                        else:
                             # Keep this error reporting for the case where plant_obj is None
                             errors.append({"type": "plant_pest_link", "pest": pest_name, "plant": plant_name, "error": "Affected plant not found in created plants list."})

                # 6. Link Diseases to Plants (using affected_plants field in disease data)
                logger.info("Linking diseases to plants...")
                for disease_item in diseases_data:
                    disease_name = disease_item.get('scientific_name') or disease_item.get('common_name')
                    affected_plants = disease_item.get('affected_plants', [])

                    disease_obj = created_diseases.get(disease_name)
                    if not disease_obj:
                        errors.append({"type": "plant_disease_link", "disease": disease_name, "error": "Disease not found in created diseases list."})
                        continue

                    for plant_name in affected_plants:
                        plant_obj = created_plants.get(plant_name)
                        if plant_obj:
                            try:
                                # Create the many-to-many relationship
                                PlantDisease.objects.get_or_create(plant=plant_obj, disease=disease_obj)
                                success_counts['plant_disease'] += 1
                            except Exception as e:
                                logger.error(f"Error linking disease '{disease_name}' to plant '{plant_name}': {e}")
                                errors.append({"type": "plant_disease_link", "disease": disease_name, "plant": plant_name, "error": str(e)})
                        else:
                             errors.append({"type": "plant_disease_link", "disease": disease_name, "plant": plant_name, "error": "Affected plant not found in created plants list."})


                # If any errors occurred during the complex import, raise exception to rollback
                if errors:
                    raise Exception("Errors occurred during complex bulk import processing.")

            # If transaction completes without raising exception
            msg = f"Successfully processed complex import: {success_counts['plant']} plants, {success_counts['pest']} pests, {success_counts['disease']} diseases, {success_counts['companionship']} companionships, {success_counts['interaction']} interactions, {success_counts['plant_pest']} pest links, {success_counts['plant_disease']} disease links."
            logger.info(msg)
            return {
                "success": True,
                "message": msg,
                "details": success_counts, # Provide counts instead of individual results for complex import
                "timestamp": timezone.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Complex bulk import failed: {str(e)}")
            return {
                "success": False,
                "message": "Complex bulk import failed. Transaction rolled back.",
                "errors": errors,
                "exception": str(e),
                "timestamp": timezone.now().isoformat()
            }

    # --- Handle Simple List Import (Original Logic - slightly adapted) ---
    else:
        logger.info(f"Processing simple list import for {entity_type}.")
        # Map entity types to their serializers (needed for simple import)
        serializer_map = {
            'plant': PlantSerializer, # Keep serializers needed for simple case
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
             return {"success": False, "message": f"Unknown entity type for simple import: {entity_type}"}

        serializer_class = serializer_map[entity_type]
        success_count = 0
        errors = []
        results = []

        try:
            with transaction.atomic():
                for index, item_data in enumerate(data_list):
                    # Special handling for plant scientific name parsing even in simple import
                    if entity_type == 'plant' and 'scientific_name' in item_data:
                        base_sci_name, cultivar = parse_scientific_name(item_data['scientific_name'])
                        item_data['scientific_name'] = base_sci_name # Modify data for serializer
                        if cultivar:
                             item_data['subspecies_cultivar'] = cultivar # Add cultivar if found

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
                            logger.error(f"Error saving simple {entity_type} record at index {index}: {str(e)}")
                            errors.append({"index": index, "error": f"Error saving record: {str(e)}", "data": item_data})
                    else:
                        logger.error(f"Validation error for simple {entity_type} record at index {index}: {serializer.errors}")
                        errors.append({"index": index, "error": serializer.errors, "data": item_data})

                # If any errors occurred, roll back the transaction
                if errors:
                    raise Exception("Validation or save errors occurred during simple bulk import")

            # If transaction completes without raising exception
            logger.info(f"Successfully imported {success_count} simple {entity_type} records")
            return {
                "success": True,
                "message": f"Successfully imported {success_count} simple {entity_type} records",
                "details": results,
                "timestamp": timezone.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Simple bulk import failed: {str(e)}")
            return {
                "success": False,
                "message": "Simple bulk import failed. Transaction rolled back.",
                "errors": errors,
                "exception": str(e),
                "timestamp": timezone.now().isoformat()
            }
