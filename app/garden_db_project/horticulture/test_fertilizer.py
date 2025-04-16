from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Fertilizer

User = get_user_model()

class FertilizerModelTests(TestCase):
    """Tests for the Fertilizer model."""
    
    def test_fertilizer_creation(self):
        """Test creating a Fertilizer instance with required fields."""
        fertilizer = Fertilizer.objects.create(
            fertilizer_name="All-Purpose Organic Fertilizer",
            base_type="ORG",
            form="GRA",
            npk_ratio="5-5-5",
            micronutrient_composition=[
                {"nutrient": "Iron (Fe)", "value": 0.5, "unit": "%"},
                {"nutrient": "Calcium (Ca)", "value": 1.0, "unit": "%"}
            ],
            application_rate=[
                {"value": 2, "unit": "lbs/1000 sq ft", "context": "Lawn application"},
                {"value": 1, "unit": "tbsp/gallon", "context": "Container plants"}
            ],
            application_timing_frequency="Every 4-6 weeks during growing season",
            recommended_for="Vegetables, flowers, and herbs",
            compatibility_notes="Do not mix with high-phosphorus fertilizers"
        )
        
        retrieved_fertilizer = Fertilizer.objects.get(pk=fertilizer.pk)
        self.assertEqual(retrieved_fertilizer.fertilizer_name, "All-Purpose Organic Fertilizer")
        self.assertEqual(retrieved_fertilizer.base_type, "ORG")
        self.assertEqual(retrieved_fertilizer.form, "GRA")
        self.assertEqual(retrieved_fertilizer.npk_ratio, "5-5-5")
        
        # Test JSON fields
        self.assertEqual(len(retrieved_fertilizer.micronutrient_composition), 2)
        self.assertEqual(retrieved_fertilizer.micronutrient_composition[0]["nutrient"], "Iron (Fe)")
        self.assertEqual(retrieved_fertilizer.micronutrient_composition[0]["value"], 0.5)
        
        self.assertEqual(len(retrieved_fertilizer.application_rate), 2)
        self.assertEqual(retrieved_fertilizer.application_rate[0]["unit"], "lbs/1000 sq ft")
        self.assertEqual(retrieved_fertilizer.application_rate[1]["context"], "Container plants")
        
    def test_fertilizer_str_method(self):
        """Test the __str__ method of the Fertilizer model."""
        fertilizer = Fertilizer.objects.create(
            fertilizer_name="Test Fertilizer"
        )
        self.assertEqual(str(fertilizer), "Test Fertilizer")


class FertilizerAPITests(APITestCase):
    """Tests for the Fertilizer API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Create users
        cls.admin_user = User.objects.create_user(
            username='testadmin_fertilizerapi',
            password='password123',
            email='admin_fertilizer@example.com',
            role='admin'
        )
        
        cls.regular_user = User.objects.create_user(
            username='testuser_fertilizerapi',
            password='password123',
            email='user_fertilizer@example.com',
            role='user'
        )
        
        # Create a sample fertilizer
        cls.fertilizer1 = Fertilizer.objects.create(
            fertilizer_name="Tomato-Tone Organic Fertilizer",
            base_type="ORG",
            form="GRA",
            npk_ratio="3-4-6",
            application_timing_frequency="Monthly during growing season"
        )
        
        cls.list_url = reverse('fertilizer-list')
        cls.detail_url = reverse('fertilizer-detail', kwargs={'pk': cls.fertilizer1.pk})
    
    def test_list_fertilizers_unauthenticated(self):
        """Test listing fertilizers without authentication (should be allowed)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['fertilizer_name'], self.fertilizer1.fertilizer_name)
    
    def test_retrieve_fertilizer_unauthenticated(self):
        """Test retrieving a specific fertilizer without authentication."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fertilizer_name'], self.fertilizer1.fertilizer_name)
        self.assertEqual(response.data['npk_ratio'], self.fertilizer1.npk_ratio)
    
    def test_create_fertilizer_unauthenticated(self):
        """Test creating a fertilizer without authentication (should be unauthorized)."""
        data = {
            'fertilizer_name': 'Rose Food',
            'base_type': 'SYN',
            'form': 'GRA',
            'npk_ratio': '4-8-4'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Fertilizer.objects.count(), 1)  # No new fertilizer created
    
    def test_create_fertilizer_as_admin(self):
        """Test creating a fertilizer as an admin user."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'fertilizer_name': 'Rose Food',
            'base_type': 'SYN',
            'form': 'GRA',
            'npk_ratio': '4-8-4',
            'application_timing_frequency': 'Every 6 weeks',
            'recommended_for': 'Roses and flowering plants'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Fertilizer.objects.count(), 2)
        self.assertTrue(Fertilizer.objects.filter(fertilizer_name='Rose Food').exists())
    
    def test_update_fertilizer_as_admin(self):
        """Test updating a fertilizer as an admin user."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'fertilizer_name': 'Tomato-Tone Premium Organic Fertilizer',
            'recommended_for': 'Tomatoes and other fruiting vegetables'
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.fertilizer1.refresh_from_db()
        self.assertEqual(self.fertilizer1.fertilizer_name, 'Tomato-Tone Premium Organic Fertilizer')
        self.assertEqual(self.fertilizer1.recommended_for, 'Tomatoes and other fruiting vegetables')
    
    def test_delete_fertilizer_as_admin(self):
        """Test deleting a fertilizer as an admin user."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Fertilizer.objects.count(), 0)
