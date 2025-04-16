from django.contrib import admin
from .models import Region, SoilProfile, Fertilizer, Pest, Disease, Plant, Seed, Companionship, PlantPest, PlantDisease, UserContribution

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'role', 'created_at')
#     search_fields = ('user__username', 'user__email')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('zone_system', 'zone_identifier', 'name', 'description') # Updated fields
    search_fields = ('name', 'description')

@admin.register(SoilProfile)
class SoilProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'soil_type', 'structure', 'drainage', 'ph_min', 'ph_max') # Updated fields
    search_fields = ('name', 'soil_type') # Updated field

@admin.register(Fertilizer)
class FertilizerAdmin(admin.ModelAdmin):
    list_display = ('fertilizer_name', 'brand', 'base_type', 'form', 'npk_ratio') # Updated fields
    search_fields = ('fertilizer_name', 'brand', 'base_type', 'form') # Updated fields

@admin.register(Pest)
class PestAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'category', 'symptoms') # Added category
    search_fields = ('common_name', 'scientific_name')

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'category', 'cause', 'symptoms') # Added category, scientific_name
    search_fields = ('common_name', 'scientific_name', 'category', 'cause') # Added scientific_name, category

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'plant_type', 'suitable_region')
    search_fields = ('common_name', 'scientific_name')

@admin.register(Seed)
class SeedAdmin(admin.ModelAdmin):
    list_display = ('seed_name', 'plant', 'variety', 'source_brand', 'seed_type', 'germination_rate_pct') # Updated fields
    search_fields = ('seed_name', 'variety', 'source_brand', 'plant__common_name', 'plant__scientific_name') # Updated fields

@admin.register(Companionship)
class CompanionshipAdmin(admin.ModelAdmin):
    list_display = ('plant_subject', 'plant_object', 'strength_confidence', 'notes') # Updated fields
    search_fields = ('plant_subject__common_name', 'plant_object__common_name', 'plant_subject__scientific_name', 'plant_object__scientific_name') # Updated fields

@admin.register(PlantPest)
class PlantPestAdmin(admin.ModelAdmin):
    list_display = ('plant', 'pest', 'notes')
    search_fields = ('plant__common_name', 'pest__common_name')

@admin.register(PlantDisease)
class PlantDiseaseAdmin(admin.ModelAdmin):
    list_display = ('plant', 'disease', 'notes')
    search_fields = ('plant__common_name', 'disease__common_name')

@admin.register(UserContribution)
class UserContributionAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity_type', 'status', 'submitted_at')
    search_fields = ('user__username', 'entity_type')
