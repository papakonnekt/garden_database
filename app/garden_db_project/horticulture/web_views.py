import json
import traceback
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, View
from django.db.models import Q
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Plant, Seed, Pest, Disease, Companionship, Region, SoilProfile, Fertilizer, CompanionPlantingInteraction

class HomeView(TemplateView):
    template_name = 'horticulture/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_plants'] = Plant.objects.all().order_by('-created_at')[:5]
        context['recent_seeds'] = Seed.objects.all().order_by('-created_at')[:5]
        context['common_pests'] = Pest.objects.all().order_by('?')[:5]  # Random selection
        context['common_diseases'] = Disease.objects.all().order_by('?')[:5]  # Random selection
        return context

class AboutView(TemplateView):
    template_name = 'horticulture/about.html'

class ApiDocsView(TemplateView):
    template_name = 'horticulture/api_docs.html'

class PlantListView(ListView):
    model = Plant
    template_name = 'horticulture/plant_list.html'
    context_object_name = 'plants'
    paginate_by = 12

    def get_queryset(self):
        queryset = Plant.objects.all().order_by('common_name')

        # Filter by lifecycle type if provided
        lifecycle_type = self.request.GET.get('lifecycle_type')
        if lifecycle_type:
            queryset = queryset.filter(lifecycle_type=lifecycle_type)

        # Filter by growth habit if provided
        growth_habit = self.request.GET.get('growth_habit')
        if growth_habit:
            queryset = queryset.filter(growth_habit=growth_habit)

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(common_name__icontains=query) |
                Q(scientific_name__icontains=query) |
                Q(description__icontains=query) |
                Q(family__icontains=query) |
                Q(genus__icontains=query) |
                Q(species__icontains=query)
            )

        return queryset

class PlantDetailView(DetailView):
    model = Plant
    template_name = 'horticulture/plant_detail.html'
    context_object_name = 'plant'

class SeedListView(ListView):
    model = Seed
    template_name = 'horticulture/seed_list.html'
    context_object_name = 'seeds'
    paginate_by = 12

    def get_queryset(self):
        queryset = Seed.objects.all().order_by('seed_name')

        # Filter by seed type if provided
        seed_type = self.request.GET.get('seed_type')
        if seed_type:
            queryset = queryset.filter(seed_type=seed_type)

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(seed_name__icontains=query) |
                Q(variety__icontains=query) |
                Q(description__icontains=query) |
                Q(plant__common_name__icontains=query) |
                Q(plant__scientific_name__icontains=query)
            )

        return queryset

class SeedDetailView(DetailView):
    model = Seed
    template_name = 'horticulture/seed_detail.html'
    context_object_name = 'seed'

class PestListView(ListView):
    model = Pest
    template_name = 'horticulture/pest_list.html'
    context_object_name = 'pests'
    paginate_by = 12

    def get_queryset(self):
        queryset = Pest.objects.all().order_by('common_name')

        # Filter by category if provided
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(common_name__icontains=query) |
                Q(scientific_name__icontains=query) |
                Q(description__icontains=query) |
                Q(symptoms__icontains=query)
            )

        return queryset

class PestDetailView(DetailView):
    model = Pest
    template_name = 'horticulture/pest_detail.html'
    context_object_name = 'pest'

class DiseaseListView(ListView):
    model = Disease
    template_name = 'horticulture/disease_list.html'
    context_object_name = 'diseases'
    paginate_by = 12

    def get_queryset(self):
        queryset = Disease.objects.all().order_by('common_name')

        # Filter by category if provided
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(common_name__icontains=query) |
                Q(scientific_name__icontains=query) |
                Q(description__icontains=query) |
                Q(symptoms__icontains=query) |
                Q(cause__icontains=query)
            )

        return queryset

class DiseaseDetailView(DetailView):
    model = Disease
    template_name = 'horticulture/disease_detail.html'
    context_object_name = 'disease'

class CompanionListView(ListView):
    model = Companionship
    template_name = 'horticulture/companion_list.html'
    context_object_name = 'companionships'
    paginate_by = 20

    def get_queryset(self):
        queryset = Companionship.objects.all().select_related('plant_subject', 'plant_object')

        # Filter by interaction type if provided
        interaction_type = self.request.GET.get('interaction_type')
        if interaction_type:
            queryset = queryset.filter(interactions__interaction_type=interaction_type)

        # Filter by plant if provided
        plant_id = self.request.GET.get('plant_id')
        if plant_id:
            queryset = queryset.filter(
                Q(plant_subject_id=plant_id) | Q(plant_object_id=plant_id)
            )

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(plant_subject__common_name__icontains=query) |
                Q(plant_subject__scientific_name__icontains=query) |
                Q(plant_object__common_name__icontains=query) |
                Q(plant_object__scientific_name__icontains=query) |
                Q(notes__icontains=query)
            )

        return queryset

class SearchView(TemplateView):
    template_name = 'horticulture/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['query'] = query

        if query:
            # Get results from each model
            plants = Plant.objects.filter(
                Q(common_name__icontains=query) |
                Q(scientific_name__icontains=query) |
                Q(description__icontains=query) |
                Q(family__icontains=query)
            ).order_by('common_name')

            seeds = Seed.objects.filter(
                Q(seed_name__icontains=query) |
                Q(variety__icontains=query) |
                Q(description__icontains=query) |
                Q(plant__common_name__icontains=query)
            ).order_by('seed_name')

            pests = Pest.objects.filter(
                Q(common_name__icontains=query) |
                Q(scientific_name__icontains=query) |
                Q(description__icontains=query)
            ).order_by('common_name')

            diseases = Disease.objects.filter(
                Q(common_name__icontains=query) |
                Q(scientific_name__icontains=query) |
                Q(description__icontains=query) |
                Q(cause__icontains=query)
            ).order_by('common_name')

            # Store counts
            context['plants_count'] = plants.count()
            context['seeds_count'] = seeds.count()
            context['pests_count'] = pests.count()
            context['diseases_count'] = diseases.count()

            # Limit results for display
            context['plants'] = plants[:6]
            context['seeds'] = seeds[:6]
            context['pests'] = pests[:6]
            context['diseases'] = diseases[:6]

        return context


class BulkImportView(View):
    template_name = 'horticulture/bulk_import.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        entity_type = request.POST.get('entity_type')
        json_file = request.FILES.get('json_file')
        update_existing = request.POST.get('update_existing') == 'on'

        result = {
            'success': False,
            'message': '',
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'total': 0,
            'errors': []
        }

        if not entity_type or not json_file:
            result['message'] = 'Missing required fields.'
            return render(request, self.template_name, {'result': result})

        try:
            # Read and parse JSON file
            data = json.loads(json_file.read().decode('utf-8'))

            # Process the data based on entity type
            with transaction.atomic():
                if entity_type == 'plant':
                    if isinstance(data, list):
                        result['total'] = len(data)
                        self._import_plants(data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format. Expected a list of objects.'
                        return render(request, self.template_name, {'result': result})
                elif entity_type == 'seed':
                    if isinstance(data, list):
                        result['total'] = len(data)
                        self._import_seeds(data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format. Expected a list of objects.'
                        return render(request, self.template_name, {'result': result})
                elif entity_type == 'pest':
                    if isinstance(data, list):
                        result['total'] = len(data)
                        self._import_pests(data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format. Expected a list of objects.'
                        return render(request, self.template_name, {'result': result})
                elif entity_type == 'disease':
                    if isinstance(data, list):
                        result['total'] = len(data)
                        self._import_diseases(data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format. Expected a list of objects.'
                        return render(request, self.template_name, {'result': result})
                elif entity_type == 'region':
                    if isinstance(data, list):
                        result['total'] = len(data)
                        self._import_regions(data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format. Expected a list of objects.'
                        return render(request, self.template_name, {'result': result})
                elif entity_type == 'soil_profile':
                    if isinstance(data, list):
                        result['total'] = len(data)
                        self._import_soil_profiles(data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format. Expected a list of objects.'
                        return render(request, self.template_name, {'result': result})
                elif entity_type == 'fertilizer':
                    if isinstance(data, list):
                        result['total'] = len(data)
                        self._import_fertilizers(data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format. Expected a list of objects.'
                        return render(request, self.template_name, {'result': result})
                elif entity_type == 'companionship':
                    if isinstance(data, list):
                        result['total'] = len(data)
                        self._import_companionships(data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format. Expected a list of objects.'
                        return render(request, self.template_name, {'result': result})
                elif entity_type == 'comprehensive':
                    # Handle the comprehensive format
                    if isinstance(data, dict):
                        plants_data = data.get('plants', [])
                        companionships_data = data.get('companion_relationships', [])
                        pests_data = data.get('pests', [])

                        # Import plants first
                        if plants_data:
                            result['total'] += len(plants_data)
                            self._import_plants(plants_data, update_existing, result)

                        # Import pests
                        if pests_data:
                            result['total'] += len(pests_data)
                            self._import_pests(pests_data, update_existing, result)

                        # Import companionships last (since they depend on plants)
                        if companionships_data:
                            result['total'] += len(companionships_data)
                            self._import_companionships(companionships_data, update_existing, result)
                    else:
                        result['message'] = 'Invalid JSON format for comprehensive import. Expected an object with plants, companion_relationships, and pests arrays.'
                        return render(request, self.template_name, {'result': result})
                else:
                    result['message'] = f'Unsupported entity type: {entity_type}'
                    return render(request, self.template_name, {'result': result})

            result['success'] = True
            result['message'] = f'Successfully processed {result["total"]} records.'

        except json.JSONDecodeError:
            result['message'] = 'Invalid JSON format. Could not parse the file.'
        except Exception as e:
            result['message'] = f'Error processing import: {str(e)}'
            result['errors'].append(traceback.format_exc())

        return render(request, self.template_name, {'result': result})

    def _import_plants(self, data, update_existing, result):
        for item in data:
            try:
                scientific_name = item.get('scientific_name')
                if not scientific_name:
                    result['errors'].append(f'Missing scientific_name in item: {item}')
                    result['skipped'] += 1
                    continue

                # Check if plant already exists
                existing_plant = Plant.objects.filter(scientific_name=scientific_name).first()

                if existing_plant and update_existing:
                    # Update existing plant
                    for key, value in item.items():
                        if hasattr(existing_plant, key) and key != 'id':
                            setattr(existing_plant, key, value)
                    existing_plant.save()
                    result['updated'] += 1
                elif not existing_plant:
                    # Create new plant
                    Plant.objects.create(**item)
                    result['created'] += 1
                else:
                    # Skip existing plant
                    result['skipped'] += 1
            except Exception as e:
                result['errors'].append(f'Error processing plant: {str(e)}')
                result['skipped'] += 1

    def _import_seeds(self, data, update_existing, result):
        for item in data:
            try:
                seed_name = item.get('seed_name')
                plant_scientific_name = item.get('plant')

                if not seed_name:
                    result['errors'].append(f'Missing seed_name in item: {item}')
                    result['skipped'] += 1
                    continue

                # Get the related plant if specified
                plant = None
                if plant_scientific_name:
                    plant = Plant.objects.filter(scientific_name=plant_scientific_name).first()
                    if not plant:
                        result['errors'].append(f'Plant not found: {plant_scientific_name}')
                        result['skipped'] += 1
                        continue

                    # Replace plant name with plant object
                    item_copy = item.copy()
                    item_copy.pop('plant')
                    item_copy['plant'] = plant
                else:
                    item_copy = item

                # Check if seed already exists
                existing_seed = Seed.objects.filter(seed_name=seed_name).first()

                if existing_seed and update_existing:
                    # Update existing seed
                    for key, value in item_copy.items():
                        if hasattr(existing_seed, key) and key != 'id':
                            setattr(existing_seed, key, value)
                    existing_seed.save()
                    result['updated'] += 1
                elif not existing_seed:
                    # Create new seed
                    Seed.objects.create(**item_copy)
                    result['created'] += 1
                else:
                    # Skip existing seed
                    result['skipped'] += 1
            except Exception as e:
                result['errors'].append(f'Error processing seed: {str(e)}')
                result['skipped'] += 1

    def _import_pests(self, data, update_existing, result):
        for item in data:
            try:
                common_name = item.get('common_name')
                affected_plants = item.pop('affected_plants', [])

                if not common_name:
                    result['errors'].append(f'Missing common_name in item: {item}')
                    result['skipped'] += 1
                    continue

                # Check if pest already exists
                existing_pest = Pest.objects.filter(common_name=common_name).first()

                if existing_pest and update_existing:
                    # Update existing pest
                    for key, value in item.items():
                        if hasattr(existing_pest, key) and key != 'id':
                            setattr(existing_pest, key, value)
                    existing_pest.save()

                    # Update plant relationships
                    if affected_plants:
                        existing_pest.plants.clear()
                        for plant_name in affected_plants:
                            plant = Plant.objects.filter(scientific_name=plant_name).first()
                            if plant:
                                existing_pest.plants.add(plant)

                    result['updated'] += 1
                elif not existing_pest:
                    # Create new pest
                    pest = Pest.objects.create(**item)

                    # Add plant relationships
                    for plant_name in affected_plants:
                        plant = Plant.objects.filter(scientific_name=plant_name).first()
                        if plant:
                            pest.plants.add(plant)

                    result['created'] += 1
                else:
                    # Skip existing pest
                    result['skipped'] += 1
            except Exception as e:
                result['errors'].append(f'Error processing pest: {str(e)}')
                result['skipped'] += 1

    def _import_diseases(self, data, update_existing, result):
        for item in data:
            try:
                common_name = item.get('common_name')
                affected_plants = item.pop('affected_plants', [])

                if not common_name:
                    result['errors'].append(f'Missing common_name in item: {item}')
                    result['skipped'] += 1
                    continue

                # Check if disease already exists
                existing_disease = Disease.objects.filter(common_name=common_name).first()

                if existing_disease and update_existing:
                    # Update existing disease
                    for key, value in item.items():
                        if hasattr(existing_disease, key) and key != 'id':
                            setattr(existing_disease, key, value)
                    existing_disease.save()

                    # Update plant relationships
                    if affected_plants:
                        existing_disease.plants.clear()
                        for plant_name in affected_plants:
                            plant = Plant.objects.filter(scientific_name=plant_name).first()
                            if plant:
                                existing_disease.plants.add(plant)

                    result['updated'] += 1
                elif not existing_disease:
                    # Create new disease
                    disease = Disease.objects.create(**item)

                    # Add plant relationships
                    for plant_name in affected_plants:
                        plant = Plant.objects.filter(scientific_name=plant_name).first()
                        if plant:
                            disease.plants.add(plant)

                    result['created'] += 1
                else:
                    # Skip existing disease
                    result['skipped'] += 1
            except Exception as e:
                result['errors'].append(f'Error processing disease: {str(e)}')
                result['skipped'] += 1

    def _import_regions(self, data, update_existing, result):
        for item in data:
            try:
                zone_identifier = item.get('zone_identifier')
                zone_system = item.get('zone_system')

                if not zone_identifier or not zone_system:
                    result['errors'].append(f'Missing zone_identifier or zone_system in item: {item}')
                    result['skipped'] += 1
                    continue

                # Check if region already exists
                existing_region = Region.objects.filter(zone_identifier=zone_identifier, zone_system=zone_system).first()

                if existing_region and update_existing:
                    # Update existing region
                    for key, value in item.items():
                        if hasattr(existing_region, key) and key != 'id':
                            setattr(existing_region, key, value)
                    existing_region.save()
                    result['updated'] += 1
                elif not existing_region:
                    # Create new region
                    Region.objects.create(**item)
                    result['created'] += 1
                else:
                    # Skip existing region
                    result['skipped'] += 1
            except Exception as e:
                result['errors'].append(f'Error processing region: {str(e)}')
                result['skipped'] += 1

    def _import_soil_profiles(self, data, update_existing, result):
        for item in data:
            try:
                name = item.get('name')

                if not name:
                    result['errors'].append(f'Missing name in item: {item}')
                    result['skipped'] += 1
                    continue

                # Check if soil profile already exists
                existing_profile = SoilProfile.objects.filter(name=name).first()

                if existing_profile and update_existing:
                    # Update existing soil profile
                    for key, value in item.items():
                        if hasattr(existing_profile, key) and key != 'id':
                            setattr(existing_profile, key, value)
                    existing_profile.save()
                    result['updated'] += 1
                elif not existing_profile:
                    # Create new soil profile
                    SoilProfile.objects.create(**item)
                    result['created'] += 1
                else:
                    # Skip existing soil profile
                    result['skipped'] += 1
            except Exception as e:
                result['errors'].append(f'Error processing soil profile: {str(e)}')
                result['skipped'] += 1

    def _import_fertilizers(self, data, update_existing, result):
        for item in data:
            try:
                fertilizer_name = item.get('fertilizer_name')

                if not fertilizer_name:
                    result['errors'].append(f'Missing fertilizer_name in item: {item}')
                    result['skipped'] += 1
                    continue

                # Check if fertilizer already exists
                existing_fertilizer = Fertilizer.objects.filter(fertilizer_name=fertilizer_name).first()

                if existing_fertilizer and update_existing:
                    # Update existing fertilizer
                    for key, value in item.items():
                        if hasattr(existing_fertilizer, key) and key != 'id':
                            setattr(existing_fertilizer, key, value)
                    existing_fertilizer.save()
                    result['updated'] += 1
                elif not existing_fertilizer:
                    # Create new fertilizer
                    Fertilizer.objects.create(**item)
                    result['created'] += 1
                else:
                    # Skip existing fertilizer
                    result['skipped'] += 1
            except Exception as e:
                result['errors'].append(f'Error processing fertilizer: {str(e)}')
                result['skipped'] += 1

    def _import_companionships(self, data, update_existing, result):
        for item in data:
            try:
                plant_subject_name = item.get('plant_subject')
                plant_object_name = item.get('plant_object')
                interactions_data = item.pop('interactions', [])

                if not plant_subject_name or not plant_object_name:
                    result['errors'].append(f'Missing plant_subject or plant_object in item: {item}')
                    result['skipped'] += 1
                    continue

                # Get the related plants
                plant_subject = Plant.objects.filter(scientific_name=plant_subject_name).first()
                plant_object = Plant.objects.filter(scientific_name=plant_object_name).first()

                if not plant_subject or not plant_object:
                    result['errors'].append(f'Plant not found: {plant_subject_name} or {plant_object_name}')
                    result['skipped'] += 1
                    continue

                # Prepare companionship data
                companionship_data = item.copy()
                companionship_data.pop('plant_subject')
                companionship_data.pop('plant_object')
                companionship_data['plant_subject'] = plant_subject
                companionship_data['plant_object'] = plant_object

                # Check if companionship already exists
                existing_companionship = Companionship.objects.filter(
                    plant_subject=plant_subject,
                    plant_object=plant_object
                ).first()

                if existing_companionship and update_existing:
                    # Update existing companionship
                    for key, value in companionship_data.items():
                        if hasattr(existing_companionship, key) and key != 'id':
                            setattr(existing_companionship, key, value)
                    existing_companionship.save()

                    # Update interactions
                    if interactions_data:
                        existing_companionship.interactions.clear()
                        for interaction_data in interactions_data:
                            interaction_type = interaction_data.get('interaction_type')
                            mechanism_description = interaction_data.get('mechanism_description')

                            interaction = CompanionPlantingInteraction.objects.create(
                                interaction_type=interaction_type,
                                mechanism_description=mechanism_description,
                                interaction_code=f"{plant_subject.common_name}_{plant_object.common_name}_{interaction_type}"
                            )
                            existing_companionship.interactions.add(interaction)

                    result['updated'] += 1
                elif not existing_companionship:
                    # Create new companionship
                    companionship = Companionship.objects.create(**companionship_data)

                    # Add interactions
                    for interaction_data in interactions_data:
                        interaction_type = interaction_data.get('interaction_type')
                        mechanism_description = interaction_data.get('mechanism_description')

                        interaction = CompanionPlantingInteraction.objects.create(
                            interaction_type=interaction_type,
                            mechanism_description=mechanism_description,
                            interaction_code=f"{plant_subject.common_name}_{plant_object.common_name}_{interaction_type}"
                        )
                        companionship.interactions.add(interaction)

                    result['created'] += 1
                else:
                    # Skip existing companionship
                    result['skipped'] += 1
            except Exception as e:
                result['errors'].append(f'Error processing companionship: {str(e)}')
                result['skipped'] += 1
