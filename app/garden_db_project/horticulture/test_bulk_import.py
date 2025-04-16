from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Plant, Fertilizer, Region, SoilProfile

User = get_user_model()

class BulkImportTests(APITestCase):
    """Tests for the bulk import functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Create users
        cls.admin_user = User.objects.create_user(
            username='testadmin_bulkimport',
            password='password123',
            email='admin_bulkimport@example.com',
            role='admin'
        )
        
        cls.regular_user = User.objects.create_user(
            username='testuser_bulkimport',
            password='password123',
            email='user_bulkimport@example.com',
            role='user'
        )
        
        # Create a soil profile and region for foreign key relationships
        cls.soil_profile = SoilProfile.objects.create(
            name="Bulk Import Test Soil",
            soil_type="LO"
        )
        
        cls.region = Region.objects.create(
            zone_system="USDA",
            zone_identifier="5b"
        )
        
        cls.bulk_import_url = reverse('bulk-import')
    
    def test_bulk_import_unauthenticated(self):
        """Test bulk import without authentication (should be unauthorized)."""
        data = {
            'entity_type': 'plant',
            'data': [
                {
                    'scientific_name': 'Daucus carota',
                    'common_name': 'Carrot'
                }
            ]
        }
        response = self.client.post(self.bulk_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Plant.objects.count(), 0)  # No plants created
    
    def test_bulk_import_as_regular_user(self):
        """Test bulk import as a regular user (should be forbidden)."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'entity_type': 'plant',
            'data': [
                {
                    'scientific_name': 'Daucus carota',
                    'common_name': 'Carrot'
                }
            ]
        }
        response = self.client.post(self.bulk_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Plant.objects.count(), 0)  # No plants created
    
    def test_bulk_import_plants_as_admin(self):
        """Test bulk import of plants as an admin user."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'entity_type': 'plant',
            'data': [
                {
                    'scientific_name': 'Daucus carota',
                    'common_name': 'Carrot',
                    'lifecycle_type': 'BI',
                    'soil_preference': self.soil_profile.id,
                    'suitable_region': self.region.id
                },
                {
                    'scientific_name': 'Allium cepa',
                    'common_name': 'Onion',
                    'lifecycle_type': 'BI',
                    'soil_preference': self.soil_profile.id,
                    'suitable_region': self.region.id
                }
            ]
        }
        response = self.client.post(self.bulk_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plant.objects.count(), 2)
        self.assertTrue(Plant.objects.filter(scientific_name='Daucus carota').exists())
        self.assertTrue(Plant.objects.filter(scientific_name='Allium cepa').exists())
    
    def test_bulk_import_fertilizers_as_admin(self):
        """Test bulk import of fertilizers as an admin user."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'entity_type': 'fertilizer',
            'data': [
                {
                    'fertilizer_name': 'All-Purpose 10-10-10',
                    'base_type': 'SYN',
                    'form': 'GRA',
                    'npk_ratio': '10-10-10'
                },
                {
                    'fertilizer_name': 'Fish Emulsion',
                    'base_type': 'ORG',
                    'form': 'LIQ',
                    'npk_ratio': '5-1-1'
                }
            ]
        }
        response = self.client.post(self.bulk_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Fertilizer.objects.count(), 2)
        self.assertTrue(Fertilizer.objects.filter(fertilizer_name='All-Purpose 10-10-10').exists())
        self.assertTrue(Fertilizer.objects.filter(fertilizer_name='Fish Emulsion').exists())
    
    def test_bulk_import_invalid_entity_type(self):
        """Test bulk import with an invalid entity type."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'entity_type': 'invalid_type',
            'data': [
                {
                    'name': 'Test'
                }
            ]
        }
        response = self.client.post(self.bulk_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Unknown entity type', response.data['error'])
    
    def test_bulk_import_invalid_data_format(self):
        """Test bulk import with invalid data format."""
        self.client.force_authenticate(user=self.admin_user)
        # Missing entity_type
        data1 = {
            'data': [
                {
                    'scientific_name': 'Daucus carota',
                    'common_name': 'Carrot'
                }
            ]
        }
        response1 = self.client.post(self.bulk_import_url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        
        # data is not a list
        data2 = {
            'entity_type': 'plant',
            'data': {
                'scientific_name': 'Daucus carota',
                'common_name': 'Carrot'
            }
        }
        response2 = self.client.post(self.bulk_import_url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_import_validation_error(self):
        """Test bulk import with validation errors in the data."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'entity_type': 'plant',
            'data': [
                {
                    # Missing required field 'common_name'
                    'scientific_name': 'Daucus carota'
                }
            ]
        }
        response = self.client.post(self.bulk_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        self.assertEqual(Plant.objects.count(), 0)  # No plants created
