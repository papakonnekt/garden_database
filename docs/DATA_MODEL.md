# Garden Database Data Model

This document describes the data model used in the Garden Database application. Understanding this model will help you effectively use the database and API.

## Core Entities

### Plant

The central entity representing a plant species or variety.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| common_name | String | Primary common name |
| scientific_name | String | Botanical name (Genus species) |
| description | Text | Detailed description |
| family | String | Botanical family |
| genus | String | Genus |
| species | String | Species |
| subspecies_cultivar | String | Subspecies or cultivar information |
| lifecycle_type | Enum | Annual (AN), Perennial (PE), Biennial (BI) |
| growth_habit | Enum | Vine (VI), Shrub (SH), Tree (TR), Groundcover (GC), Herbaceous (HB), Bulb (BU) |
| avg_height_inches | Integer | Average height in inches |
| avg_spread_inches | Integer | Average spread/width in inches |
| days_to_maturity_min | Integer | Minimum days to maturity |
| days_to_maturity_max | Integer | Maximum days to maturity |
| germination_period_days_min | Integer | Minimum germination period in days |
| germination_period_days_max | Integer | Maximum germination period in days |
| sunlight_requirements | Enum | Full Sun (FS), Partial Sun (PS), Shade (SH), Full Shade (FD) |
| moisture_requirements | Enum | Low (LO), Moderate (MO), High (HI), Boggy (BO) |
| soil_ph_min | Decimal | Minimum soil pH |
| soil_ph_max | Decimal | Maximum soil pH |
| temperature_tolerance_min_f | Integer | Minimum temperature tolerance (°F) |
| temperature_tolerance_max_f | Integer | Maximum temperature tolerance (°F) |
| npk_preference | String | NPK ratio preference (e.g., "5-10-10") |
| micronutrient_needs_desc | Text | Description of micronutrient needs |
| root_system_type | String | Type of root system |
| harvest_seasonality | String | Harvest season information |
| yield_estimates | Text | Estimated yield information |
| lifecycle_details | Text | Additional lifecycle information |
| common_names_list | Array | List of alternative common names |
| suitable_region | FK | Reference to Region |
| soil_preference | FK | Reference to SoilProfile |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### Seed

Information about specific seed varieties.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| seed_name | String | Name of the seed |
| plant | FK | Reference to Plant |
| variety | String | Specific variety |
| seed_type | Enum | Heirloom (H), Hybrid F1 (F1), Open-Pollinated (OP), GMO (GMO) |
| source_brand | String | Source or brand name |
| catalogue_id | String | Catalog identifier |
| germination_rate_pct | Integer | Germination rate percentage |
| viability_period_months | Integer | Viability period in months |
| storage_conditions | Text | Storage condition requirements |
| days_to_germ_min | Integer | Minimum days to germination |
| days_to_germ_max | Integer | Maximum days to germination |
| planting_depth_inches | Decimal | Recommended planting depth |
| spacing_inches | Integer | Recommended spacing |
| optimal_planting_season | String | Best season for planting |
| recommended_conditions | Text | Recommended growing conditions |
| sowing_instructions_text | Text | Detailed sowing instructions |
| packet_info | JSON | Additional packet information |
| description | Text | General description |
| image_url | URL | Image URL |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### Pest

Information about garden pests.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| common_name | String | Common name |
| scientific_name | String | Scientific name |
| description | Text | Detailed description |
| category | Enum | Insect (INS), Mammal (MAM), Mollusk (MOL), Other (OTH) |
| symptoms | Text | Plant damage symptoms |
| damage_type | String | Type of damage caused |
| severity_level | Enum | Low (LOW), Medium (MED), High (HIG) |
| control_methods | Text | Control strategies |
| prevention_methods | Text | Prevention strategies |
| organic_control_options | Text | Organic control methods |
| chemical_control_options | Text | Chemical control options |
| natural_predators | Text | Natural enemies |
| lifecycle_stage | String | Most damaging lifecycle stage |
| size_mm | Decimal | Average size in millimeters |
| color | String | Primary color or pattern |
| identification_tips | Text | Identification guidance |
| active_seasons | Array | Active seasons |
| peak_activity_time | String | Peak activity period |
| geographic_distribution | Text | Geographic distribution |
| habitat_preference | Text | Preferred habitat |
| additional_notes | Text | Additional information |
| plants | M2M | Many-to-many relationship with Plant |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### Disease

Information about plant diseases.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| common_name | String | Common name |
| scientific_name | String | Scientific name |
| description | Text | Detailed description |
| category | Enum | Fungal (FUN), Bacterial (BAC), Viral (VIR), Nematode (NEM), Other (OTH) |
| cause | String | Causal agent |
| cause_details | Text | Detailed cause information |
| symptoms | Text | Symptoms description |
| diagnostic_methods | Text | Methods for diagnosis |
| severity_level | Enum | Low (LOW), Medium (MED), High (HIG) |
| disease_cycle | Text | Disease lifecycle information |
| transmission_methods | Text | How the disease spreads |
| survival_conditions | Text | Conditions for pathogen survival |
| control_methods | Text | Control strategies |
| prevention_methods | Text | Prevention strategies |
| organic_control_options | Text | Organic control methods |
| chemical_control_options | Text | Chemical control options |
| resistant_varieties | Text | Disease-resistant varieties |
| favorable_conditions | Text | Conditions that favor disease |
| temperature_range | String | Optimal temperature range |
| humidity_preference | String | Humidity requirements |
| geographic_distribution | Text | Geographic distribution |
| first_reported | String | When/where first reported |
| economic_impact | Text | Economic impact information |
| additional_notes | Text | Additional information |
| plants | M2M | Many-to-many relationship with Plant |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### Fertilizer

Information about fertilizers.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| fertilizer_name | String | Name of the fertilizer |
| description | Text | Detailed description |
| fertilizer_type | String | Type of fertilizer |
| npk_ratio | String | NPK ratio (e.g., "10-10-10") |
| nitrogen_pct | Decimal | Percentage of nitrogen |
| phosphorus_pct | Decimal | Percentage of phosphorus |
| potassium_pct | Decimal | Percentage of potassium |
| micronutrients | JSON | Micronutrient content |
| organic | Boolean | Whether it's organic |
| source_materials | Array | Source materials |
| application_method | String | How to apply |
| application_rate | String | Recommended application rate |
| application_frequency | String | How often to apply |
| suitable_plants | Array | Plants this fertilizer is good for |
| best_season | String | Best season to apply |
| ph_effect | String | Effect on soil pH |
| release_rate | String | Nutrient release rate |
| environmental_impact | Text | Environmental considerations |
| storage_requirements | Text | Storage information |
| safety_precautions | Text | Safety information |
| manufacturer | String | Manufacturer name |
| price_range | String | Approximate cost |
| additional_notes | Text | Additional information |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### Region

Information about growing regions and zones.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| zone_system | String | Zone system name (e.g., "USDA") |
| zone_identifier | String | Zone identifier (e.g., "7a") |
| description | Text | Description of the region |
| avg_min_temp_f | Integer | Average minimum temperature (°F) |
| avg_max_temp_f | Integer | Average maximum temperature (°F) |
| frost_free_days | Integer | Average frost-free days |
| annual_rainfall_inches | Decimal | Annual rainfall in inches |
| geographic_area | Text | Geographic area description |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### SoilProfile

Information about soil types.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| name | String | Soil profile name |
| description | Text | Detailed description |
| soil_type | String | Type of soil |
| texture | String | Soil texture |
| drainage_rate | String | Drainage characteristics |
| water_retention | String | Water retention characteristics |
| ph_min | Decimal | Minimum pH |
| ph_max | Decimal | Maximum pH |
| organic_matter_pct | Decimal | Percentage of organic matter |
| fertility_level | String | Fertility level |
| composition | JSON | Soil composition details |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

## Relationship Entities

### Companionship

Represents companion planting relationships between plants.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| plant_subject | FK | Reference to first Plant |
| plant_object | FK | Reference to second Plant |
| interactions | M2M | Many-to-many relationship with CompanionPlantingInteraction |
| notes | Text | Additional notes about the relationship |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### CompanionPlantingInteraction

Describes specific interactions in companion planting.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| interaction_type | Enum | Beneficial (BEN), Detrimental (DET), Neutral (NEU) |
| mechanism_description | Text | Description of how the interaction works |
| interaction_code | String | Unique code for the interaction |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### PlantPest

Junction table for plant-pest relationships.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| plant | FK | Reference to Plant |
| pest | FK | Reference to Pest |
| severity | Enum | Low (LOW), Medium (MED), High (HIG) |
| notes | Text | Additional notes |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

### PlantDisease

Junction table for plant-disease relationships.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| plant | FK | Reference to Plant |
| disease | FK | Reference to Disease |
| severity | Enum | Low (LOW), Medium (MED), High (HIG) |
| notes | Text | Additional notes |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

## User Contribution

### UserContribution

Tracks user contributions to the database.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| user | FK | Reference to User (nullable) |
| entity_type | String | Type of entity being contributed |
| entity_id | UUID | ID of the entity (if existing) |
| proposed_data | JSON | JSON data containing the proposed changes |
| status | Enum | Pending, Approved, Rejected |
| reviewed_by | FK | Reference to User who reviewed |
| review_notes | Text | Notes from the reviewer |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| version | Integer | Version number |

## Entity Relationships Diagram

```
Plant ─────┬───── Seed
           │
           ├───── PlantPest ───── Pest
           │
           ├───── PlantDisease ── Disease
           │
           ├───── Companionship ─ Plant
           │
           ├───── Region
           │
           └───── SoilProfile

Companionship ── CompanionPlantingInteraction

UserContribution ── User
```

## Notes on Data Types

- **UUID**: Universally Unique Identifier
- **FK**: Foreign Key reference to another entity
- **M2M**: Many-to-Many relationship
- **Enum**: Enumerated type with specific allowed values
- **JSON**: JSON-formatted data
- **Array**: List of values
- **DateTime**: Date and time timestamp
