# garden_db_project/horticulture/schema.py
import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import logging # Added for basic error logging
from django.utils import timezone # Added for timestamping reviews

# Import all models needed for types and mutations
from .models import (
    Region, SoilProfile, Plant, User, Fertilizer, Pest, Disease, Seed,
    Companionship, PlantPest, PlantDisease, UserContribution,
    CompanionPlantingInteraction
)

logger = logging.getLogger(__name__) # Added logger

# --- Object Types ---

class RegionType(DjangoObjectType):
    class Meta:
        model = Region
        fields = "__all__"

class SoilProfileType(DjangoObjectType):
    class Meta:
        model = SoilProfile
        fields = "__all__"

class PlantType(DjangoObjectType):
    class Meta:
        model = Plant
        fields = "__all__"

class UserType(DjangoObjectType):
    class Meta:
        model = User
        # Exclude password_hash for security
        exclude = ("password_hash",)

class FertilizerType(DjangoObjectType):
    class Meta:
        model = Fertilizer
        fields = "__all__"

class PestType(DjangoObjectType):
    class Meta:
        model = Pest
        fields = "__all__"

class DiseaseType(DjangoObjectType):
    class Meta:
        model = Disease
        fields = "__all__"

class SeedType(DjangoObjectType):
    class Meta:
        model = Seed
        fields = "__all__"

class CompanionshipType(DjangoObjectType):
    class Meta:
        model = Companionship
        fields = "__all__"

class PlantPestType(DjangoObjectType):
    class Meta:
        model = PlantPest
        fields = "__all__"

class PlantDiseaseType(DjangoObjectType):
    class Meta:
        model = PlantDisease
        fields = "__all__"

class UserContributionType(DjangoObjectType):
    class Meta:
        model = UserContribution
        fields = "__all__"

class CompanionPlantingInteractionType(DjangoObjectType):
    class Meta:
        model = CompanionPlantingInteraction
        fields = "__all__"


# --- Query ---

class Query(graphene.ObjectType):
    # User Queries
    all_users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.UUID(required=True))

    def resolve_all_users(root, info):
        # Add permission checks later
        return User.objects.all()

    def resolve_user_by_id(root, info, id):
        # Add permission checks later
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

    # Region Queries
    all_regions = graphene.List(RegionType)
    region_by_id = graphene.Field(RegionType, id=graphene.ID(required=True))

    def resolve_all_regions(root, info):
        return Region.objects.all()

    def resolve_region_by_id(root, info, id):
        try:
            return Region.objects.get(pk=id)
        except Region.DoesNotExist:
            return None

    # SoilProfile Queries
    all_soil_profiles = graphene.List(SoilProfileType)
    soil_profile_by_id = graphene.Field(SoilProfileType, id=graphene.ID(required=True))

    def resolve_all_soil_profiles(root, info):
        return SoilProfile.objects.all()

    def resolve_soil_profile_by_id(root, info, id):
         try:
            return SoilProfile.objects.get(pk=id)
         except SoilProfile.DoesNotExist:
            return None

    # Plant Queries
    all_plants = graphene.List(PlantType)
    plant_by_id = graphene.Field(PlantType, id=graphene.ID(required=True))

    def resolve_all_plants(root, info):
        return Plant.objects.all()

    def resolve_plant_by_id(root, info, id):
         try:
            return Plant.objects.get(pk=id)
         except Plant.DoesNotExist:
            return None

    # Fertilizer Queries
    all_fertilizers = graphene.List(FertilizerType)
    fertilizer_by_id = graphene.Field(FertilizerType, id=graphene.ID(required=True))

    def resolve_all_fertilizers(root, info):
        return Fertilizer.objects.all()

    def resolve_fertilizer_by_id(root, info, id):
         try:
            return Fertilizer.objects.get(pk=id)
         except Fertilizer.DoesNotExist:
            return None

    # Pest Queries
    all_pests = graphene.List(PestType)
    pest_by_id = graphene.Field(PestType, id=graphene.ID(required=True))

    def resolve_all_pests(root, info):
        return Pest.objects.all()

    def resolve_pest_by_id(root, info, id):
         try:
            return Pest.objects.get(pk=id)
         except Pest.DoesNotExist:
            return None

    # Disease Queries
    all_diseases = graphene.List(DiseaseType)
    disease_by_id = graphene.Field(DiseaseType, id=graphene.ID(required=True))

    def resolve_all_diseases(root, info):
        return Disease.objects.all()

    def resolve_disease_by_id(root, info, id):
         try:
            return Disease.objects.get(pk=id)
         except Disease.DoesNotExist:
            return None

    # Seed Queries
    all_seeds = graphene.List(SeedType)
    seed_by_id = graphene.Field(SeedType, id=graphene.ID(required=True))

    def resolve_all_seeds(root, info):
        return Seed.objects.all()

    def resolve_seed_by_id(root, info, id):
         try:
            return Seed.objects.get(pk=id)
         except Seed.DoesNotExist:
            return None

    # Companionship Queries
    all_companionships = graphene.List(CompanionshipType)
    companionship_by_id = graphene.Field(CompanionshipType, id=graphene.ID(required=True))

    def resolve_all_companionships(root, info):
        return Companionship.objects.all()

    def resolve_companionship_by_id(root, info, id):
         try:
            return Companionship.objects.get(pk=id)
         except Companionship.DoesNotExist:
            return None

    # PlantPest Queries
    all_plant_pests = graphene.List(PlantPestType)
    plant_pest_by_id = graphene.Field(PlantPestType, id=graphene.ID(required=True))

    def resolve_all_plant_pests(root, info):
        return PlantPest.objects.all()

    def resolve_plant_pest_by_id(root, info, id):
         try:
            # Assuming implicit 'id' field for through model
            return PlantPest.objects.get(pk=id)
         except PlantPest.DoesNotExist:
            return None

    # PlantDisease Queries
    all_plant_diseases = graphene.List(PlantDiseaseType)
    plant_disease_by_id = graphene.Field(PlantDiseaseType, id=graphene.ID(required=True))

    def resolve_all_plant_diseases(root, info):
        return PlantDisease.objects.all()

    def resolve_plant_disease_by_id(root, info, id):
         try:
            # Assuming implicit 'id' field for through model
            return PlantDisease.objects.get(pk=id)
         except PlantDisease.DoesNotExist:
            return None

    # UserContribution Queries
    all_user_contributions = graphene.List(UserContributionType)
    user_contribution_by_id = graphene.Field(UserContributionType, id=graphene.UUID(required=True)) # Use UUID

    def resolve_all_user_contributions(root, info):
        # Add permission checks later (e.g., only admins see all?)
        return UserContribution.objects.all()

    def resolve_user_contribution_by_id(root, info, id):
         # Add permission checks later (e.g., owner or admin?)
         try:
            return UserContribution.objects.get(pk=id)
         except UserContribution.DoesNotExist:
            return None

    # CompanionPlantingInteraction Queries
    all_companion_interactions = graphene.List(CompanionPlantingInteractionType)
    companion_interaction_by_id = graphene.Field(CompanionPlantingInteractionType, id=graphene.ID(required=True))

    def resolve_all_companion_interactions(root, info):
        return CompanionPlantingInteraction.objects.all()

    def resolve_companion_interaction_by_id(root, info, id):
         try:
            return CompanionPlantingInteraction.objects.get(pk=id)
         except CompanionPlantingInteraction.DoesNotExist:
            return None


# --- Mutations ---

# --- Region Mutations (Existing) ---
class CreateRegion(graphene.Mutation):
    class Arguments:
        zone_system = graphene.String(required=True)
        zone_identifier = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()

    ok = graphene.Boolean()
    region = graphene.Field(RegionType)

    @classmethod
    def mutate(cls, root, info, zone_system, zone_identifier, name=None, description=None):
        # Add permission checks (e.g., only admins?)
        try:
            region = Region(
                zone_system=zone_system,
                zone_identifier=zone_identifier,
                name=name,
                description=description
            )
            region.save()
            return CreateRegion(ok=True, region=region)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating Region: {e}")
             return CreateRegion(ok=False, region=None)
        except Exception as e:
            logger.error(f"Error creating Region: {e}")
            return CreateRegion(ok=False, region=None)

class UpdateRegion(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        zone_system = graphene.String() # Allow updating unique fields if needed
        zone_identifier = graphene.String()

    ok = graphene.Boolean()
    region = graphene.Field(RegionType)

    @classmethod
    def mutate(cls, root, info, id, name=None, description=None, zone_system=None, zone_identifier=None):
        # Add permission checks (e.g., only admins?)
        try:
            region = Region.objects.get(pk=id)
            updated = False
            if name is not None:
                region.name = name
                updated = True
            if description is not None:
                region.description = description
                updated = True
            if zone_system is not None:
                region.zone_system = zone_system
                updated = True
            if zone_identifier is not None:
                region.zone_identifier = zone_identifier
                updated = True

            if updated:
                region.save()
            return UpdateRegion(ok=True, region=region)
        except Region.DoesNotExist:
            return UpdateRegion(ok=False, region=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating Region {id}: {e}")
             return UpdateRegion(ok=False, region=None)
        except Exception as e:
            logger.error(f"Error updating Region {id}: {e}")
            return UpdateRegion(ok=False, region=None)

class DeleteRegion(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks (e.g., only admins?)
        try:
            region = Region.objects.get(pk=id)
            region.delete()
            return DeleteRegion(ok=True)
        except Region.DoesNotExist:
            return DeleteRegion(ok=False)
        except Exception as e:
            logger.error(f"Error deleting Region {id}: {e}")
            return DeleteRegion(ok=False)

# --- User Mutations ---
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password_hash = graphene.String(required=True) # Client should send hash
        role = graphene.String(required=True) # Default is 'user' in model, but require explicit role here

    ok = graphene.Boolean()
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, username, email, password_hash, role):
        # Add permission checks (e.g., only admins can create admins?)
        try:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash, # WARNING: Store securely hashed passwords only!
                role=role
            )
            user.save()
            return CreateUser(ok=True, user=user)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating User: {e}")
             return CreateUser(ok=False, user=None)
        except Exception as e:
            logger.error(f"Error creating User: {e}")
            return CreateUser(ok=False, user=None)

class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        username = graphene.String()
        email = graphene.String()
        password_hash = graphene.String() # Allow updating hash
        role = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, id, username=None, email=None, password_hash=None, role=None):
        # Add permission checks (e.g., user can update self, admin can update others?)
        try:
            user = User.objects.get(pk=id)
            updated = False
            if username is not None:
                user.username = username
                updated = True
            if email is not None:
                user.email = email
                updated = True
            if password_hash is not None:
                user.password_hash = password_hash # WARNING: Update with secure hash only!
                updated = True
            if role is not None:
                # Add check: only admin can change role?
                user.role = role
                updated = True

            if updated:
                user.save()
            return UpdateUser(ok=True, user=user)
        except User.DoesNotExist:
            return UpdateUser(ok=False, user=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating User {id}: {e}")
             return UpdateUser(ok=False, user=None)
        except Exception as e:
            logger.error(f"Error updating User {id}: {e}")
            return UpdateUser(ok=False, user=None)

class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks (e.g., only admins?)
        try:
            user = User.objects.get(pk=id)
            user.delete()
            return DeleteUser(ok=True)
        except User.DoesNotExist:
            return DeleteUser(ok=False)
        except Exception as e:
            logger.error(f"Error deleting User {id}: {e}")
            return DeleteUser(ok=False)


# --- SoilProfile Mutations ---
class CreateSoilProfile(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True) # Model allows null, but make required here
        soil_type = graphene.String(required=True) # Assuming choices are handled client-side
        structure = graphene.String(required=True)
        drainage = graphene.String(required=True)
        moisture_retention = graphene.String(required=True)
        organic_matter_content = graphene.String(required=True)
        ph_min = graphene.Decimal()
        ph_max = graphene.Decimal()
        description = graphene.String()

    ok = graphene.Boolean()
    soil_profile = graphene.Field(SoilProfileType)

    @classmethod
    def mutate(cls, root, info, name, soil_type, structure, drainage, moisture_retention, organic_matter_content, ph_min=None, ph_max=None, description=None):
        # Add permission checks
        try:
            soil_profile = SoilProfile(
                name=name,
                soil_type=soil_type,
                structure=structure,
                drainage=drainage,
                moisture_retention=moisture_retention,
                organic_matter_content=organic_matter_content,
                ph_min=ph_min,
                ph_max=ph_max,
                description=description
            )
            soil_profile.save()
            return CreateSoilProfile(ok=True, soil_profile=soil_profile)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating SoilProfile: {e}")
             return CreateSoilProfile(ok=False, soil_profile=None)
        except Exception as e:
            logger.error(f"Error creating SoilProfile: {e}")
            return CreateSoilProfile(ok=False, soil_profile=None)

class UpdateSoilProfile(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        soil_type = graphene.String()
        structure = graphene.String()
        ph_min = graphene.Decimal()
        ph_max = graphene.Decimal()
        drainage = graphene.String()
        moisture_retention = graphene.String()
        organic_matter_content = graphene.String()
        description = graphene.String()

    ok = graphene.Boolean()
    soil_profile = graphene.Field(SoilProfileType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            soil_profile = SoilProfile.objects.get(pk=id)
            updated = False
            for key, value in kwargs.items():
                if value is not None:
                    setattr(soil_profile, key, value)
                    updated = True

            if updated:
                soil_profile.save()
            return UpdateSoilProfile(ok=True, soil_profile=soil_profile)
        except SoilProfile.DoesNotExist:
            return UpdateSoilProfile(ok=False, soil_profile=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating SoilProfile {id}: {e}")
             return UpdateSoilProfile(ok=False, soil_profile=None)
        except Exception as e:
            logger.error(f"Error updating SoilProfile {id}: {e}")
            return UpdateSoilProfile(ok=False, soil_profile=None)

class DeleteSoilProfile(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            soil_profile = SoilProfile.objects.get(pk=id)
            soil_profile.delete()
            return DeleteSoilProfile(ok=True)
        except SoilProfile.DoesNotExist:
            return DeleteSoilProfile(ok=False)
        except Exception as e:
            logger.error(f"Error deleting SoilProfile {id}: {e}")
            return DeleteSoilProfile(ok=False)

# --- Fertilizer Mutations ---
class CreateFertilizer(graphene.Mutation):
    class Arguments:
        fertilizer_name = graphene.String(required=True)
        base_type = graphene.String(required=True) # e.g., 'organic', 'synthetic'
        form = graphene.String(required=True) # e.g., 'liquid', 'granular'
        npk_ratio = graphene.String() # e.g., '10-10-10'
        micronutrient_composition = graphene.List(graphene.String) # List of micronutrients
        application_method = graphene.String()
        application_frequency = graphene.String()
        manufacturer = graphene.String()
        notes = graphene.String()
        suitable_plants = graphene.List(graphene.ID) # IDs of Plant model

    ok = graphene.Boolean()
    fertilizer = graphene.Field(FertilizerType)

    @classmethod
    def mutate(cls, root, info, fertilizer_name, base_type, form, **kwargs):
        # Add permission checks
        try:
            # Handle M2M fields separately
            suitable_plant_ids = kwargs.pop('suitable_plants', [])
            kwargs['micronutrient_composition'] = kwargs.get('micronutrient_composition', []) # Ensure it's a list

            fertilizer = Fertilizer(
                fertilizer_name=fertilizer_name,
                base_type=base_type,
                form=form,
                **kwargs
            )
            fertilizer.save()
            if suitable_plant_ids:
                fertilizer.suitable_plants.set(suitable_plant_ids)

            return CreateFertilizer(ok=True, fertilizer=fertilizer)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating Fertilizer: {e}")
             return CreateFertilizer(ok=False, fertilizer=None)
        except Exception as e:
            logger.error(f"Error creating Fertilizer: {e}")
            return CreateFertilizer(ok=False, fertilizer=None)

class UpdateFertilizer(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        fertilizer_name = graphene.String()
        base_type = graphene.String()
        form = graphene.String()
        npk_ratio = graphene.String()
        micronutrient_composition = graphene.List(graphene.String)
        application_method = graphene.String()
        application_frequency = graphene.String()
        manufacturer = graphene.String()
        notes = graphene.String()
        suitable_plants = graphene.List(graphene.ID) # Allow updating M2M

    ok = graphene.Boolean()
    fertilizer = graphene.Field(FertilizerType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            fertilizer = Fertilizer.objects.get(pk=id)
            updated = False
            suitable_plant_ids = kwargs.pop('suitable_plants', None) # Handle M2M

            for key, value in kwargs.items():
                if value is not None:
                    setattr(fertilizer, key, value)
                    updated = True

            if suitable_plant_ids is not None:
                fertilizer.suitable_plants.set(suitable_plant_ids)
                updated = True # Consider M2M update as an update

            if updated:
                fertilizer.save()
            return UpdateFertilizer(ok=True, fertilizer=fertilizer)
        except Fertilizer.DoesNotExist:
            return UpdateFertilizer(ok=False, fertilizer=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating Fertilizer {id}: {e}")
             return UpdateFertilizer(ok=False, fertilizer=None)
        except Exception as e:
            logger.error(f"Error updating Fertilizer {id}: {e}")
            return UpdateFertilizer(ok=False, fertilizer=None)

class DeleteFertilizer(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            fertilizer = Fertilizer.objects.get(pk=id)
            fertilizer.delete()
            return DeleteFertilizer(ok=True)
        except Fertilizer.DoesNotExist:
            return DeleteFertilizer(ok=False)
        except Exception as e:
            logger.error(f"Error deleting Fertilizer {id}: {e}")
            return DeleteFertilizer(ok=False)

# --- Pest Mutations ---
class CreatePest(graphene.Mutation):
    class Arguments:
        common_name = graphene.String(required=True)
        scientific_name = graphene.String()
        category = graphene.String(required=True) # e.g., 'insect', 'fungus', 'mammal'
        description = graphene.String()
        identification_guide = graphene.String()
        life_cycle = graphene.String()
        damage_symptoms = graphene.String()
        treatment_strategies = graphene.List(graphene.String) # List of strategies
        affected_plants = graphene.List(graphene.ID) # IDs of Plant model

    ok = graphene.Boolean()
    pest = graphene.Field(PestType)

    @classmethod
    def mutate(cls, root, info, common_name, category, **kwargs):
        # Add permission checks
        try:
            affected_plant_ids = kwargs.pop('affected_plants', [])
            kwargs['treatment_strategies'] = kwargs.get('treatment_strategies', []) # Ensure list

            pest = Pest(
                common_name=common_name,
                category=category,
                **kwargs
            )
            pest.save()
            if affected_plant_ids:
                pest.affected_plants.set(affected_plant_ids)

            return CreatePest(ok=True, pest=pest)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating Pest: {e}")
             return CreatePest(ok=False, pest=None)
        except Exception as e:
            logger.error(f"Error creating Pest: {e}")
            return CreatePest(ok=False, pest=None)

class UpdatePest(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        common_name = graphene.String()
        scientific_name = graphene.String()
        category = graphene.String()
        description = graphene.String()
        identification_guide = graphene.String()
        life_cycle = graphene.String()
        damage_symptoms = graphene.String()
        treatment_strategies = graphene.List(graphene.String)
        affected_plants = graphene.List(graphene.ID)

    ok = graphene.Boolean()
    pest = graphene.Field(PestType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            pest = Pest.objects.get(pk=id)
            updated = False
            affected_plant_ids = kwargs.pop('affected_plants', None)

            for key, value in kwargs.items():
                if value is not None:
                    setattr(pest, key, value)
                    updated = True

            if affected_plant_ids is not None:
                pest.affected_plants.set(affected_plant_ids)
                updated = True

            if updated:
                pest.save()
            return UpdatePest(ok=True, pest=pest)
        except Pest.DoesNotExist:
            return UpdatePest(ok=False, pest=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating Pest {id}: {e}")
             return UpdatePest(ok=False, pest=None)
        except Exception as e:
            logger.error(f"Error updating Pest {id}: {e}")
            return UpdatePest(ok=False, pest=None)

class DeletePest(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            pest = Pest.objects.get(pk=id)
            pest.delete()
            return DeletePest(ok=True)
        except Pest.DoesNotExist:
            return DeletePest(ok=False)
        except Exception as e:
            logger.error(f"Error deleting Pest {id}: {e}")
            return DeletePest(ok=False)

# --- Disease Mutations ---
class CreateDisease(graphene.Mutation):
    class Arguments:
        common_name = graphene.String(required=True)
        scientific_name = graphene.String()
        category = graphene.String(required=True) # e.g., 'fungal', 'bacterial', 'viral'
        description = graphene.String()
        identification_guide = graphene.String()
        transmission_methods = graphene.String()
        symptoms = graphene.String()
        treatment_strategies = graphene.List(graphene.String)
        affected_plants = graphene.List(graphene.ID)

    ok = graphene.Boolean()
    disease = graphene.Field(DiseaseType)

    @classmethod
    def mutate(cls, root, info, common_name, category, **kwargs):
        # Add permission checks
        try:
            affected_plant_ids = kwargs.pop('affected_plants', [])
            kwargs['treatment_strategies'] = kwargs.get('treatment_strategies', []) # Ensure list

            disease = Disease(
                common_name=common_name,
                category=category,
                **kwargs
            )
            disease.save()
            if affected_plant_ids:
                disease.affected_plants.set(affected_plant_ids)

            return CreateDisease(ok=True, disease=disease)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating Disease: {e}")
             return CreateDisease(ok=False, disease=None)
        except Exception as e:
            logger.error(f"Error creating Disease: {e}")
            return CreateDisease(ok=False, disease=None)

class UpdateDisease(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        common_name = graphene.String()
        scientific_name = graphene.String()
        category = graphene.String()
        description = graphene.String()
        identification_guide = graphene.String()
        transmission_methods = graphene.String()
        symptoms = graphene.String()
        treatment_strategies = graphene.List(graphene.String)
        affected_plants = graphene.List(graphene.ID)

    ok = graphene.Boolean()
    disease = graphene.Field(DiseaseType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            disease = Disease.objects.get(pk=id)
            updated = False
            affected_plant_ids = kwargs.pop('affected_plants', None)

            for key, value in kwargs.items():
                if value is not None:
                    setattr(disease, key, value)
                    updated = True

            if affected_plant_ids is not None:
                disease.affected_plants.set(affected_plant_ids)
                updated = True

            if updated:
                disease.save()
            return UpdateDisease(ok=True, disease=disease)
        except Disease.DoesNotExist:
            return UpdateDisease(ok=False, disease=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating Disease {id}: {e}")
             return UpdateDisease(ok=False, disease=None)
        except Exception as e:
            logger.error(f"Error updating Disease {id}: {e}")
            return UpdateDisease(ok=False, disease=None)

class DeleteDisease(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            disease = Disease.objects.get(pk=id)
            disease.delete()
            return DeleteDisease(ok=True)
        except Disease.DoesNotExist:
            return DeleteDisease(ok=False)
        except Exception as e:
            logger.error(f"Error deleting Disease {id}: {e}")
            return DeleteDisease(ok=False)

# --- Plant Mutations ---
class CreatePlant(graphene.Mutation):
    class Arguments:
        scientific_name = graphene.String(required=True)
        common_name = graphene.String(required=True)
        family = graphene.String()
        genus = graphene.String()
        species = graphene.String()
        variety = graphene.String()
        description = graphene.String()
        plant_type = graphene.String() # e.g., 'vegetable', 'fruit', 'herb', 'flower'
        growth_habit = graphene.String() # e.g., 'bush', 'vine', 'tree'
        life_cycle = graphene.String() # e.g., 'annual', 'perennial', 'biennial'
        sun_exposure = graphene.String() # e.g., 'full sun', 'part shade'
        water_needs = graphene.String() # e.g., 'low', 'medium', 'high'
        soil_preference_id = graphene.ID() # FK to SoilProfile
        hardiness_zone_min = graphene.Int()
        hardiness_zone_max = graphene.Int()
        mature_height_min_cm = graphene.Int()
        mature_height_max_cm = graphene.Int()
        mature_width_min_cm = graphene.Int()
        mature_width_max_cm = graphene.Int()
        bloom_time = graphene.String() # e.g., 'spring', 'summer'
        flower_color = graphene.String()
        foliage_color = graphene.String()
        fruit_color = graphene.String()
        harvest_time = graphene.String()
        days_to_maturity_min = graphene.Int()
        days_to_maturity_max = graphene.Int()
        spacing_min_cm = graphene.Int()
        spacing_max_cm = graphene.Int()
        planting_depth_cm = graphene.Decimal()
        propagation_methods = graphene.List(graphene.String)
        uses = graphene.List(graphene.String) # e.g., 'culinary', 'medicinal', 'ornamental'
        origin_region_id = graphene.ID() # FK to Region
        notes = graphene.String()
        # M2M fields handled separately if needed (e.g., pests, diseases)

    ok = graphene.Boolean()
    plant = graphene.Field(PlantType)

    @classmethod
    def mutate(cls, root, info, scientific_name, common_name, **kwargs):
        # Add permission checks
        try:
            # Handle FKs
            soil_preference_id = kwargs.pop('soil_preference_id', None)
            origin_region_id = kwargs.pop('origin_region_id', None)
            kwargs['propagation_methods'] = kwargs.get('propagation_methods', [])
            kwargs['uses'] = kwargs.get('uses', [])

            plant = Plant(
                scientific_name=scientific_name,
                common_name=common_name,
                soil_preference_id=soil_preference_id,
                origin_region_id=origin_region_id,
                **kwargs
            )
            plant.save()
            # Handle M2M fields after save if needed

            return CreatePlant(ok=True, plant=plant)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating Plant: {e}")
             return CreatePlant(ok=False, plant=None)
        except Exception as e:
            logger.error(f"Error creating Plant: {e}")
            return CreatePlant(ok=False, plant=None)

class UpdatePlant(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        scientific_name = graphene.String()
        common_name = graphene.String()
        family = graphene.String()
        genus = graphene.String()
        species = graphene.String()
        variety = graphene.String()
        description = graphene.String()
        plant_type = graphene.String()
        growth_habit = graphene.String()
        life_cycle = graphene.String()
        sun_exposure = graphene.String()
        water_needs = graphene.String()
        soil_preference_id = graphene.ID()
        hardiness_zone_min = graphene.Int()
        hardiness_zone_max = graphene.Int()
        mature_height_min_cm = graphene.Int()
        mature_height_max_cm = graphene.Int()
        mature_width_min_cm = graphene.Int()
        mature_width_max_cm = graphene.Int()
        bloom_time = graphene.String()
        flower_color = graphene.String()
        foliage_color = graphene.String()
        fruit_color = graphene.String()
        harvest_time = graphene.String()
        days_to_maturity_min = graphene.Int()
        days_to_maturity_max = graphene.Int()
        spacing_min_cm = graphene.Int()
        spacing_max_cm = graphene.Int()
        planting_depth_cm = graphene.Decimal()
        propagation_methods = graphene.List(graphene.String)
        uses = graphene.List(graphene.String)
        origin_region_id = graphene.ID()
        notes = graphene.String()
        # M2M fields

    ok = graphene.Boolean()
    plant = graphene.Field(PlantType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            plant = Plant.objects.get(pk=id)
            updated = False
            # Handle FKs explicitly if needed, or let setattr handle them if ID is passed
            for key, value in kwargs.items():
                if value is not None:
                    setattr(plant, key, value)
                    updated = True

            # Handle M2M updates if needed

            if updated:
                plant.save()
            return UpdatePlant(ok=True, plant=plant)
        except Plant.DoesNotExist:
            return UpdatePlant(ok=False, plant=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating Plant {id}: {e}")
             return UpdatePlant(ok=False, plant=None)
        except Exception as e:
            logger.error(f"Error updating Plant {id}: {e}")
            return UpdatePlant(ok=False, plant=None)

class DeletePlant(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            plant = Plant.objects.get(pk=id)
            plant.delete()
            return DeletePlant(ok=True)
        except Plant.DoesNotExist:
            return DeletePlant(ok=False)
        except Exception as e:
            logger.error(f"Error deleting Plant {id}: {e}")
            return DeletePlant(ok=False)

# --- Seed Mutations ---
class CreateSeed(graphene.Mutation):
    class Arguments:
        plant_id = graphene.ID(required=True) # FK to Plant
        seed_name = graphene.String(required=True) # e.g., 'Heirloom Tomato Seeds'
        supplier = graphene.String()
        purchase_date = graphene.Date()
        quantity = graphene.Int()
        unit = graphene.String() # e.g., 'seeds', 'grams'
        germination_rate_percent = graphene.Decimal()
        viability_years = graphene.Int()
        days_to_germination_min = graphene.Int()
        days_to_germination_max = graphene.Int()
        seed_depth_cm = graphene.Decimal()
        seed_spacing_cm = graphene.Decimal()
        planting_instructions = graphene.String()
        storage_recommendations = graphene.String()
        is_organic = graphene.Boolean()
        is_gmo = graphene.Boolean()
        is_hybrid = graphene.Boolean()
        is_heirloom = graphene.Boolean()
        packet_image_url = graphene.String()
        notes = graphene.String()

    ok = graphene.Boolean()
    seed = graphene.Field(SeedType)

    @classmethod
    def mutate(cls, root, info, plant_id, seed_name, **kwargs):
        # Add permission checks
        try:
            seed = Seed(
                plant_id=plant_id,
                seed_name=seed_name,
                **kwargs
            )
            seed.save()
            return CreateSeed(ok=True, seed=seed)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating Seed: {e}")
             return CreateSeed(ok=False, seed=None)
        except Exception as e:
            logger.error(f"Error creating Seed: {e}")
            return CreateSeed(ok=False, seed=None)

class UpdateSeed(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        plant_id = graphene.ID() # Allow changing associated plant?
        seed_name = graphene.String()
        supplier = graphene.String()
        purchase_date = graphene.Date()
        quantity = graphene.Int()
        unit = graphene.String()
        germination_rate_percent = graphene.Decimal()
        viability_years = graphene.Int()
        days_to_germination_min = graphene.Int()
        days_to_germination_max = graphene.Int()
        seed_depth_cm = graphene.Decimal()
        seed_spacing_cm = graphene.Decimal()
        planting_instructions = graphene.String()
        storage_recommendations = graphene.String()
        is_organic = graphene.Boolean()
        is_gmo = graphene.Boolean()
        is_hybrid = graphene.Boolean()
        is_heirloom = graphene.Boolean()
        packet_image_url = graphene.String()
        notes = graphene.String()

    ok = graphene.Boolean()
    seed = graphene.Field(SeedType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            seed = Seed.objects.get(pk=id)
            updated = False
            for key, value in kwargs.items():
                if value is not None:
                    setattr(seed, key, value)
                    updated = True

            if updated:
                seed.save()
            return UpdateSeed(ok=True, seed=seed)
        except Seed.DoesNotExist:
            return UpdateSeed(ok=False, seed=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating Seed {id}: {e}")
             return UpdateSeed(ok=False, seed=None)
        except Exception as e:
            logger.error(f"Error updating Seed {id}: {e}")
            return UpdateSeed(ok=False, seed=None)

class DeleteSeed(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            seed = Seed.objects.get(pk=id)
            seed.delete()
            return DeleteSeed(ok=True)
        except Seed.DoesNotExist:
            return DeleteSeed(ok=False)
        except Exception as e:
            logger.error(f"Error deleting Seed {id}: {e}")
            return DeleteSeed(ok=False)


# --- Companionship Mutations ---
# Note: Assumes unique constraint on (plant_subject, plant_object)
class CreateCompanionship(graphene.Mutation):
    class Arguments:
        plant_subject_id = graphene.ID(required=True)
        plant_object_id = graphene.ID(required=True)
        interaction_id = graphene.ID(required=True) # FK to CompanionPlantingInteraction
        strength_confidence = graphene.String() # e.g., 'strong', 'weak', 'anecdotal'
        notes = graphene.String()

    ok = graphene.Boolean()
    companionship = graphene.Field(CompanionshipType)

    @classmethod
    def mutate(cls, root, info, plant_subject_id, plant_object_id, interaction_id, strength_confidence=None, notes=None):
        # Add permission checks
        try:
            companionship = Companionship(
                plant_subject_id=plant_subject_id,
                plant_object_id=plant_object_id,
                interaction_id=interaction_id,
                strength_confidence=strength_confidence,
                notes=notes
            )
            companionship.save()
            return CreateCompanionship(ok=True, companionship=companionship)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating Companionship: {e}")
             return CreateCompanionship(ok=False, companionship=None)
        except Exception as e:
            logger.error(f"Error creating Companionship: {e}")
            return CreateCompanionship(ok=False, companionship=None)

class UpdateCompanionship(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True) # Use the implicit PK
        plant_subject_id = graphene.ID() # Allow changing? Might violate unique constraint
        plant_object_id = graphene.ID() # Allow changing? Might violate unique constraint
        interaction_id = graphene.ID()
        strength_confidence = graphene.String()
        notes = graphene.String()

    ok = graphene.Boolean()
    companionship = graphene.Field(CompanionshipType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            companionship = Companionship.objects.get(pk=id)
            updated = False
            for key, value in kwargs.items():
                if value is not None:
                    setattr(companionship, key, value)
                    updated = True

            if updated:
                companionship.save()
            return UpdateCompanionship(ok=True, companionship=companionship)
        except Companionship.DoesNotExist:
            return UpdateCompanionship(ok=False, companionship=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating Companionship {id}: {e}")
             return UpdateCompanionship(ok=False, companionship=None)
        except Exception as e:
            logger.error(f"Error updating Companionship {id}: {e}")
            return UpdateCompanionship(ok=False, companionship=None)

class DeleteCompanionship(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True) # Use the implicit PK

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            companionship = Companionship.objects.get(pk=id)
            companionship.delete()
            return DeleteCompanionship(ok=True)
        except Companionship.DoesNotExist:
            return DeleteCompanionship(ok=False)
        except Exception as e:
            logger.error(f"Error deleting Companionship {id}: {e}")
            return DeleteCompanionship(ok=False)

# --- PlantPest Mutations (Through Model) ---
class CreatePlantPest(graphene.Mutation):
    class Arguments:
        plant_id = graphene.ID(required=True)
        pest_id = graphene.ID(required=True)
        notes = graphene.String()

    ok = graphene.Boolean()
    plant_pest = graphene.Field(PlantPestType)

    @classmethod
    def mutate(cls, root, info, plant_id, pest_id, notes=None):
        # Add permission checks
        try:
            plant_pest = PlantPest(
                plant_id=plant_id,
                pest_id=pest_id,
                notes=notes
            )
            plant_pest.save()
            return CreatePlantPest(ok=True, plant_pest=plant_pest)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating PlantPest: {e}")
             return CreatePlantPest(ok=False, plant_pest=None)
        except Exception as e:
            logger.error(f"Error creating PlantPest: {e}")
            return CreatePlantPest(ok=False, plant_pest=None)

class UpdatePlantPest(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True) # Use implicit PK
        plant_id = graphene.ID() # Allow changing?
        pest_id = graphene.ID() # Allow changing?
        notes = graphene.String()

    ok = graphene.Boolean()
    plant_pest = graphene.Field(PlantPestType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            plant_pest = PlantPest.objects.get(pk=id)
            updated = False
            for key, value in kwargs.items():
                if value is not None:
                    setattr(plant_pest, key, value)
                    updated = True

            if updated:
                plant_pest.save()
            return UpdatePlantPest(ok=True, plant_pest=plant_pest)
        except PlantPest.DoesNotExist:
            return UpdatePlantPest(ok=False, plant_pest=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating PlantPest {id}: {e}")
             return UpdatePlantPest(ok=False, plant_pest=None)
        except Exception as e:
            logger.error(f"Error updating PlantPest {id}: {e}")
            return UpdatePlantPest(ok=False, plant_pest=None)

class DeletePlantPest(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True) # Use implicit PK

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            plant_pest = PlantPest.objects.get(pk=id)
            plant_pest.delete()
            return DeletePlantPest(ok=True)
        except PlantPest.DoesNotExist:
            return DeletePlantPest(ok=False)
        except Exception as e:
            logger.error(f"Error deleting PlantPest {id}: {e}")
            return DeletePlantPest(ok=False)

# --- PlantDisease Mutations (Through Model) ---
class CreatePlantDisease(graphene.Mutation):
    class Arguments:
        plant_id = graphene.ID(required=True)
        disease_id = graphene.ID(required=True)
        notes = graphene.String()

    ok = graphene.Boolean()
    plant_disease = graphene.Field(PlantDiseaseType)

    @classmethod
    def mutate(cls, root, info, plant_id, disease_id, notes=None):
        # Add permission checks
        try:
            plant_disease = PlantDisease(
                plant_id=plant_id,
                disease_id=disease_id,
                notes=notes
            )
            plant_disease.save()
            return CreatePlantDisease(ok=True, plant_disease=plant_disease)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating PlantDisease: {e}")
             return CreatePlantDisease(ok=False, plant_disease=None)
        except Exception as e:
            logger.error(f"Error creating PlantDisease: {e}")
            return CreatePlantDisease(ok=False, plant_disease=None)

class UpdatePlantDisease(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True) # Use implicit PK
        plant_id = graphene.ID() # Allow changing?
        disease_id = graphene.ID() # Allow changing?
        notes = graphene.String()

    ok = graphene.Boolean()
    plant_disease = graphene.Field(PlantDiseaseType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            plant_disease = PlantDisease.objects.get(pk=id)
            updated = False
            for key, value in kwargs.items():
                if value is not None:
                    setattr(plant_disease, key, value)
                    updated = True

            if updated:
                plant_disease.save()
            return UpdatePlantDisease(ok=True, plant_disease=plant_disease)
        except PlantDisease.DoesNotExist:
            return UpdatePlantDisease(ok=False, plant_disease=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating PlantDisease {id}: {e}")
             return UpdatePlantDisease(ok=False, plant_disease=None)
        except Exception as e:
            logger.error(f"Error updating PlantDisease {id}: {e}")
            return UpdatePlantDisease(ok=False, plant_disease=None)

class DeletePlantDisease(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True) # Use implicit PK

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            plant_disease = PlantDisease.objects.get(pk=id)
            plant_disease.delete()
            return DeletePlantDisease(ok=True)
        except PlantDisease.DoesNotExist:
            return DeletePlantDisease(ok=False)
        except Exception as e:
            logger.error(f"Error deleting PlantDisease {id}: {e}")
            return DeletePlantDisease(ok=False)

# --- UserContribution Mutations ---
class CreateUserContribution(graphene.Mutation):
    class Arguments:
        user_id = graphene.UUID(required=True)
        entity_type = graphene.String(required=True) # e.g., 'Plant', 'Companionship'
        entity_id = graphene.ID() # Optional: ID of existing entity being modified
        proposed_data = graphene.JSONString(required=True) # JSON representing the proposed change/addition
        status = graphene.String(required=True) # Default 'pending' in model, but require here
        admin_notes = graphene.String() # Optional notes from user submitting

    ok = graphene.Boolean()
    user_contribution = graphene.Field(UserContributionType)

    @classmethod
    def mutate(cls, root, info, user_id, entity_type, proposed_data, status, entity_id=None, admin_notes=None):
        # Add permission checks (e.g., user must be authenticated)
        if not info.context.user.is_authenticated:
             logger.warning("Unauthenticated user tried to create contribution.")
             return CreateUserContribution(ok=False, user_contribution=None) # Or raise Exception

        try:
            user_contribution = UserContribution(
                user_id=user_id, # Or better: user=info.context.user if user_id matches logged-in user
                entity_type=entity_type,
                entity_id=entity_id,
                proposed_data=proposed_data,
                status=status, # Should likely default to 'pending' unless admin creates
                admin_notes=admin_notes # This field name might be confusing here, maybe 'user_notes'?
            )
            user_contribution.save()
            return CreateUserContribution(ok=True, user_contribution=user_contribution)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating UserContribution: {e}")
             return CreateUserContribution(ok=False, user_contribution=None)
        except Exception as e:
            logger.error(f"Error creating UserContribution: {e}")
            return CreateUserContribution(ok=False, user_contribution=None)

class UpdateUserContribution(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        user_id = graphene.UUID() # Allow changing user? Maybe not.
        entity_type = graphene.String()
        entity_id = graphene.ID()
        proposed_data = graphene.JSONString()
        status = graphene.String() # Admins might update this
        admin_notes = graphene.String() # Admins might add notes
        # reviewed_by_id = graphene.UUID() # Should be set internally on approve/reject
        # reviewed_at = graphene.DateTime() # Should be set internally

    ok = graphene.Boolean()
    user_contribution = graphene.Field(UserContributionType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks (e.g., only owner or admin can update?)
        # Admins should use Approve/Reject mutations for status changes primarily
        try:
            user_contribution = UserContribution.objects.get(pk=id)
            # Check permissions: e.g., if info.context.user != user_contribution.user and not info.context.user.is_staff: raise Exception("Not allowed")
            updated = False
            for key, value in kwargs.items():
                 # Prevent non-admins from changing status directly?
                if key == 'status' and (not info.context.user.is_authenticated or info.context.user.role != 'admin'):
                    continue # Skip status update if not admin
                if value is not None:
                    setattr(user_contribution, key, value)
                    updated = True

            if updated:
                user_contribution.save()
            return UpdateUserContribution(ok=True, user_contribution=user_contribution)
        except UserContribution.DoesNotExist:
            return UpdateUserContribution(ok=False, user_contribution=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating UserContribution {id}: {e}")
             return UpdateUserContribution(ok=False, user_contribution=None)
        except Exception as e:
            logger.error(f"Error updating UserContribution {id}: {e}")
            return UpdateUserContribution(ok=False, user_contribution=None)

class DeleteUserContribution(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks (e.g., only owner or admin?)
        try:
            user_contribution = UserContribution.objects.get(pk=id)
            # Check permissions here
            user_contribution.delete()
            return DeleteUserContribution(ok=True)
        except UserContribution.DoesNotExist:
            return DeleteUserContribution(ok=False)
        except Exception as e:
            logger.error(f"Error deleting UserContribution {id}: {e}")
            return DeleteUserContribution(ok=False)

# --- NEW: Approve/Reject UserContribution Mutations ---
class ApproveContribution(graphene.Mutation):
    """Approves a user contribution. Requires admin privileges."""
    class Arguments:
        id = graphene.UUID(required=True)

    ok = graphene.Boolean()
    contribution = graphene.Field(UserContributionType)

    @classmethod
    def mutate(cls, root, info, id):
        user = info.context.user
        if not user.is_authenticated or user.role != 'admin':
            logger.warning(f"Unauthorized attempt to approve contribution {id} by user {user.username if user.is_authenticated else 'anonymous'}")
            # Option 1: Raise Exception
            # raise Exception("You do not have permission to perform this action.")
            # Option 2: Return ok=False
            return ApproveContribution(ok=False, contribution=None)

        try:
            contribution_instance = UserContribution.objects.get(pk=id)
            contribution_instance.status = 'approved'
            contribution_instance.reviewed_at = timezone.now()
            contribution_instance.reviewed_by = user
            contribution_instance.save()
            # TODO: Add logic here to actually apply the contribution_instance.proposed_data
            # This might involve creating/updating the related entity (Plant, Companionship, etc.)
            logger.info(f"Contribution {id} approved by admin {user.username}")
            return ApproveContribution(ok=True, contribution=contribution_instance)
        except UserContribution.DoesNotExist:
            logger.error(f"ApproveContribution: Contribution with id {id} not found.")
            return ApproveContribution(ok=False, contribution=None)
        except Exception as e:
            logger.error(f"Error approving contribution {id}: {e}")
            return ApproveContribution(ok=False, contribution=None)

class RejectContribution(graphene.Mutation):
    """Rejects a user contribution. Requires admin privileges."""
    class Arguments:
        id = graphene.UUID(required=True)
        admin_notes = graphene.String() # Optional reason for rejection

    ok = graphene.Boolean()
    contribution = graphene.Field(UserContributionType)

    @classmethod
    def mutate(cls, root, info, id, admin_notes=None):
        user = info.context.user
        if not user.is_authenticated or user.role != 'admin':
            logger.warning(f"Unauthorized attempt to reject contribution {id} by user {user.username if user.is_authenticated else 'anonymous'}")
            # raise Exception("You do not have permission to perform this action.")
            return RejectContribution(ok=False, contribution=None)

        try:
            contribution_instance = UserContribution.objects.get(pk=id)
            contribution_instance.status = 'rejected'
            contribution_instance.reviewed_at = timezone.now()
            contribution_instance.reviewed_by = user
            if admin_notes:
                contribution_instance.admin_notes = admin_notes
            contribution_instance.save()
            logger.info(f"Contribution {id} rejected by admin {user.username}")
            return RejectContribution(ok=True, contribution=contribution_instance)
        except UserContribution.DoesNotExist:
            logger.error(f"RejectContribution: Contribution with id {id} not found.")
            return RejectContribution(ok=False, contribution=None)
        except Exception as e:
            logger.error(f"Error rejecting contribution {id}: {e}")
            return RejectContribution(ok=False, contribution=None)


# --- CompanionPlantingInteraction Mutations ---
class CreateCompanionPlantingInteraction(graphene.Mutation):
    class Arguments:
        interaction_code = graphene.String(required=True) # e.g., 'BENEFICIAL_PEST_REPELLENT'
        interaction_type = graphene.String(required=True) # e.g., 'beneficial', 'detrimental', 'neutral'
        mechanism_description = graphene.String()

    ok = graphene.Boolean()
    interaction = graphene.Field(CompanionPlantingInteractionType)

    @classmethod
    def mutate(cls, root, info, interaction_code, interaction_type, mechanism_description=None):
        # Add permission checks
        try:
            interaction = CompanionPlantingInteraction(
                interaction_code=interaction_code,
                interaction_type=interaction_type,
                mechanism_description=mechanism_description
            )
            interaction.save()
            return CreateCompanionPlantingInteraction(ok=True, interaction=interaction)
        except IntegrityError as e:
             logger.error(f"IntegrityError creating CompanionPlantingInteraction: {e}")
             return CreateCompanionPlantingInteraction(ok=False, interaction=None)
        except Exception as e:
            logger.error(f"Error creating CompanionPlantingInteraction: {e}")
            return CreateCompanionPlantingInteraction(ok=False, interaction=None)

class UpdateCompanionPlantingInteraction(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        interaction_code = graphene.String()
        interaction_type = graphene.String()
        mechanism_description = graphene.String()

    ok = graphene.Boolean()
    interaction = graphene.Field(CompanionPlantingInteractionType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        # Add permission checks
        try:
            interaction = CompanionPlantingInteraction.objects.get(pk=id)
            updated = False
            for key, value in kwargs.items():
                if value is not None:
                    setattr(interaction, key, value)
                    updated = True

            if updated:
                interaction.save()
            return UpdateCompanionPlantingInteraction(ok=True, interaction=interaction)
        except CompanionPlantingInteraction.DoesNotExist:
            return UpdateCompanionPlantingInteraction(ok=False, interaction=None)
        except IntegrityError as e:
             logger.error(f"IntegrityError updating CompanionPlantingInteraction {id}: {e}")
             return UpdateCompanionPlantingInteraction(ok=False, interaction=None)
        except Exception as e:
            logger.error(f"Error updating CompanionPlantingInteraction {id}: {e}")
            return UpdateCompanionPlantingInteraction(ok=False, interaction=None)

class DeleteCompanionPlantingInteraction(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        # Add permission checks
        try:
            interaction = CompanionPlantingInteraction.objects.get(pk=id)
            interaction.delete()
            return DeleteCompanionPlantingInteraction(ok=True)
        except CompanionPlantingInteraction.DoesNotExist:
            return DeleteCompanionPlantingInteraction(ok=False)
        except Exception as e:
            logger.error(f"Error deleting CompanionPlantingInteraction {id}: {e}")
            return DeleteCompanionPlantingInteraction(ok=False)


# --- Main Mutation Class ---
class Mutation(graphene.ObjectType):
    # Region Mutations
    create_region = CreateRegion.Field()
    update_region = UpdateRegion.Field()
    delete_region = DeleteRegion.Field()

    # User Mutations
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()

    # SoilProfile Mutations
    create_soil_profile = CreateSoilProfile.Field()
    update_soil_profile = UpdateSoilProfile.Field()
    delete_soil_profile = DeleteSoilProfile.Field()

    # Fertilizer Mutations
    create_fertilizer = CreateFertilizer.Field()
    update_fertilizer = UpdateFertilizer.Field()
    delete_fertilizer = DeleteFertilizer.Field()

    # Pest Mutations
    create_pest = CreatePest.Field()
    update_pest = UpdatePest.Field()
    delete_pest = DeletePest.Field()

    # Disease Mutations
    create_disease = CreateDisease.Field()
    update_disease = UpdateDisease.Field()
    delete_disease = DeleteDisease.Field()

    # Plant Mutations
    create_plant = CreatePlant.Field()
    update_plant = UpdatePlant.Field()
    delete_plant = DeletePlant.Field()

    # Seed Mutations
    create_seed = CreateSeed.Field()
    update_seed = UpdateSeed.Field()
    delete_seed = DeleteSeed.Field()

    # Companionship Mutations
    create_companionship = CreateCompanionship.Field()
    update_companionship = UpdateCompanionship.Field()
    delete_companionship = DeleteCompanionship.Field()

    # PlantPest Mutations
    create_plant_pest = CreatePlantPest.Field()
    update_plant_pest = UpdatePlantPest.Field()
    delete_plant_pest = DeletePlantPest.Field()

    # PlantDisease Mutations
    create_plant_disease = CreatePlantDisease.Field()
    update_plant_disease = UpdatePlantDisease.Field()
    delete_plant_disease = DeletePlantDisease.Field()

    # UserContribution Mutations
    create_user_contribution = CreateUserContribution.Field()
    update_user_contribution = UpdateUserContribution.Field()
    delete_user_contribution = DeleteUserContribution.Field()
    # NEW: Approve/Reject UserContribution
    approve_contribution = ApproveContribution.Field()
    reject_contribution = RejectContribution.Field()

    # CompanionPlantingInteraction Mutations
    create_companion_interaction = CreateCompanionPlantingInteraction.Field()
    update_companion_interaction = UpdateCompanionPlantingInteraction.Field()
    delete_companion_interaction = DeleteCompanionPlantingInteraction.Field()

# --- Schema ---
# Combine Query and Mutation into a schema
schema = graphene.Schema(query=Query, mutation=Mutation)