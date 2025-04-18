"""
Bulk Import Handler for Garden Database

This module provides a clean implementation for importing various entity types
from JSON data, with proper handling of relationships and error reporting.
"""

import logging
import json
from django.db import transaction
from django.utils import timezone

from .models import (
    Plant, Seed, Fertilizer, Region, SoilProfile, Pest, Disease, Companionship,
    CompanionPlantingInteraction, PlantPest, PlantDisease
)

logger = logging.getLogger(__name__)

class BulkImportHandler:
    """
    Handles bulk import of various entity types from JSON data.
    Provides methods for importing different entity types and managing relationships.
    """
    
    def __init__(self, update_existing=False):
        """
        Initialize the handler.
        
        Args:
            update_existing (bool): Whether to update existing records or skip them
        """
        self.update_existing = update_existing
        self.result = {
            'success': False,
            'message': '',
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'total': 0,
            'errors': []
        }
        # Store created entities for relationship linking
        self.created_plants = {}  # scientific_name -> Plant object
        self.created_pests = {}   # common_name -> Pest object
        self.created_diseases = {} # common_name -> Disease object
        self.created_interactions = {} # code -> Interaction object
    
    def process_json_file(self, json_file, entity_type):
        """
        Process a JSON file for the given entity type.
        
        Args:
            json_file: The uploaded JSON file
            entity_type (str): The type of entity to import
            
        Returns:
            dict: Result of the import operation
        """
        try:
            # Read and parse JSON file
            data = json.loads(json_file.read().decode('utf-8'))
            logger.info(f"Parsed JSON data type: {type(data).__name__}")
            
            # Process the data based on entity type
            with transaction.atomic():
                if entity_type == 'comprehensive':
                    self._process_comprehensive_import(data)
                elif entity_type == 'plant':
                    self._process_simple_import(data, self._import_plant)
                elif entity_type == 'pest':
                    self._process_simple_import(data, self._import_pest)
                elif entity_type == 'disease':
                    self._process_simple_import(data, self._import_disease)
                elif entity_type == 'seed':
                    self._process_simple_import(data, self._import_seed)
                elif entity_type == 'fertilizer':
                    self._process_simple_import(data, self._import_fertilizer)
                elif entity_type == 'region':
                    self._process_simple_import(data, self._import_region)
                elif entity_type == 'soil_profile':
                    self._process_simple_import(data, self._import_soil_profile)
                elif entity_type == 'companionship':
                    self._process_simple_import(data, self._import_companionship)
                else:
                    self.result['message'] = f'Unsupported entity type: {entity_type}'
                    return self.result
                
                # If any errors occurred, roll back the transaction
                if self.result['errors'] and not self.result['created'] and not self.result['updated']:
                    raise Exception("Import failed with errors and no successful imports")
                
            # Set success message
            self.result['success'] = True
            self.result['message'] = f'Successfully processed {self.result["total"]} records.'
            
        except json.JSONDecodeError:
            self.result['message'] = 'Invalid JSON format. Could not parse the file.'
        except Exception as e:
            logger.error(f"Error processing import: {str(e)}")
            self.result['message'] = f'Error processing import: {str(e)}'
            
        return self.result
    
    def _process_comprehensive_import(self, data):
        """
        Process a comprehensive import containing multiple entity types.
        
        Args:
            data: The parsed JSON data
        """
        logger.info("Processing comprehensive import")
        
        # Handle both dict and list formats
        if isinstance(data, list):
            logger.info("Converting list data to comprehensive format")
            data = {"plants": data}
        
        if not isinstance(data, dict):
            self.result['message'] = 'Invalid JSON format for comprehensive import. Expected an object or array.'
            return
        
        # Log the keys in the data
        logger.info(f"Comprehensive import data keys: {list(data.keys())}")
        
        # Extract data for each entity type
        plants_data = data.get('plants', [])
        logger.info(f"Found {len(plants_data)} plants in the import data")
        
        pests_data = data.get('pests', [])
        logger.info(f"Found {len(pests_data)} pests in the import data")
        
        diseases_data = data.get('diseases', [])
        logger.info(f"Found {len(diseases_data)} diseases in the import data")
        
        companions_data = data.get('companion_relationships', [])
        logger.info(f"Found {len(companions_data)} companion relationships in the import data")
        
        # Import plants first (needed for relationships)
        if plants_data:
            self.result['total'] += len(plants_data)
            for plant_data in plants_data:
                self._import_plant(plant_data)
        
        # Import pests
        if pests_data:
            self.result['total'] += len(pests_data)
            for pest_data in pests_data:
                self._import_pest(pest_data)
        
        # Import diseases
        if diseases_data:
            self.result['total'] += len(diseases_data)
            for disease_data in diseases_data:
                self._import_disease(disease_data)
        
        # Import companion relationships (depends on plants)
        if companions_data:
            self.result['total'] += len(companions_data)
            for companion_data in companions_data:
                self._import_companionship(companion_data)
    
    def _process_simple_import(self, data, import_func):
        """
        Process a simple import of a single entity type.
        
        Args:
            data: The parsed JSON data
            import_func: The function to use for importing each item
        """
        if not isinstance(data, list):
            self.result['message'] = 'Invalid JSON format. Expected a list of objects.'
            return
        
        self.result['total'] = len(data)
        for item in data:
            import_func(item)
    
    def _import_plant(self, plant_data):
        """
        Import a single plant.
        
        Args:
            plant_data (dict): The plant data to import
        """
        try:
            scientific_name = plant_data.get('scientific_name')
            if not scientific_name:
                self.result['errors'].append(f'Missing scientific_name in plant data: {plant_data}')
                self.result['skipped'] += 1
                return None
            
            logger.info(f"Processing plant: {scientific_name}")
            
            # Check if plant already exists
            existing_plant = Plant.objects.filter(scientific_name=scientific_name).first()
            
            if existing_plant and self.update_existing:
                # Update existing plant
                logger.info(f"Updating existing plant: {scientific_name}")
                for key, value in plant_data.items():
                    if hasattr(existing_plant, key) and key != 'id':
                        setattr(existing_plant, key, value)
                existing_plant.save()
                self.result['updated'] += 1
                self.created_plants[scientific_name] = existing_plant
                return existing_plant
            elif not existing_plant:
                # Create new plant
                logger.info(f"Creating new plant: {scientific_name}")
                plant = Plant.objects.create(**plant_data)
                self.result['created'] += 1
                self.created_plants[scientific_name] = plant
                return plant
            else:
                # Skip existing plant
                logger.info(f"Skipping existing plant: {scientific_name}")
                self.result['skipped'] += 1
                return None
        except Exception as e:
            logger.error(f"Error processing plant: {str(e)}")
            self.result['errors'].append(f'Error processing plant: {str(e)}')
            self.result['skipped'] += 1
            return None
    
    def _import_pest(self, pest_data):
        """
        Import a single pest.
        
        Args:
            pest_data (dict): The pest data to import
        """
        try:
            common_name = pest_data.get('common_name')
            if not common_name:
                self.result['errors'].append(f'Missing common_name in pest data: {pest_data}')
                self.result['skipped'] += 1
                return None
            
            logger.info(f"Processing pest: {common_name}")
            
            # Make a copy of the data and extract affected_plants
            pest_data_copy = pest_data.copy()
            affected_plants = pest_data_copy.pop('affected_plants', [])
            logger.info(f"Pest {common_name} has {len(affected_plants)} affected plants: {affected_plants}")
            
            # Check if pest already exists
            existing_pest = Pest.objects.filter(common_name=common_name).first()
            
            if existing_pest and self.update_existing:
                # Update existing pest
                logger.info(f"Updating existing pest: {common_name}")
                for key, value in pest_data_copy.items():
                    if hasattr(existing_pest, key) and key != 'id':
                        setattr(existing_pest, key, value)
                existing_pest.save()
                
                # Update plant relationships
                self._link_pest_to_plants(existing_pest, affected_plants)
                
                self.result['updated'] += 1
                self.created_pests[common_name] = existing_pest
                return existing_pest
            elif not existing_pest:
                # Create new pest
                logger.info(f"Creating new pest: {common_name}")
                pest = Pest.objects.create(**pest_data_copy)
                
                # Link to plants
                self._link_pest_to_plants(pest, affected_plants)
                
                self.result['created'] += 1
                self.created_pests[common_name] = pest
                return pest
            else:
                # Skip existing pest
                logger.info(f"Skipping existing pest: {common_name}")
                self.result['skipped'] += 1
                return None
        except Exception as e:
            logger.error(f"Error processing pest: {str(e)}")
            self.result['errors'].append(f'Error processing pest: {str(e)}')
            self.result['skipped'] += 1
            return None
    
    def _link_pest_to_plants(self, pest, plant_names):
        """
        Link a pest to plants.
        
        Args:
            pest: The Pest object
            plant_names (list): List of plant scientific names
        """
        if not plant_names:
            return
        
        logger.info(f"Linking pest {pest.common_name} to {len(plant_names)} plants")
        
        # First, remove existing relationships
        deleted_count, _ = PlantPest.objects.filter(pest=pest).delete()
        logger.info(f"Deleted {deleted_count} existing plant-pest relationships")
        
        # Then, add new relationships
        for plant_name in plant_names:
            logger.info(f"Looking for plant: {plant_name}")
            
            # Try to find the plant in our created plants first
            plant = self.created_plants.get(plant_name)
            
            # If not found, try to find it in the database
            if not plant:
                plant = Plant.objects.filter(scientific_name=plant_name).first()
            
            if plant:
                logger.info(f"Found plant {plant_name}, creating PlantPest link")
                link, created = PlantPest.objects.get_or_create(plant=plant, pest=pest)
                logger.info(f"PlantPest link created: {created}, ID: {link.id}")
            else:
                logger.error(f"Plant not found for pest {pest.common_name}: {plant_name}")
                self.result['errors'].append(f'Plant not found for pest {pest.common_name}: {plant_name}')
    
    def _import_disease(self, disease_data):
        """
        Import a single disease.
        
        Args:
            disease_data (dict): The disease data to import
        """
        try:
            common_name = disease_data.get('common_name')
            if not common_name:
                self.result['errors'].append(f'Missing common_name in disease data: {disease_data}')
                self.result['skipped'] += 1
                return None
            
            logger.info(f"Processing disease: {common_name}")
            
            # Make a copy of the data and extract affected_plants
            disease_data_copy = disease_data.copy()
            affected_plants = disease_data_copy.pop('affected_plants', [])
            logger.info(f"Disease {common_name} has {len(affected_plants)} affected plants: {affected_plants}")
            
            # Check if disease already exists
            existing_disease = Disease.objects.filter(common_name=common_name).first()
            
            if existing_disease and self.update_existing:
                # Update existing disease
                logger.info(f"Updating existing disease: {common_name}")
                for key, value in disease_data_copy.items():
                    if hasattr(existing_disease, key) and key != 'id':
                        setattr(existing_disease, key, value)
                existing_disease.save()
                
                # Update plant relationships
                self._link_disease_to_plants(existing_disease, affected_plants)
                
                self.result['updated'] += 1
                self.created_diseases[common_name] = existing_disease
                return existing_disease
            elif not existing_disease:
                # Create new disease
                logger.info(f"Creating new disease: {common_name}")
                disease = Disease.objects.create(**disease_data_copy)
                
                # Link to plants
                self._link_disease_to_plants(disease, affected_plants)
                
                self.result['created'] += 1
                self.created_diseases[common_name] = disease
                return disease
            else:
                # Skip existing disease
                logger.info(f"Skipping existing disease: {common_name}")
                self.result['skipped'] += 1
                return None
        except Exception as e:
            logger.error(f"Error processing disease: {str(e)}")
            self.result['errors'].append(f'Error processing disease: {str(e)}')
            self.result['skipped'] += 1
            return None
    
    def _link_disease_to_plants(self, disease, plant_names):
        """
        Link a disease to plants.
        
        Args:
            disease: The Disease object
            plant_names (list): List of plant scientific names
        """
        if not plant_names:
            return
        
        logger.info(f"Linking disease {disease.common_name} to {len(plant_names)} plants")
        
        # First, remove existing relationships
        deleted_count, _ = PlantDisease.objects.filter(disease=disease).delete()
        logger.info(f"Deleted {deleted_count} existing plant-disease relationships")
        
        # Then, add new relationships
        for plant_name in plant_names:
            logger.info(f"Looking for plant: {plant_name}")
            
            # Try to find the plant in our created plants first
            plant = self.created_plants.get(plant_name)
            
            # If not found, try to find it in the database
            if not plant:
                plant = Plant.objects.filter(scientific_name=plant_name).first()
            
            if plant:
                logger.info(f"Found plant {plant_name}, creating PlantDisease link")
                link, created = PlantDisease.objects.get_or_create(plant=plant, disease=disease)
                logger.info(f"PlantDisease link created: {created}, ID: {link.id}")
            else:
                logger.error(f"Plant not found for disease {disease.common_name}: {plant_name}")
                self.result['errors'].append(f'Plant not found for disease {disease.common_name}: {plant_name}')
    
    def _import_companionship(self, companion_data):
        """
        Import a single companionship relationship.
        
        Args:
            companion_data (dict): The companionship data to import
        """
        try:
            plant_subject_name = companion_data.get('plant_subject')
            plant_object_name = companion_data.get('plant_object')
            
            if not plant_subject_name or not plant_object_name:
                self.result['errors'].append(f'Missing plant_subject or plant_object in companionship data: {companion_data}')
                self.result['skipped'] += 1
                return None
            
            logger.info(f"Processing companionship: {plant_subject_name} -> {plant_object_name}")
            
            # Make a copy of the data and extract interactions
            companion_data_copy = companion_data.copy()
            interactions_data = companion_data_copy.pop('interactions', [])
            
            # Get the related plants
            plant_subject = self.created_plants.get(plant_subject_name)
            if not plant_subject:
                plant_subject = Plant.objects.filter(scientific_name=plant_subject_name).first()
            
            plant_object = self.created_plants.get(plant_object_name)
            if not plant_object:
                plant_object = Plant.objects.filter(scientific_name=plant_object_name).first()
            
            if not plant_subject or not plant_object:
                self.result['errors'].append(f'Plant not found: {plant_subject_name} or {plant_object_name}')
                self.result['skipped'] += 1
                return None
            
            # Prepare companionship data
            companionship_data = {
                'plant_subject': plant_subject,
                'plant_object': plant_object,
                'notes': companion_data_copy.get('notes', '')
            }
            
            # Check if companionship already exists
            existing_companionship = Companionship.objects.filter(
                plant_subject=plant_subject,
                plant_object=plant_object
            ).first()
            
            if existing_companionship and self.update_existing:
                # Update existing companionship
                logger.info(f"Updating existing companionship: {plant_subject_name} -> {plant_object_name}")
                existing_companionship.notes = companionship_data['notes']
                existing_companionship.save()
                
                # Update interactions
                self._link_interactions_to_companionship(existing_companionship, interactions_data)
                
                self.result['updated'] += 1
                return existing_companionship
            elif not existing_companionship:
                # Create new companionship
                logger.info(f"Creating new companionship: {plant_subject_name} -> {plant_object_name}")
                companionship = Companionship.objects.create(**companionship_data)
                
                # Link interactions
                self._link_interactions_to_companionship(companionship, interactions_data)
                
                self.result['created'] += 1
                return companionship
            else:
                # Skip existing companionship
                logger.info(f"Skipping existing companionship: {plant_subject_name} -> {plant_object_name}")
                self.result['skipped'] += 1
                return None
        except Exception as e:
            logger.error(f"Error processing companionship: {str(e)}")
            self.result['errors'].append(f'Error processing companionship: {str(e)}')
            self.result['skipped'] += 1
            return None
    
    def _link_interactions_to_companionship(self, companionship, interactions_data):
        """
        Link interactions to a companionship.
        
        Args:
            companionship: The Companionship object
            interactions_data (list): List of interaction data
        """
        if not interactions_data:
            return
        
        logger.info(f"Linking {len(interactions_data)} interactions to companionship")
        
        # Clear existing interactions
        companionship.interactions.clear()
        
        # Add new interactions
        for interaction_data in interactions_data:
            interaction_type = interaction_data.get('interaction_type')
            mechanism_description = interaction_data.get('mechanism_description')
            
            if not interaction_type or not mechanism_description:
                self.result['errors'].append(f'Missing interaction_type or mechanism_description in interaction data: {interaction_data}')
                continue
            
            # Generate a consistent code for the interaction
            inter_code = f"{interaction_type}_{mechanism_description[:20]}".replace(" ", "_").upper()
            
            # Check if we've already created this interaction
            interaction = self.created_interactions.get(inter_code)
            
            if not interaction:
                # Create or get the interaction
                interaction, created = CompanionPlantingInteraction.objects.get_or_create(
                    interaction_code=inter_code,
                    defaults={
                        'interaction_type': interaction_type,
                        'mechanism_description': mechanism_description
                    }
                )
                self.created_interactions[inter_code] = interaction
            
            # Add the interaction to the companionship
            companionship.interactions.add(interaction)
    
    def _import_seed(self, seed_data):
        """
        Import a single seed.
        
        Args:
            seed_data (dict): The seed data to import
        """
        try:
            seed_name = seed_data.get('seed_name')
            if not seed_name:
                self.result['errors'].append(f'Missing seed_name in seed data: {seed_data}')
                self.result['skipped'] += 1
                return None
            
            logger.info(f"Processing seed: {seed_name}")
            
            # Make a copy of the data
            seed_data_copy = seed_data.copy()
            
            # Handle plant reference
            plant_scientific_name = seed_data_copy.pop('plant', None)
            plant = None
            
            if plant_scientific_name:
                # Try to find the plant in our created plants first
                plant = self.created_plants.get(plant_scientific_name)
                
                # If not found, try to find it in the database
                if not plant:
                    plant = Plant.objects.filter(scientific_name=plant_scientific_name).first()
                
                if not plant:
                    self.result['errors'].append(f'Plant not found for seed {seed_name}: {plant_scientific_name}')
                    self.result['skipped'] += 1
                    return None
                
                seed_data_copy['plant'] = plant
            
            # Check if seed already exists
            existing_seed = Seed.objects.filter(seed_name=seed_name).first()
            
            if existing_seed and self.update_existing:
                # Update existing seed
                logger.info(f"Updating existing seed: {seed_name}")
                for key, value in seed_data_copy.items():
                    if hasattr(existing_seed, key) and key != 'id':
                        setattr(existing_seed, key, value)
                existing_seed.save()
                self.result['updated'] += 1
                return existing_seed
            elif not existing_seed:
                # Create new seed
                logger.info(f"Creating new seed: {seed_name}")
                seed = Seed.objects.create(**seed_data_copy)
                self.result['created'] += 1
                return seed
            else:
                # Skip existing seed
                logger.info(f"Skipping existing seed: {seed_name}")
                self.result['skipped'] += 1
                return None
        except Exception as e:
            logger.error(f"Error processing seed: {str(e)}")
            self.result['errors'].append(f'Error processing seed: {str(e)}')
            self.result['skipped'] += 1
            return None
    
    def _import_fertilizer(self, fertilizer_data):
        """
        Import a single fertilizer.
        
        Args:
            fertilizer_data (dict): The fertilizer data to import
        """
        try:
            fertilizer_name = fertilizer_data.get('fertilizer_name')
            if not fertilizer_name:
                self.result['errors'].append(f'Missing fertilizer_name in fertilizer data: {fertilizer_data}')
                self.result['skipped'] += 1
                return None
            
            logger.info(f"Processing fertilizer: {fertilizer_name}")
            
            # Check if fertilizer already exists
            existing_fertilizer = Fertilizer.objects.filter(fertilizer_name=fertilizer_name).first()
            
            if existing_fertilizer and self.update_existing:
                # Update existing fertilizer
                logger.info(f"Updating existing fertilizer: {fertilizer_name}")
                for key, value in fertilizer_data.items():
                    if hasattr(existing_fertilizer, key) and key != 'id':
                        setattr(existing_fertilizer, key, value)
                existing_fertilizer.save()
                self.result['updated'] += 1
                return existing_fertilizer
            elif not existing_fertilizer:
                # Create new fertilizer
                logger.info(f"Creating new fertilizer: {fertilizer_name}")
                fertilizer = Fertilizer.objects.create(**fertilizer_data)
                self.result['created'] += 1
                return fertilizer
            else:
                # Skip existing fertilizer
                logger.info(f"Skipping existing fertilizer: {fertilizer_name}")
                self.result['skipped'] += 1
                return None
        except Exception as e:
            logger.error(f"Error processing fertilizer: {str(e)}")
            self.result['errors'].append(f'Error processing fertilizer: {str(e)}')
            self.result['skipped'] += 1
            return None
    
    def _import_region(self, region_data):
        """
        Import a single region.
        
        Args:
            region_data (dict): The region data to import
        """
        try:
            zone_identifier = region_data.get('zone_identifier')
            zone_system = region_data.get('zone_system')
            
            if not zone_identifier or not zone_system:
                self.result['errors'].append(f'Missing zone_identifier or zone_system in region data: {region_data}')
                self.result['skipped'] += 1
                return None
            
            logger.info(f"Processing region: {zone_system} {zone_identifier}")
            
            # Check if region already exists
            existing_region = Region.objects.filter(
                zone_identifier=zone_identifier,
                zone_system=zone_system
            ).first()
            
            if existing_region and self.update_existing:
                # Update existing region
                logger.info(f"Updating existing region: {zone_system} {zone_identifier}")
                for key, value in region_data.items():
                    if hasattr(existing_region, key) and key != 'id':
                        setattr(existing_region, key, value)
                existing_region.save()
                self.result['updated'] += 1
                return existing_region
            elif not existing_region:
                # Create new region
                logger.info(f"Creating new region: {zone_system} {zone_identifier}")
                region = Region.objects.create(**region_data)
                self.result['created'] += 1
                return region
            else:
                # Skip existing region
                logger.info(f"Skipping existing region: {zone_system} {zone_identifier}")
                self.result['skipped'] += 1
                return None
        except Exception as e:
            logger.error(f"Error processing region: {str(e)}")
            self.result['errors'].append(f'Error processing region: {str(e)}')
            self.result['skipped'] += 1
            return None
    
    def _import_soil_profile(self, soil_profile_data):
        """
        Import a single soil profile.
        
        Args:
            soil_profile_data (dict): The soil profile data to import
        """
        try:
            name = soil_profile_data.get('name')
            if not name:
                self.result['errors'].append(f'Missing name in soil profile data: {soil_profile_data}')
                self.result['skipped'] += 1
                return None
            
            logger.info(f"Processing soil profile: {name}")
            
            # Check if soil profile already exists
            existing_profile = SoilProfile.objects.filter(name=name).first()
            
            if existing_profile and self.update_existing:
                # Update existing soil profile
                logger.info(f"Updating existing soil profile: {name}")
                for key, value in soil_profile_data.items():
                    if hasattr(existing_profile, key) and key != 'id':
                        setattr(existing_profile, key, value)
                existing_profile.save()
                self.result['updated'] += 1
                return existing_profile
            elif not existing_profile:
                # Create new soil profile
                logger.info(f"Creating new soil profile: {name}")
                profile = SoilProfile.objects.create(**soil_profile_data)
                self.result['created'] += 1
                return profile
            else:
                # Skip existing soil profile
                logger.info(f"Skipping existing soil profile: {name}")
                self.result['skipped'] += 1
                return None
        except Exception as e:
            logger.error(f"Error processing soil profile: {str(e)}")
            self.result['errors'].append(f'Error processing soil profile: {str(e)}')
            self.result['skipped'] += 1
            return None
