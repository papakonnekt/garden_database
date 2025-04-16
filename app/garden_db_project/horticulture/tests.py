from django.test import TestCase
from django.urls import reverse
# Use get_user_model to handle potential custom user models correctly
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
# Import your models - adjust path if needed
from .models import Region
# Import timezone if needed for date fields (Region doesn't have them now)
# from django.utils import timezone

# Get the User model defined in settings.AUTH_USER_MODEL
# Ensure AUTH_USER_MODEL is set in settings.py, e.g., AUTH_USER_MODEL = 'horticulture.User'
# If using default Django User, this will get that. If custom, ensure it's registered.
User = get_user_model()

# Create your tests here.

class RegionModelTests(TestCase):
    """Tests for the Region model."""

    def test_region_creation(self):
        """Test creating a Region instance."""
        zone_system = "USDA"
        zone_identifier = "7b"
        region = Region.objects.create(
            zone_system=zone_system,
            zone_identifier=zone_identifier
        )
        retrieved_region = Region.objects.get(pk=region.pk)
        self.assertEqual(retrieved_region.zone_system, zone_system)
        self.assertEqual(retrieved_region.zone_identifier, zone_identifier)
        # Test the __str__ method if defined
        self.assertEqual(str(retrieved_region), f"{zone_system} {zone_identifier}")


class RegionAPITests(APITestCase):
    """Tests for the Region API endpoints (using DRF's APITestCase)."""

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class using Django's setUpTestData."""
        # Create users once for the class
        # Ensure your User model has a 'role' field or adjust user creation accordingly
        try:
            cls.admin_user = User.objects.create_user(
                username='testadmin_regionapi', # Use unique username
                password='password123',
                email='admin_region@example.com',
                role='admin' # Assuming 'role' field exists
            )
            cls.regular_user = User.objects.create_user(
                username='testuser_regionapi', # Use unique username
                password='password123',
                email='user_region@example.com',
                role='user' # Assuming 'role' field exists
            )
        except TypeError as e:
            # Fallback if 'role' is not a field on the default user model
            # or if create_user doesn't accept it directly
            print(f"Warning: Could not set 'role' directly on user creation: {e}")
            cls.admin_user = User.objects.create_user(
                username='testadmin_regionapi',
                password='password123',
                email='admin_region@example.com',
                is_staff=True, # Admins are typically staff
                is_superuser=True # Or superuser, depending on your permission setup
            )
            # You might need to assign the 'admin' role differently if it's via groups/permissions
            cls.regular_user = User.objects.create_user(
                username='testuser_regionapi',
                password='password123',
                email='user_region@example.com'
            )
            # Assign 'user' role if applicable/needed

        # Create a sample region for tests that need an existing object
        cls.region1 = Region.objects.create(zone_system="USDA", zone_identifier="5a")
        cls.list_url = reverse('region-list')
        # Example detail URL - adjust if your URL name is different
        # cls.detail_url = reverse('region-detail', kwargs={'pk': cls.region1.pk})

    def test_list_regions_unauthenticated(self):
        """Test listing regions without authentication (should be allowed due to IsAdminOrReadOnly)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the created region is in the response data
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['zone_system'], self.region1.zone_system)

    def test_create_region_unauthenticated(self):
        """Test creating a region without authentication (should be unauthorized)."""
        data = {'zone_system': 'Sunset', 'zone_identifier': 'H1'}
        response = self.client.post(self.list_url, data, format='json')
        # Expecting 401 Unauthorized as no credentials were provided.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Region.objects.count(), 1) # Ensure no region was created

    def test_create_region_as_admin(self):
        """Test creating a region as an authenticated admin user (should succeed)."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'zone_system': 'Sunset', 'zone_identifier': 'H2'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Region.objects.count(), 2) # One from setUpTestData, one created now
        self.assertTrue(Region.objects.filter(zone_system='Sunset', zone_identifier='H2').exists())

    def test_create_region_as_non_admin(self):
        """Test creating a region as an authenticated non-admin user (should be forbidden)."""
        self.client.force_authenticate(user=self.regular_user)
        data = {'zone_system': 'Koppen', 'zone_identifier': 'Cfb'}
        response = self.client.post(self.list_url, data, format='json')
        # IsAdminOrReadOnly allows read, but POST requires admin rights (IsAdminUser)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Ensure count remains unchanged from setUpTestData
        self.assertEqual(Region.objects.count(), 1)

    # --- Add more tests as needed (retrieve, update, delete, specific validations) ---
