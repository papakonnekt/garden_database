from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Plant, SoilProfile, Region

User = get_user_model()

class PlantModelTests(TestCase):
    """Tests for the Plant model."""
    
    def setUp(self):
        """Set up test data."""
        self.soil_profile = SoilProfile.objects.create(
            name="Test Loam Soil",
            soil_type="LO",
            structure="GR",
            drainage="GO",
            moisture_retention="ME",
            organic_matter_content="ME",
            ph_min=6.0,
            ph_max=7.0
        )
        
        self.region = Region.objects.create(
            zone_system="USDA",
            zone_identifier="7b",
            description="Test region"
        )
        
    def test_plant_creation(self):
        """Test creating a Plant instance with required fields."""
        plant = Plant.objects.create(
            scientific_name="Solanum lycopersicum",
            common_name="Tomato",
            lifecycle_type="AN",
            growth_habit="VI",
            moisture_requirements="MO",
            sunlight_requirements="FS",
            soil_preference=self.soil_profile,
            suitable_region=self.region
        )
        
        retrieved_plant = Plant.objects.get(pk=plant.pk)
        self.assertEqual(retrieved_plant.scientific_name, "Solanum lycopersicum")
        self.assertEqual(retrieved_plant.common_name, "Tomato")
        self.assertEqual(retrieved_plant.lifecycle_type, "AN")
        self.assertEqual(retrieved_plant.growth_habit, "VI")
        self.assertEqual(retrieved_plant.moisture_requirements, "MO")
        self.assertEqual(retrieved_plant.sunlight_requirements, "FS")
        self.assertEqual(retrieved_plant.soil_preference, self.soil_profile)
        self.assertEqual(retrieved_plant.suitable_region, self.region)
        
    def test_plant_str_method(self):
        """Test the __str__ method of the Plant model."""
        plant = Plant.objects.create(
            scientific_name="Solanum lycopersicum",
            common_name="Tomato"
        )
        self.assertEqual(str(plant), "Tomato (Solanum lycopersicum)")
        
    def test_plant_json_fields(self):
        """Test JSON fields in the Plant model."""
        plant = Plant.objects.create(
            scientific_name="Solanum lycopersicum",
            common_name="Tomato",
            common_names_list=["Tomato", "Love Apple"],
            variant_details=[
                {"variant_type": "Determinate", "description": "Bush type with limited growth"}
            ],
            additional_morphological_traits={
                "leaf_type": "Compound",
                "stem_characteristics": "Hairy",
                "branching_pattern": "Sympodial"
            },
            growth_stage_specific_npk={
                "seedling": "High N, Low P, Low K",
                "vegetative": "Medium N, Medium P, Medium K",
                "flowering": "Low N, High P, Medium K",
                "fruiting": "Low N, Medium P, High K"
            }
        )
        
        retrieved_plant = Plant.objects.get(pk=plant.pk)
        self.assertEqual(len(retrieved_plant.common_names_list), 2)
        self.assertEqual(retrieved_plant.common_names_list[0], "Tomato")
        self.assertEqual(retrieved_plant.common_names_list[1], "Love Apple")
        
        self.assertEqual(len(retrieved_plant.variant_details), 1)
        self.assertEqual(retrieved_plant.variant_details[0]["variant_type"], "Determinate")
        
        self.assertEqual(retrieved_plant.additional_morphological_traits["leaf_type"], "Compound")
        self.assertEqual(retrieved_plant.additional_morphological_traits["stem_characteristics"], "Hairy")
        
        self.assertEqual(retrieved_plant.growth_stage_specific_npk["seedling"], "High N, Low P, Low K")
        self.assertEqual(retrieved_plant.growth_stage_specific_npk["fruiting"], "Low N, Medium P, High K")


class PlantAPITests(APITestCase):
    """Tests for the Plant API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Create users
        cls.admin_user = User.objects.create_user(
            username='testadmin_plantapi',
            password='password123',
            email='admin_plant@example.com',
            role='admin'
        )
        
        cls.regular_user = User.objects.create_user(
            username='testuser_plantapi',
            password='password123',
            email='user_plant@example.com',
            role='user'
        )
        
        # Create a soil profile and region for foreign key relationships
        cls.soil_profile = SoilProfile.objects.create(
            name="API Test Soil",
            soil_type="SA"
        )
        
        cls.region = Region.objects.create(
            zone_system="USDA",
            zone_identifier="6a"
        )
        
        # Create a sample plant
        cls.plant1 = Plant.objects.create(
            scientific_name="Lactuca sativa",
            common_name="Lettuce",
            lifecycle_type="AN",
            soil_preference=cls.soil_profile,
            suitable_region=cls.region
        )
        
        cls.list_url = reverse('plant-list')
        cls.detail_url = reverse('plant-detail', kwargs={'pk': cls.plant1.pk})
    
    def test_list_plants_unauthenticated(self):
        """Test listing plants without authentication (should be allowed)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['scientific_name'], self.plant1.scientific_name)
    
    def test_retrieve_plant_unauthenticated(self):
        """Test retrieving a specific plant without authentication."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['scientific_name'], self.plant1.scientific_name)
        self.assertEqual(response.data['common_name'], self.plant1.common_name)
    
    def test_create_plant_unauthenticated(self):
        """Test creating a plant without authentication (should be unauthorized)."""
        data = {
            'scientific_name': 'Brassica oleracea',
            'common_name': 'Cabbage',
            'lifecycle_type': 'BI'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Plant.objects.count(), 1)  # No new plant created
    
    def test_create_plant_as_admin(self):
        """Test creating a plant as an admin user."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'scientific_name': 'Brassica oleracea',
            'common_name': 'Cabbage',
            'lifecycle_type': 'BI',
            'soil_preference': self.soil_profile.id,
            'suitable_region': self.region.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plant.objects.count(), 2)
        self.assertTrue(Plant.objects.filter(scientific_name='Brassica oleracea').exists())
    
    def test_update_plant_as_admin(self):
        """Test updating a plant as an admin user."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'common_name': 'Romaine Lettuce',
            'description': 'A variety of lettuce with long, sturdy leaves'
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plant1.refresh_from_db()
        self.assertEqual(self.plant1.common_name, 'Romaine Lettuce')
        self.assertEqual(self.plant1.description, 'A variety of lettuce with long, sturdy leaves')
    
    def test_delete_plant_as_admin(self):
        """Test deleting a plant as an admin user."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Plant.objects.count(), 0)
