from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Region, SoilProfile, Plant, Fertilizer, Pest, Disease, Seed, Companionship, PlantPest, PlantDisease, UserContribution, CompanionPlantingInteraction

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class SoilProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilProfile
        fields = '__all__'

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = '__all__'


class PestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pest
        fields = '__all__'


class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'
class CompanionPlantingInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanionPlantingInteraction
        fields = '__all__'




class CompanionshipDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Companionship details, focusing on the object plant
    and the interactions for use within PlantDetailSerializer.
    """
    # Use PlantSerializer to represent the companion plant (plant_object)
    plant_object = PlantSerializer(read_only=True)
    # Use CompanionPlantingInteractionSerializer for the interactions M2M field
    interactions = CompanionPlantingInteractionSerializer(many=True, read_only=True)

    class Meta:
        model = Companionship
        # Fields relevant when viewing from the subject plant's perspective
        fields = ['id', 'plant_object', 'interactions', 'strength_confidence', 'notes']
class PlantDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a Plant, including related objects.
    """
    # Nested serializers for ForeignKey relationships
    soil_preference = SoilProfileSerializer(read_only=True)
    suitable_region = RegionSerializer(read_only=True)

    # Nested serializers for ManyToMany relationships
    pests = PestSerializer(many=True, read_only=True)
    diseases = DiseaseSerializer(many=True, read_only=True)

    # Use the custom CompanionshipDetailSerializer for the 'subject' side of the relationship
    # This shows plants that *this* plant is a companion *to* (or has a relationship *with*)
    companion_relationships_subject = CompanionshipDetailSerializer(many=True, read_only=True)

    # We might also want to show plants that are companions *to this* plant.
    # This uses the 'related_name' from the Companionship model's plant_object field.
    companion_relationships_object = CompanionshipDetailSerializer(many=True, read_only=True)


    class Meta:
        model = Plant
        # Include all fields from the Plant model plus the nested relationships
        fields = [
            # Plant model fields (explicitly list or use '__all__' carefully)
            'id', 'scientific_name', 'common_name', 'common_names_list', 'family',
            'genus', 'species', 'subspecies_cultivar', 'description',
            'lifecycle_type', 'lifecycle_details', 'plant_type', 'growth_habit',
            'soil_ph_min', 'soil_ph_max', 'moisture_requirements',
            'sunlight_requirements', 'temperature_tolerance_min_f',
            'temperature_tolerance_max_f', 'npk_preference',
            'growth_stage_specific_npk', 'micronutrient_needs_desc',
            'variant_details', 'avg_height_inches', 'avg_spread_inches',
            'root_system_type', 'additional_morphological_traits',
            'germination_period_days_min', 'germination_period_days_max',
            'days_to_maturity_min', 'days_to_maturity_max', 'yield_estimates',
            'harvest_seasonality', 'image_url', 'version', 'created_at', 'updated_at',
            # Nested related fields
            'soil_preference',
            'suitable_region',
            'pests',
            'diseases',
            'companion_relationships_subject', # Relationships where this plant is the subject
            'companion_relationships_object', # Relationships where this plant is the object
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id']

# class UserProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)
#
#     class Meta:
#         model = UserProfile
#         fields = '__all__'

class FertilizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fertilizer
        fields = '__all__'


class SeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seed
        fields = '__all__'

class CompanionshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companionship
        fields = '__all__'



class PlantPestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantPest
        fields = '__all__'

class PlantDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantDisease
        fields = '__all__'

class UserContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContribution
        fields = '__all__'

