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

class PestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pest
        fields = '__all__'

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
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

class CompanionPlantingInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanionPlantingInteraction
        fields = '__all__'