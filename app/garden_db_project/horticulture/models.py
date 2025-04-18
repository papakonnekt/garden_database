import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
# Remove direct import of User, use settings.AUTH_USER_MODEL instead
# from django.contrib.auth.models import User

# Use Django's built-in User model and create a profile model
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     role = models.CharField(max_length=50, default='user', null=False, blank=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.user.username

class Region(models.Model): # Represents a climatic zone or region (PRD 2.5)
    id = models.BigAutoField(primary_key=True)
    # Name field might be redundant if zone_system + zone_identifier is unique, but keep for now.
    name = models.CharField(max_length=100, blank=True, null=True, help_text="Optional descriptive name for the region/zone")
    zone_system = models.CharField(max_length=50, null=False, blank=False, default="USDA Hardiness Zones", help_text="The zoning system used (e.g., 'USDA Hardiness Zones')") # Added
    zone_identifier = models.CharField(max_length=20, null=False, blank=False, default="Unknown", help_text="The specific zone identifier within the system (e.g., '7a', '9b')")
    description = models.TextField(blank=True, null=True, help_text="Description of the zone (e.g., 'Average minimum winter temperature 0 to 5 °F')")
    # Removed first_frost_avg and last_frost_avg as per PRD 2.5 focus on zone definition
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('zone_system', 'zone_identifier') # Ensure combination is unique
        verbose_name = "Climatic Region/Zone"
        verbose_name_plural = "Climatic Regions/Zones"

    def __str__(self):
        return f"{self.zone_system} - {self.zone_identifier}" # Updated __str__

class SoilProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False, default="Default Soil Profile", help_text="Unique name for the soil profile (e.g., 'Generic Clay Loam')")

    # Soil Characteristics (PRD 2.5)
    class SoilType(models.TextChoices):
        CLAY = 'CL', 'Clay'
        SANDY = 'SA', 'Sandy'
        SILTY = 'SI', 'Silty'
        LOAM = 'LO', 'Loam'
        PEATY = 'PE', 'Peaty'
        CHALKY = 'CH', 'Chalky'
        UNKNOWN = 'UNK', 'Unknown'
    soil_type = models.CharField(max_length=3, choices=SoilType.choices, blank=True, null=True) # Renamed from 'type'

    class SoilStructure(models.TextChoices):
        GRANULAR = 'GR', 'Granular'
        BLOCKY = 'BL', 'Blocky'
        PLATY = 'PL', 'Platy'
        MASSIVE = 'MA', 'Massive'
        SINGLE_GRAINED = 'SG', 'Single-grained'
        UNKNOWN = 'UNK', 'Unknown'
    structure = models.CharField(max_length=3, choices=SoilStructure.choices, blank=True, null=True) # Added

    ph_min = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Typical minimum pH value") # Kept min/max for range
    ph_max = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Typical maximum pH value") # Kept min/max for range

    class SoilDrainage(models.TextChoices):
        POOR = 'PO', 'Poor'
        MODERATE = 'MO', 'Moderate'
        GOOD = 'GO', 'Good'
        EXCESSIVE = 'EX', 'Excessive'
        UNKNOWN = 'UNK', 'Unknown'
    drainage = models.CharField(max_length=3, choices=SoilDrainage.choices, blank=True, null=True) # Added

    class SoilMoistureRetention(models.TextChoices):
        LOW = 'LO', 'Low'
        MEDIUM = 'ME', 'Medium'
        HIGH = 'HI', 'High'
        UNKNOWN = 'UNK', 'Unknown'
    moisture_retention = models.CharField(max_length=3, choices=SoilMoistureRetention.choices, blank=True, null=True) # Added

    class SoilOrganicMatter(models.TextChoices):
        LOW = 'LO', 'Low'
        MEDIUM = 'ME', 'Medium'
        HIGH = 'HI', 'High'
        UNKNOWN = 'UNK', 'Unknown'
    # PRD allows float % too, sticking to enum for now for simplicity
    organic_matter_content = models.CharField(max_length=3, choices=SoilOrganicMatter.choices, blank=True, null=True) # Added

    # Removed nutrient_levels and amendments_rec as they are not explicitly in PRD 2.5 for SoilProfile itself
    description = models.TextField(blank=True, null=True, help_text="General description of the soil profile") # Added for context

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Fertilizer(models.Model):
    id = models.BigAutoField(primary_key=True)

    # Fertilizer Identification (PRD 2.3)
    fertilizer_name = models.CharField(max_length=150, null=False, blank=False, default="Unknown Fertilizer", help_text="Name of the fertilizer")
    brand = models.CharField(max_length=100, blank=True, null=True) # Added

    class FertilizerBaseType(models.TextChoices):
        ORGANIC = 'ORG', 'Organic'
        SYNTHETIC = 'SYN', 'Synthetic'
        MINERAL = 'MIN', 'Mineral' # Added possibility
        UNKNOWN = 'UNK', 'Unknown'
    base_type = models.CharField(max_length=3, choices=FertilizerBaseType.choices, blank=True, null=True)

    class FertilizerForm(models.TextChoices):
        LIQUID = 'LIQ', 'Liquid'
        GRANULAR = 'GRA', 'Granular'
        POWDER = 'POW', 'Powder'
        SLOW_RELEASE = 'SLO', 'Slow-Release'
        FOLIAR = 'FOL', 'Foliar'
        SPIKE = 'SPI', 'Spike'
        UNKNOWN = 'UNK', 'Unknown'
    form = models.CharField(max_length=3, choices=FertilizerForm.choices, blank=True, null=True)

    # Nutrient Content (PRD 2.3)
    npk_ratio = models.CharField(max_length=30, blank=True, null=True, help_text="NPK ratio as string (e.g., '10-10-10', '5-2-3+Fe')") # Increased length
    # Removed individual NPK percentage fields
    micronutrient_composition = models.JSONField(default=list, blank=True, help_text="Array of objects for micronutrients, e.g., [{'nutrient': 'Iron (Fe)', 'value': 0.5, 'unit': '%'}]") # Added

    # Usage Recommendations (PRD 2.3)
    application_rate = models.JSONField(default=list, blank=True, help_text="Array of objects for application rates, e.g., [{'value': 1, 'unit': 'oz/gallon', 'context': 'foliar spray'}]") # Added
    application_timing_frequency = models.TextField(blank=True, null=True, help_text="Recommended timing/frequency (e.g., 'Every 2 weeks during growing season')") # Added
    recommended_for = models.TextField(blank=True, null=True, help_text="Recommended plant types or stages (e.g., 'Acid-loving plants', 'Vegetable gardens')") # Added
    compatibility_notes = models.TextField(blank=True, null=True, help_text="Compatibility issues (e.g., 'Do not mix with X')") # Added
    # Removed old usage_instructions field

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fertilizer_name

# Shared Category Enum for Pests & Diseases (PRD 2.5)
class ProblemCategory(models.TextChoices):
    FUNGAL = 'FUN', 'Fungal'
    BACTERIAL = 'BAC', 'Bacterial'
    INSECT = 'INS', 'Insect'
    VIRAL = 'VIR', 'Viral'
    DEFICIENCY = 'DEF', 'Nutrient Deficiency'
    MAMMAL = 'MAM', 'Mammal'
    MOLLUSK = 'MOL', 'Mollusk'
    ENVIRONMENTAL = 'ENV', 'Environmental'
    OTHER = 'OTH', 'Other'
    UNKNOWN = 'UNK', 'Unknown'

class Pest(models.Model):
    id = models.BigAutoField(primary_key=True)
    common_name = models.CharField(max_length=100, unique=True, null=False, blank=False, default="Unknown Pest", help_text="Common name of the pest")
    scientific_name = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=3, choices=ProblemCategory.choices, default=ProblemCategory.INSECT, help_text="Category of the pest") # Added category
    description = models.TextField(blank=True, null=True, help_text="Description of the pest, lifecycle, etc.") # Added help_text
    symptoms = models.TextField(blank=True, null=True, help_text="Symptoms caused by the pest") # Added help_text
    treatment_strategies = models.JSONField(default=list, blank=True, help_text="Array of treatment strategies (organic and conventional)") # Replaces control fields
    prevention_strategies = models.JSONField(default=list, blank=True, help_text="Array of prevention strategies") # Added
    image_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.common_name

class Disease(models.Model):
    id = models.BigAutoField(primary_key=True)
    common_name = models.CharField(max_length=100, unique=True, null=False, blank=False, default="Unknown Disease", help_text="Common name of the disease")
    scientific_name = models.CharField(max_length=100, blank=True, null=True, help_text="Optional scientific name (e.g., for fungus/bacteria)") # Added
    category = models.CharField(max_length=3, choices=ProblemCategory.choices, blank=True, null=True, help_text="Category of the disease") # Added category
    # cause field might be redundant if category is used, but keeping for now as PRD had it. Could store specific agent name here.
    cause = models.CharField(max_length=100, blank=True, null=True, help_text="Specific cause if known (e.g., 'Alternaria solani')")
    description = models.TextField(blank=True, null=True, help_text="Description of the disease") # Added help_text
    symptoms = models.TextField(blank=True, null=True, help_text="Symptoms caused by the disease") # Added help_text
    treatment_strategies = models.JSONField(default=list, blank=True, help_text="Array of treatment strategies (organic and conventional)") # Replaces control fields
    prevention_strategies = models.JSONField(default=list, blank=True, help_text="Array of prevention strategies") # Added
    conditions_favoring = models.TextField(blank=True, null=True, help_text="Conditions favoring disease development")
    geographic_distribution = models.TextField(blank=True, null=True, help_text="Geographic distribution of the disease")
    transmission_methods = models.JSONField(default=list, blank=True, help_text="Array of transmission methods")
    image_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.common_name

class Plant(models.Model):
    id = models.BigAutoField(primary_key=True)
    # Identification (PRD 2.1)
    scientific_name = models.CharField(max_length=255, unique=True, null=False, blank=False, default="Unknown Species", help_text="Unique scientific name (Genus species)")
    common_name = models.CharField(max_length=150, null=False, blank=False, default="Unknown Plant", help_text="Primary common name")
    common_names_list = models.JSONField(default=list, blank=True, help_text="Array of alternative common names")
    family = models.CharField(max_length=100, blank=True, null=True)
    genus = models.CharField(max_length=100, blank=True, null=True)
    species = models.CharField(max_length=100, blank=True, null=True)
    subspecies_cultivar = models.CharField(max_length=100, blank=True, null=True, help_text="Subspecies or cultivar name, if applicable")
    description = models.TextField(blank=True, null=True) # General description

    # Lifecycle Classification (PRD 2.1)
    class LifecycleType(models.TextChoices):
        ANNUAL = 'AN', 'Annual'
        PERENNIAL = 'PE', 'Perennial'
        BIENNIAL = 'BI', 'Biennial'
    lifecycle_type = models.CharField(max_length=2, choices=LifecycleType.choices, blank=True, null=True)
    lifecycle_details = models.TextField(blank=True, null=True, help_text="Optional descriptive text about lifecycle")

    # Growth Form (PRD 2.1)
    class GrowthHabitType(models.TextChoices):
        VINE = 'VI', 'Vine'
        SHRUB = 'SH', 'Shrub'
        TREE = 'TR', 'Tree'
        GROUNDCOVER = 'GC', 'Groundcover'
        HERBACEOUS = 'HB', 'Herbaceous'
        BULB = 'BU', 'Bulb'
    plant_type = models.CharField(max_length=50, blank=True, null=True, help_text="General type like Vegetable, Herb, Flower") # Keep for general categorization? PRD doesn't explicitly list this.

    # Environmental Requirements (PRD 2.1)
    soil_preference = models.ForeignKey(SoilProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='preferred_by_plants', help_text="Link to preferred general soil profile(s)") # Changed related_name
    # PRD specifies preferred_types (array[string]) and ph_range (object) within soil object.
    # Representing pH range directly on Plant model for now. Preferred types could be handled via ManyToMany to SoilProfile or a JSON field if needed.
    soil_ph_min = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Minimum preferred soil pH")
    soil_ph_max = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Maximum preferred soil pH")

    class MoistureRequirements(models.TextChoices):
        LOW = 'LO', 'Low'
        MODERATE = 'MO', 'Moderate'
        HIGH = 'HI', 'High'
        BOGGY = 'BO', 'Boggy'
    moisture_requirements = models.CharField(max_length=2, choices=MoistureRequirements.choices, blank=True, null=True)

    class SunlightRequirements(models.TextChoices):
        FULL_SUN = 'FS', 'Full Sun'
        PARTIAL_SUN = 'PS', 'Partial Sun' # Often used interchangeably with Partial Shade
        PARTIAL_SHADE = 'SH', 'Partial Shade'
        FULL_SHADE = 'FD', 'Full Shade'
    sunlight_requirements = models.CharField(max_length=2, choices=SunlightRequirements.choices, blank=True, null=True)
    # Removed old sun_exposure field

    temperature_tolerance_min_f = models.IntegerField(blank=True, null=True, help_text="Minimum hardy temperature in Fahrenheit")
    temperature_tolerance_max_f = models.IntegerField(blank=True, null=True, help_text="Maximum hardy temperature in Fahrenheit")

    # Nutrient Requirements (PRD 2.1)
    npk_preference = models.CharField(max_length=100, blank=True, null=True, help_text="Base NPK needs (e.g., '5-10-5', 'High N, Moderate P, Low K')") # Adjusted max_length again
    growth_stage_specific_npk = models.JSONField(default=dict, blank=True, help_text="Object for stage-specific NPK needs, e.g., {'seedling': '...', 'vegetative': '...'}")
    micronutrient_needs_desc = models.TextField(blank=True, null=True, help_text="Descriptive micronutrient needs (e.g., 'Sensitive to boron deficiency')")
    growth_habit = models.CharField(max_length=2, choices=GrowthHabitType.choices, blank=True, null=True)

    # Morphological Traits (PRD 2.1)
    variant_details = models.JSONField(default=list, blank=True, help_text="Array of objects describing variants, e.g., [{'variant_type': 'Determinate', 'description': '...'}]")
    avg_height_inches = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Typical mature height range in inches")
    avg_spread_inches = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Typical mature lateral spread range in inches")
    root_system_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Shallow Fibrous, Deep Taproot")
    additional_morphological_traits = models.JSONField(default=dict, blank=True, help_text="Object for additional traits like {'leaf_type': '...', 'stem_characteristics': '...', 'branching_pattern': '...'}")
    # Growth & Harvest Data (PRD 2.1)
    germination_period_days_min = models.IntegerField(blank=True, null=True, help_text="Typical minimum days for germination")
    germination_period_days_max = models.IntegerField(blank=True, null=True, help_text="Typical maximum days for germination")
    days_to_maturity_min = models.IntegerField(blank=True, null=True, help_text="Minimum days from seed/transplant to first harvest/flowering")
    days_to_maturity_max = models.IntegerField(blank=True, null=True, help_text="Maximum days from seed/transplant to first harvest/flowering")
    yield_estimates = models.TextField(blank=True, null=True, help_text="Descriptive yield estimates (e.g., 'lbs per plant', 'fruits per sq ft')")
    harvest_seasonality = models.TextField(blank=True, null=True, help_text="Typical harvest season (e.g., 'Early Summer', 'Fall', 'Year-round zones 9+')")
    image_url = models.URLField(max_length=255, blank=True, null=True)
    suitable_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name='plants')
    version = models.IntegerField(default=1, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ManyToMany relationships defined below using through models
    pests = models.ManyToManyField(Pest, through='PlantPest', related_name='plants')
    diseases = models.ManyToManyField(Disease, through='PlantDisease', related_name='plants')
    companions = models.ManyToManyField(
        'self',
        through='Companionship',
        symmetrical=False,
        related_name='companion_to'
    )

    def __str__(self):
        return f"{self.common_name} ({self.scientific_name})"

class Seed(models.Model):
    id = models.BigAutoField(primary_key=True)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, null=True, related_name='seeds', help_text="The plant species this seed belongs to")

    # Seed Identification (PRD 2.2)
    seed_name = models.CharField(max_length=150, null=False, blank=False, default="Unknown Seed", help_text="Specific seed name, often includes variety (e.g., 'Beefsteak Tomato Seeds')")
    variety = models.CharField(max_length=100, blank=True, null=True, help_text="Specific variety name (e.g., 'Beefsteak')") # Added
    source_brand = models.CharField(max_length=100, blank=True, null=True, help_text="Source or brand of the seeds") # Renamed from source
    catalogue_id = models.CharField(max_length=50, blank=True, null=True, help_text="Optional catalogue ID from the source") # Added
    description = models.TextField(blank=True, null=True) # General description

    # Seed Attributes (PRD 2.2)
    germination_rate_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Expected germination rate percentage")
    viability_period_months = models.IntegerField(blank=True, null=True, help_text="Typical viability period in months under optimal storage") # Added
    storage_conditions = models.TextField(blank=True, null=True, help_text="Recommended storage conditions (e.g., 'Cool, dark, dry place')") # Added

    class SeedType(models.TextChoices):
        HEIRLOOM = 'H', 'Heirloom'
        HYBRID = 'F1', 'Hybrid (F1)'
        OPEN_POLLINATED = 'OP', 'Open-Pollinated'
        GMO = 'GMO', 'Genetically Modified'
        UNKNOWN = 'UNK', 'Unknown'
    seed_type = models.CharField(max_length=3, choices=SeedType.choices, blank=True, null=True) # Added

    # Usage Data (PRD 2.2)
    optimal_planting_season = models.TextField(blank=True, null=True, help_text="Recommended planting season(s) (e.g., 'Spring after last frost')") # Added
    days_to_germ_min = models.IntegerField(blank=True, null=True, help_text="Minimum days to germination")
    days_to_germ_max = models.IntegerField(blank=True, null=True, help_text="Maximum days to germination")
    # Sowing Instructions
    planting_depth_inches = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Recommended planting depth in inches")
    spacing_inches = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Recommended spacing between plants in inches")
    sowing_instructions_text = models.TextField(blank=True, null=True, help_text="Detailed sowing instructions") # Added
    recommended_conditions = models.TextField(blank=True, null=True, help_text="Special conditions (e.g., 'Requires light for germination', 'Needs scarification')") # Added

    packet_info = models.JSONField(blank=True, null=True, help_text="Other info from packet (e.g., year packed, quantity, lot number)") # Updated help text
    image_url = models.URLField(max_length=255, blank=True, null=True)
    version = models.IntegerField(default=1, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.seed_name} ({self.plant.common_name})" # Updated __str__


# Companion Planting Interaction Definitions (PRD 2.4)
class CompanionPlantingInteraction(models.Model):
    id = models.BigAutoField(primary_key=True)
    interaction_code = models.CharField(max_length=100, unique=True, null=False, blank=False, default="DEFAULT_CODE", help_text="Unique code, e.g., PEST_REPEL_APHID")

    class InteractionType(models.TextChoices):
        BENEFICIAL = 'BEN', 'Beneficial'
        DETRIMENTAL = 'DET', 'Detrimental'
        NEUTRAL = 'NEU', 'Neutral'
    interaction_type = models.CharField(max_length=3, choices=InteractionType.choices, null=False, blank=False, default=InteractionType.NEUTRAL, help_text="Type of interaction (beneficial, detrimental, neutral)")

    mechanism_description = models.TextField(blank=True, null=True, help_text="Explanation of how the interaction works")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.interaction_code} ({self.get_interaction_type_display()})"

    class Meta:
        verbose_name = "Companion Planting Interaction"
        verbose_name_plural = "Companion Planting Interactions"

# --- Junction / Through Models ---

class Companionship(models.Model): # Represents a specific pairing instance between two plants
    id = models.BigAutoField(primary_key=True) # Add explicit primary key
    plant_subject = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='companion_relationships_subject', null=True, blank=True, help_text="The plant this relationship originates from")
    plant_object = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='companion_relationships_object', null=True, blank=True, help_text="The plant this relationship targets")

    # Link to defined interaction types/reasons (PRD 2.1 / 2.4)
    # A single pairing can have multiple reasons (e.g., repels aphids AND attracts pollinators)
    interactions = models.ManyToManyField(CompanionPlantingInteraction, related_name='plant_pairings', help_text="Specific interaction mechanisms (reason codes)")

    class StrengthConfidence(models.TextChoices):
        HIGH = 'HI', 'High'
        MEDIUM = 'ME', 'Medium'
        LOW = 'LO', 'Low'
        ANECDOTAL = 'AN', 'Anecdotal'
    strength_confidence = models.CharField(max_length=2, choices=StrengthConfidence.choices, blank=True, null=True)

    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this specific pairing") # Renamed from description
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # unique_together = ('plant_subject', 'plant_object') # A subject->object pair can exist multiple times if different interactions apply? Or should interactions be the M2M link?
        # Let's assume a direct pairing is unique, and interactions detail the reasons.
        unique_together = ('plant_subject', 'plant_object')
        verbose_name = "Companionship"
        verbose_name_plural = "Companionships"

    def __str__(self):
        # Improve __str__ later if needed, maybe list interaction codes
        return f"{self.plant_subject} -> {self.plant_object} ({self.strength_confidence or 'N/A'})"

class PlantPest(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    pest = models.ForeignKey(Pest, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('plant', 'pest')
        verbose_name = "Plant Pest"
        verbose_name_plural = "Plant Pests"

    def __str__(self):
        return f"{self.plant} susceptible to {self.pest}"

class PlantDisease(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('plant', 'disease')
        verbose_name = "Plant Disease"
        verbose_name_plural = "Plant Diseases"

    def __str__(self):
        return f"{self.plant} susceptible to {self.disease}"

# --- User Contributions ---

class UserContribution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='contributions')
    entity_type = models.CharField(max_length=50, null=False, blank=False, default="plant", help_text="Type of entity being contributed (e.g., 'plant', 'seed', 'tip')")
    entity_id = models.CharField(max_length=50, null=True, blank=True) # ID of existing entity if modifying
    proposed_data = models.JSONField(null=False, default=dict, help_text="JSON data containing the proposed changes or additions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', null=False, blank=False, help_text="Current status of the contribution")
    admin_notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now) # Use default=timezone.now for submission time
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_contributions')

    def __str__(self):
        return f"Contribution {self.id} by {self.user.username} ({self.status})"
