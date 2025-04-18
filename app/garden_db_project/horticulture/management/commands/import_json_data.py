import os
import json
import re # Moved import here
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import IntegrityError, transaction, models
from django.db.models import Q # Added for OR query
from django.core.exceptions import FieldDoesNotExist # Added for generic field handling

# Attempt to import models. If they don't exist, the command will still load
# but will raise errors during execution if model operations are attempted.
from horticulture.models import (
    Plant, PlantDisease, Pest, Disease, Seed, Region, SoilProfile, ProblemCategory,
    PlantPest, Companionship, CompanionPlantingInteraction # Added models for comprehensive import
)

class Command(BaseCommand):
    help = 'Imports data from JSON files located in a specified directory into the database.'

    # Mapping from filename prefixes to models, JSON keys, and model fields
    MODEL_MAPPING = {
        'pests': {'model': Pest, 'json_key': 'scientific_name', 'model_field': 'scientific_name'},
        'diseases': {'model': Disease, 'json_key': 'Scientific Name (Pathogen)', 'model_field': 'scientific_name'},
        'seeds': {'model': Seed, 'json_key': 'name', 'model_field': 'name'},
        'regions': {'model': Region, 'json_key': 'name', 'model_field': 'name'},
        'soils': {'model': SoilProfile, 'json_key': 'name', 'model_field': 'name'},
        # Plant is not typically imported via single file prefix, but included for completeness if needed
        'plants': {'model': Plant, 'json_key': 'scientific_name', 'model_field': 'scientific_name'},
    }

    # Mapping for keys within a comprehensive JSON file
    COMPREHENSIVE_KEYS_MAPPING = {
        'plants': {'model': Plant, 'json_key': 'scientific_name', 'model_field': 'scientific_name'},
        'diseases': {'model': Disease, 'json_key': 'Scientific Name (Pathogen)', 'model_field': 'scientific_name', 'link_func': '_link_disease_to_plants', 'link_key': 'affected_plants'},
        'pests': {'model': Pest, 'json_key': 'scientific_name', 'model_field': 'scientific_name', 'link_func': '_link_pest_to_plants', 'link_key': 'affected_plants'}, # Assuming 'affected_plants' key for pests
        'companion_relationships': {'model': Companionship, 'import_func': '_import_companionship'}, # Special handling
        # Add other types like fertilizers, amendments if they become part of comprehensive files
    }

    def add_arguments(self, parser):
        # Group for directory-based import
        group_dir = parser.add_argument_group('Directory Import Options')
        group_dir.add_argument(
            '--directory',
            type=str,
            # Removed default='jsons' to make it explicitly optional unless no other args given
            help='Directory containing the JSON files, relative to the project root. Use this OR --type/--path.',
        )

        # Group for single file import
        group_file = parser.add_argument_group('Single File Import Options')
        group_file.add_argument(
            '--type',
            type=str,
            choices=list(self.MODEL_MAPPING.keys()),
            help='Type of data to import (must match a key in MODEL_MAPPING). Required if --path is specified.',
        )
        group_file.add_argument(
            '--path',
            type=str,
            help='Path to a single JSON file to import, relative to the project root. Required if --type is specified.',
        )

    def handle(self, *args, **options):
        import_type = options['type']
        file_path_arg = options['path']
        directory_name = options['directory']

        # --- Argument Validation ---
        is_single_file_mode = import_type and file_path_arg
        is_directory_mode = directory_name is not None

        if is_single_file_mode and is_directory_mode:
            raise CommandError("Specify either '--directory' or both '--type' and '--path', not all.")
        if not is_single_file_mode and not is_directory_mode:
            # Default to directory mode if nothing else specified
            directory_name = 'jsons' # Use default if neither mode explicitly chosen
            is_directory_mode = True
            self.stdout.write(self.style.NOTICE(f"No specific mode chosen, defaulting to directory import from '{directory_name}'."))
            # Alternatively, raise an error if explicit mode selection is desired:
            # raise CommandError("Specify either '--directory' or both '--type' and '--path'.")
        elif import_type and not file_path_arg:
             raise CommandError("If --type is specified, --path must also be specified.")
        elif file_path_arg and not import_type:
             raise CommandError("If --path is specified, --type must also be specified.")


        # --- Project Root Calculation ---
        # Project root is the parent directory of the 'app' directory
        project_root = os.path.dirname(os.path.dirname(settings.BASE_DIR))

        # --- Single File Import Logic ---
        if is_single_file_mode:
            self.stdout.write(f"Starting single file import: type='{import_type}', path='{file_path_arg}'")

            # Validation against MODEL_MAPPING keys is handled by 'choices' in add_arguments
            mapping = self.MODEL_MAPPING[import_type]
            model_class = mapping['model']
            json_key = mapping['json_key']
            model_field = mapping['model_field']

            full_file_path = os.path.join(project_root, file_path_arg)

            if not os.path.isfile(full_file_path):
                raise CommandError(f"File not found at specified path: '{full_file_path}'")

            filename = os.path.basename(full_file_path)
            self.stdout.write(f"\nProcessing file: {filename}...")
            # Pass None for model_class etc. as import_data will detect structure
            self.import_data(full_file_path, None, None, None, filename)

        # --- Directory Import Logic ---
        elif is_directory_mode:
            source_directory = os.path.join(project_root, directory_name)

            if not os.path.isdir(source_directory):
                raise CommandError(f"Directory '{source_directory}' does not exist.")

            self.stdout.write(f"Starting import process from directory: {source_directory}")

            for filename in os.listdir(source_directory):
                if filename.endswith('.json'):
                    file_path = os.path.join(source_directory, filename)
                    self.stdout.write(f"\nProcessing file: {filename}...")

                    # Try comprehensive first, then fallback to prefix matching
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, dict) and any(key in data for key in self.COMPREHENSIVE_KEYS_MAPPING):
                             self.stdout.write(self.style.NOTICE(f"Detected comprehensive structure in {filename} during directory scan."))
                             self._import_comprehensive_data(data, filename)
                             continue # Move to next file after comprehensive import
                        else:
                             # If not comprehensive, proceed to prefix matching
                             self.stdout.write(self.style.NOTICE(f"File {filename} not comprehensive, attempting prefix match..."))
                             pass # Fall through to prefix matching logic
                    except json.JSONDecodeError as e:
                        self.stdout.write(self.style.ERROR(f"Error parsing JSON in {filename}: {e}. Skipping file."))
                        continue
                    except Exception as e: # Catch other file reading errors
                        self.stdout.write(self.style.ERROR(f"Error reading file {filename}: {e}. Skipping file."))
                        continue

                    # --- Prefix Matching Logic (Fallback) ---
                    matched = False
                    for prefix, mapping in self.MODEL_MAPPING.items():
                        # Ensure prefix matching is robust (e.g., 'pests_' vs 'pests_extra_')
                        # Also allow exact match like 'pests.json'
                        if filename.startswith(prefix + '_') or filename == prefix + '.json':
                            model_class = mapping['model']
                            json_key = mapping['json_key']
                            model_field = mapping['model_field']
                            # Call import_data with specific type info for single-type import
                            self.import_data(file_path, model_class, json_key, model_field, filename, force_single_type=True)
                            matched = True
                            break # Stop checking prefixes once a match is found

                    if not matched:
                        self.stdout.write(self.style.WARNING(f"Skipped {filename}: Not comprehensive and no matching model prefix found."))
                else:
                     self.stdout.write(self.style.NOTICE(f"Skipped non-JSON file: {filename}"))

        self.stdout.write(self.style.SUCCESS("\nImport process finished."))


    # Helper function to transform JSON keys (Correctly indented)
    def transform_json_key(self, json_key):
        # Basic transformation: lowercase, replace spaces with underscores
        transformed = json_key.lower().replace(' ', '_')
        # Remove potential problematic characters like parentheses, etc.
        # Keep alphanumeric and underscores, remove others
        transformed = re.sub(r'[^\w_]+', '', transformed)
        # Handle potential double underscores resulting from replacements
        transformed = transformed.replace('__', '_')
        # Remove leading/trailing underscores that might result
        transformed = transformed.strip('_')
        return transformed

    # Import data function (Correctly indented)
    def import_data(self, file_path, model_class, json_key, model_field, filename, force_single_type=False):
        """
        Imports data from a single JSON file.
        Detects comprehensive structure unless force_single_type is True.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing JSON in {filename}: {e}"))
                    return # Skip this file

            # --- Structure Detection ---
            is_comprehensive = False
            if not force_single_type and isinstance(data, dict):
                # Check if top-level keys match our comprehensive structure definition
                comprehensive_keys_present = [key for key in self.COMPREHENSIVE_KEYS_MAPPING if key in data]
                if comprehensive_keys_present:
                    # Consider it comprehensive if at least one known section key is present
                    is_comprehensive = True
                    self.stdout.write(self.style.NOTICE(f"Detected comprehensive file structure in {filename}. Processing sections: {', '.join(comprehensive_keys_present)}"))
                    self._import_comprehensive_data(data, filename)
                    return # Exit after processing comprehensive data

            # --- Fallback or Forced Single-Type Import Logic ---
            if not is_comprehensive:
                if not model_class or not json_key or not model_field:
                     # This can happen if called from directory scan without a prefix match but file wasn't comprehensive
                     self.stdout.write(self.style.WARNING(f"Skipping {filename}: Not comprehensive and no type info provided for single-type import."))
                     return

                self.stdout.write(self.style.NOTICE(f"Processing {filename} as single-type: {model_class.__name__}"))
                imported_count = 0
                failed_count = 0

                items = []
                # Determine the list of items based on expected structure for the model type
                if model_class in [Pest, Disease, Seed]: # Types expecting a list within a dict
                    if isinstance(data, dict):
                        found_list = False
                        for value in data.values():
                            if isinstance(value, list):
                                items = value
                                found_list = True
                                break
                        if not found_list:
                             self.stdout.write(self.style.ERROR(f"Skipped {filename}: Expected a list of items within the top-level JSON object for {model_class.__name__}, but none found."))
                             return
                    else:
                        self.stdout.write(self.style.ERROR(f"Skipped {filename}: Expected a top-level JSON object for {model_class.__name__}, but found {type(data).__name__}."))
                        return
                else: # Types expecting a list directly, or a single object
                    if isinstance(data, dict):
                        items = [data] # Treat single object as a list with one item
                    elif isinstance(data, list):
                        items = data
                    else:
                        self.stdout.write(self.style.ERROR(f"Skipped {filename}: JSON root must be an object or a list of objects for {model_class.__name__}."))
                        return

                # Get the set of valid field names for the model
                valid_field_names = set(f.name for f in model_class._meta.get_fields())

                # Loop through items
                for item_data in items:
                    obj, created, error = self._import_single_item(
                        model_class=model_class,
                        item_data=item_data,
                        unique_key_json=json_key,
                        unique_key_model=model_field,
                        valid_field_names=valid_field_names,
                        filename=filename
                    )

                    if obj:
                        imported_count += 1
                        # --- Link relationships for single-type imports (currently only Disease) ---
                        if model_class == Disease:
                            affected_plants_key = "Affected Host Plants" # Specific to current Disease JSON structure
                            if affected_plants_key in item_data and isinstance(item_data[affected_plants_key], list):
                                self._link_disease_to_plants(obj, item_data[affected_plants_key], filename)
                        # Add similar blocks here if other single-type imports need linking (e.g., Pests if they have a single-type format)
                    else:
                        failed_count += 1
                        # Error message already printed by _import_single_item

                # Success message for the file
                self.stdout.write(self.style.SUCCESS(f"Finished processing {filename}: Imported/Updated {imported_count} records, Failed {failed_count} records."))

        # Outer exception handling
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred processing {filename}: {e}"))

    # --- Helper Functions ---

    def _import_single_item(self, model_class, item_data, unique_key_json, unique_key_model, valid_field_names, filename, specific_mappings=None):
        """
        Imports or updates a single item into the database.

        Args:
            model_class: The Django model class.
            item_data: Dictionary containing the data for one item from JSON.
            unique_key_json: The key in item_data used for the unique identifier.
            unique_key_model: The corresponding model field name for the unique identifier.
            valid_field_names: A set of valid field names for the model.
            filename: The name of the source JSON file (for logging).
            specific_mappings: Optional dictionary for model-specific field handling logic.

        Returns:
            Tuple: (object_instance, created_boolean, error_message_string or None)
                   Returns (None, False, error_message) on failure.
        """
        if not isinstance(item_data, dict):
            error_msg = f"Skipping non-object item in {filename}."
            self.stdout.write(self.style.WARNING(error_msg))
            return None, False, error_msg

        unique_field_value = item_data.get(unique_key_json)
        if unique_field_value is None:
            error_msg = f"Skipping record in {filename}: Unique JSON key '{unique_key_json}' not found or is null."
            self.stdout.write(self.style.WARNING(error_msg))
            return None, False, error_msg

        defaults = {}
        for current_json_key, value in item_data.items():
            # Skip the key used for the unique identifier and relationship keys handled later
            if current_json_key == unique_key_json or current_json_key in ['Affected Host Plants', 'affected_plants', 'interactions', 'plant_subject', 'plant_object']:
                continue

            processed_specifically = False
            # --- START: Model-specific mapping (e.g., Disease) ---
            if model_class == Disease: # Example specific handling
                if current_json_key == "Pathogen Type":
                    category_map = {
                        "Fungal": ProblemCategory.FUNGAL, "Bacterial": ProblemCategory.BACTERIAL,
                        "Viral": ProblemCategory.VIRAL, # Add others as needed
                    }
                    defaults['category'] = category_map.get(str(value), ProblemCategory.UNKNOWN)
                    processed_specifically = True
                elif current_json_key == "Disease Cycle/Epidemiology":
                    defaults['description'] = str(value)
                    processed_specifically = True
                elif current_json_key == "Symptoms":
                    if isinstance(value, dict):
                        defaults['symptoms'] = "\n".join([f"{k}: {v}" for k, v in value.items()])
                    elif isinstance(value, str):
                         defaults['symptoms'] = value
                    processed_specifically = True # Mark as processed even if type wasn't dict/str
                elif current_json_key == "Management Strategies":
                    if isinstance(value, (dict, list)):
                        defaults['treatment_strategies'] = value
                    processed_specifically = True
                elif current_json_key == "Conditions Favoring Disease Development":
                    defaults['conditions_favoring'] = str(value)
                    processed_specifically = True
                elif current_json_key == "Geographic Distribution":
                    defaults['geographic_distribution'] = str(value)
                    processed_specifically = True
                elif current_json_key == "Transmission Methods":
                    if isinstance(value, list):
                        defaults['transmission_methods'] = value
                    processed_specifically = True
            # --- END: Model-specific mapping ---
            # Add elif blocks here for Pest-specific mappings if needed
            elif model_class == Pest:
                 # Example: Map 'Control Methods' to a specific field if needed
                 if current_json_key == "Control Methods":
                     if isinstance(value, (dict, list)):
                         defaults['control_methods'] = value # Assuming a JSONField 'control_methods'
                     elif isinstance(value, str):
                          defaults['control_methods_text'] = value # Assuming a TextField fallback
                     processed_specifically = True
                 # Add other Pest specific mappings

            # --- START: Generic mapping (if not processed specifically) ---
            if not processed_specifically:
                potential_model_field = self.transform_json_key(current_json_key)
                if potential_model_field in valid_field_names and potential_model_field != unique_key_model:
                    # Basic type handling for common cases (can be expanded)
                    try:
                        field_object = model_class._meta.get_field(potential_model_field)
                        # Handle JSONField specifically if needed, otherwise basic assignment
                        if isinstance(field_object, models.JSONField):
                             defaults[potential_model_field] = value # Assign directly
                        elif isinstance(field_object, (models.CharField, models.TextField)):
                             defaults[potential_model_field] = str(value) # Ensure string
                        elif isinstance(field_object, models.IntegerField):
                             try:
                                 defaults[potential_model_field] = int(value)
                             except (ValueError, TypeError):
                                 self.stdout.write(self.style.WARNING(f"  Could not convert value '{value}' to int for field '{potential_model_field}' in {filename}. Skipping field."))
                        elif isinstance(field_object, models.FloatField):
                             try:
                                 defaults[potential_model_field] = float(value)
                             except (ValueError, TypeError):
                                 self.stdout.write(self.style.WARNING(f"  Could not convert value '{value}' to float for field '{potential_model_field}' in {filename}. Skipping field."))
                        elif isinstance(field_object, models.BooleanField):
                             # Handle common boolean representations
                             if isinstance(value, str):
                                 defaults[potential_model_field] = value.lower() in ['true', 'yes', '1']
                             else:
                                 defaults[potential_model_field] = bool(value)
                        # Add handling for DateField, DateTimeField if needed
                        # elif isinstance(field_object, models.DateField): ...
                        else:
                             # For other types (ForeignKey, ManyToMany are handled separately), assign directly
                             defaults[potential_model_field] = value
                    except FieldDoesNotExist:
                         self.stdout.write(self.style.WARNING(f"  Field '{potential_model_field}' (from JSON key '{current_json_key}') does not exist in model {model_class.__name__}. Skipping."))
                # Optional: Add warnings for skipped keys
            # --- END: Generic mapping ---

        try:
            with transaction.atomic():
                obj, created = model_class.objects.update_or_create(
                    **{unique_key_model: unique_field_value},
                    defaults=defaults
                )
                action = "Created" if created else "Updated"
                # self.stdout.write(self.style.SUCCESS(f"  {action}: {obj}")) # Verbose
                return obj, created, None
        except IntegrityError as e:
            # --- START: Handle common_name uniqueness violation for Disease ---
            # Check if it's a Disease model and the error message indicates a common_name constraint issue
            # Note: The exact constraint name might vary slightly depending on DB backend/Django version,
            # but checking for the model and field name is usually robust enough.
            if model_class == Disease and 'horticulture_disease_common_name' in str(e):
                common_name_from_data = defaults.get('common_name')
                if common_name_from_data:
                    self.stdout.write(self.style.WARNING(
                        f"  IntegrityError on {unique_key_model} for '{unique_field_value}'. "
                        f"Checking for existing disease with common_name='{common_name_from_data}'..."
                    ))
                    try:
                        # Attempt to find the existing object by common_name
                        existing_obj = Disease.objects.get(common_name=common_name_from_data)
                        self.stdout.write(self.style.NOTICE(
                            f"  Found existing disease '{existing_obj}' by common_name. Updating it with data from current record."
                        ))

                        # Update the found object fields using the 'defaults' from the current item
                        fields_updated_count = 0
                        with transaction.atomic(): # Wrap update in transaction
                            for key, value in defaults.items():
                                # Only update if the value is different to avoid unnecessary saves
                                if hasattr(existing_obj, key) and getattr(existing_obj, key) != value:
                                    setattr(existing_obj, key, value)
                                    fields_updated_count += 1
                                    # self.stdout.write(f"    Updating field {key}...") # Verbose logging if needed

                            # Explicitly check if the unique_key_model (e.g., scientific_name) needs updating
                            # This might happen if the scientific name in the JSON differs from the one
                            # associated with the existing common_name record.
                            if getattr(existing_obj, unique_key_model) != unique_field_value:
                                 self.stdout.write(self.style.WARNING(
                                     f"    Scientific name mismatch: Existing='{getattr(existing_obj, unique_key_model)}', New='{unique_field_value}'. "
                                     f"Keeping existing scientific name associated with common_name '{common_name_from_data}'."
                                 ))
                                 # Decision: Do not update the scientific_name here to preserve the integrity
                                 # of the record found by common_name. The warning highlights the discrepancy.
                                 # If overwriting scientific_name is desired, uncomment the next line:
                                 # setattr(existing_obj, unique_key_model, unique_field_value)
                                 # fields_updated_count += 1

                            if fields_updated_count > 0:
                                existing_obj.save()
                                self.stdout.write(self.style.SUCCESS(
                                    f"  Successfully updated {fields_updated_count} fields for existing disease '{existing_obj}' found via common_name."
                                ))
                            else:
                                 self.stdout.write(self.style.NOTICE(
                                    f"  No fields needed updating for existing disease '{existing_obj}' found via common_name."
                                ))


                        obj = existing_obj # Set obj to the one we found and updated
                        created = False    # Mark as not created
                        return obj, created, None # Return the updated object and success

                    except Disease.DoesNotExist:
                        # This case is unusual: the DB threw a unique constraint error for common_name,
                        # but we couldn't find the record using that same common_name.
                        error_msg = (f"  IntegrityError on common_name for '{common_name_from_data}' "
                                     f"(originally identified by {unique_key_json}='{unique_field_value}'), "
                                     f"but no existing record found by this common_name. This is unexpected. File: {filename}. Error: {e}")
                        self.stdout.write(self.style.ERROR(error_msg))
                        return None, False, error_msg
                    except Exception as lookup_update_e:
                        # Catch potential errors during the get() or save() operations
                        error_msg = (f"  Error looking up/updating disease by common_name '{common_name_from_data}' "
                                     f"after initial IntegrityError in {filename}: {lookup_update_e}")
                        self.stdout.write(self.style.ERROR(error_msg))
                        return None, False, error_msg
                else:
                    # If common_name wasn't in the defaults dict for some reason, we can't proceed with the lookup.
                    error_msg = (f"Database integrity error likely on common_name for record identified by "
                                 f"{unique_key_json}='{unique_field_value}' in {filename}, but 'common_name' not found in processed 'defaults' dictionary. Cannot attempt recovery. Error: {e}")
                    self.stdout.write(self.style.ERROR(error_msg))
                    return None, False, error_msg
            # --- END: Handle common_name uniqueness violation ---
            else:
                # Original error handling for other IntegrityErrors or errors on other models
                error_msg = f"Database integrity error for record identified by {unique_key_json}='{unique_field_value}' in {filename}: {e}"
                self.stdout.write(self.style.ERROR(error_msg))
                return None, False, error_msg
        except Exception as e:
             # Keep original general exception handling for non-IntegrityError issues
             error_msg = f"Error importing record identified by {unique_key_json}='{unique_field_value}' in {filename}: {e}"
             self.stdout.write(self.style.ERROR(error_msg))
             return None, False, error_msg

    def _link_disease_to_plants(self, disease_obj, plant_identifiers, filename):
        """Links a Disease object to Plant objects based on identifiers."""
        if not isinstance(plant_identifiers, list):
            self.stdout.write(self.style.WARNING(f"  'Affected Host Plants' is not a list for disease '{disease_obj}' in {filename}. Skipping linking."))
            return

        total_linked = 0
        total_errors = 0
        processed_identifiers = set()

        for identifier in plant_identifiers:
            if not isinstance(identifier, str):
                self.stdout.write(self.style.WARNING(f"  Skipping non-string plant identifier '{identifier}' for disease '{disease_obj}'."))
                continue

            # Avoid processing the same general type multiple times if listed redundantly
            general_plant_type = identifier.split('(')[0].strip()
            if not general_plant_type or general_plant_type in processed_identifiers:
                continue
            processed_identifiers.add(general_plant_type)

            try:
                # Find plants where common_name *contains* the general type (case-insensitive)
                # Or where scientific_name *starts with* the general type (case-insensitive) - common for genus matching
                matching_plants = Plant.objects.filter(
                    Q(common_name__icontains=general_plant_type) |
                    Q(scientific_name__istartswith=general_plant_type)
                ).distinct()

                if not matching_plants.exists():
                    self.stdout.write(self.style.WARNING(f"  No existing plants found matching general type '{general_plant_type}' for disease '{disease_obj}'. No links created for this identifier."))
                else:
                    self.stdout.write(self.style.NOTICE(f"  Found {matching_plants.count()} existing plant(s) matching type '{general_plant_type}' for disease '{disease_obj}'. Linking..."))
                    linked_count = 0
                    link_errors = 0
                    for plant_instance in matching_plants:
                        try:
                            with transaction.atomic():
                                pd_obj, pd_created = PlantDisease.objects.update_or_create(
                                    plant=plant_instance,
                                    disease=disease_obj,
                                    # Add defaults for PlantDisease if any are needed
                                )
                                linked_count += 1
                        except IntegrityError as e_pd_integrity:
                            self.stdout.write(self.style.ERROR(f"    Integrity error creating relationship for {plant_instance} <-> {disease_obj}: {e_pd_integrity}"))
                            link_errors += 1
                        except Exception as e_pd_create:
                            self.stdout.write(self.style.ERROR(f"    Error creating relationship for {plant_instance} <-> {disease_obj}: {e_pd_create}"))
                            link_errors += 1

                    if linked_count > 0:
                         self.stdout.write(self.style.SUCCESS(f"    Successfully linked/updated {linked_count} plant(s) of type '{general_plant_type}' to disease '{disease_obj}'."))
                         total_linked += linked_count
                    if link_errors > 0:
                         self.stdout.write(self.style.ERROR(f"    Failed to link {link_errors} plant(s) of type '{general_plant_type}' to disease '{disease_obj}' due to errors."))
                         total_errors += link_errors

            except Exception as e_plant_lookup:
                self.stdout.write(self.style.ERROR(f"  Error querying plants matching type '{general_plant_type}' for identifier '{identifier}': {e_plant_lookup}"))
                total_errors += 1 # Count query error as a failure
                continue

        self.stdout.write(f"  Finished linking plants for disease '{disease_obj}'. Total linked: {total_linked}, Total errors: {total_errors}.")

    def _import_comprehensive_data(self, data, filename):
        """Processes a dictionary assumed to be from a comprehensive JSON file."""
        self.stdout.write(self.style.NOTICE(f"--- Starting Comprehensive Import: {filename} ---"))
        processed_objects = {} # Store created/updated objects {section_key: {unique_id: obj}}

        # Define processing order - ensure plants are processed first if present
        processing_order = ['plants'] + [k for k in self.COMPREHENSIVE_KEYS_MAPPING if k != 'plants']

        for section_key in processing_order:
            if section_key not in data:
                continue # Skip sections not present in this file

            if section_key not in self.COMPREHENSIVE_KEYS_MAPPING:
                self.stdout.write(self.style.WARNING(f"Skipping unknown section '{section_key}' in {filename}."))
                continue

            mapping = self.COMPREHENSIVE_KEYS_MAPPING[section_key]
            section_data = data[section_key]

            if not isinstance(section_data, list):
                self.stdout.write(self.style.ERROR(f"Expected a list for section '{section_key}' in {filename}, found {type(section_data).__name__}. Skipping section."))
                continue

            self.stdout.write(f"\nProcessing section: '{section_key}' ({len(section_data)} items)...")
            processed_objects[section_key] = {}
            section_imported_count = 0
            section_failed_count = 0

            # --- Special handling for sections with custom import functions ---
            if 'import_func' in mapping:
                import_function = getattr(self, mapping['import_func'], None)
                if import_function:
                    for item_data in section_data:
                        # Custom import functions should return (success_boolean, error_message_or_None)
                        success, error = import_function(item_data, filename)
                        if success:
                            section_imported_count += 1
                        else:
                            section_failed_count += 1
                            # Error should be logged within the import function
                else:
                    self.stdout.write(self.style.ERROR(f"Configured import function '{mapping['import_func']}' not found for section '{section_key}'. Skipping section."))
                    continue # Skip to next section
            # --- Standard handling using _import_single_item ---
            else:
                model_class = mapping['model']
                default_json_key = mapping['json_key'] # Get the default key from mapping
                model_field = mapping['model_field']
                valid_field_names = set(f.name for f in model_class._meta.get_fields())

                for item_data in section_data:
                    # Determine the correct JSON key based on section
                    current_json_key = "scientific_name" if section_key == 'diseases' else default_json_key

                    obj, created, error = self._import_single_item(
                        model_class=model_class,
                        item_data=item_data,
                        unique_key_json=current_json_key, # Use the determined key
                        unique_key_model=model_field,
                        valid_field_names=valid_field_names,
                        filename=filename
                    )
                    if obj:
                        # Store successfully processed object using its unique model field value as the key
                        processed_objects[section_key][getattr(obj, model_field)] = obj
                        section_imported_count += 1

                        # --- START: Inline Linking for Comprehensive Import ---
                        # If this is the diseases section, perform linking immediately
                        if section_key == 'diseases':
                            link_key_json = mapping.get('link_key') # e.g., "Affected Host Plants"
                            link_func_name = mapping.get('link_func') # e.g., "_link_disease_to_plants"
                            link_function = getattr(self, link_func_name, None) if link_func_name else None

                            if link_key_json and link_function:
                                link_identifiers = item_data.get(link_key_json)
                                if link_identifiers:
                                    self.stdout.write(self.style.NOTICE(f"  Attempting inline linking for disease '{obj}'..."))
                                    link_function(obj, link_identifiers, filename)
                                else:
                                    # Log if linking key is missing for this item, but don't fail import
                                    self.stdout.write(self.style.NOTICE(f"  No '{link_key_json}' data found for disease '{obj}' in {filename}. Skipping inline linking for this item."))
                            elif not link_key_json:
                                self.stdout.write(self.style.WARNING(f"  Cannot perform inline linking for disease '{obj}': 'link_key' not defined in COMPREHENSIVE_KEYS_MAPPING for 'diseases'."))
                            elif not link_function:
                                self.stdout.write(self.style.WARNING(f"  Cannot perform inline linking for disease '{obj}': Link function '{link_func_name}' not found."))
                        # Add elif section_key == 'some_other_type': for other inline linking if needed
                        # --- END: Inline Linking ---
                    else:
                        section_failed_count += 1

            self.stdout.write(self.style.SUCCESS(f"Finished section '{section_key}': Imported/Updated {section_imported_count}, Failed {section_failed_count}"))

        # --- Post-Import Linking (Diseases linking moved inline) ---
        # Iterate again after all primary objects are created/updated
        self.stdout.write("\n--- Starting Post-Import Linking (Excluding Diseases) ---")
        for section_key in processing_order:
            # Skip diseases section as it's handled inline now
            if section_key == 'diseases':
                self.stdout.write(self.style.NOTICE(f"Skipping post-import linking for '{section_key}' (handled inline)."))
                continue

            if section_key not in data or section_key not in processed_objects:
                continue # Skip if section wasn't present or had no successful imports

            mapping = self.COMPREHENSIVE_KEYS_MAPPING.get(section_key, {})
            link_func_name = mapping.get('link_func')
            link_key_json = mapping.get('link_key')

            # Check if this section type has linking logic defined AND is NOT diseases
            if link_func_name and link_key_json: # No need to check section_key != 'diseases' due to continue above
                link_function = getattr(self, link_func_name, None)
                if link_function:
                    self.stdout.write(f"Linking relationships for section: '{section_key}'...")
                    section_data = data[section_key] # Get original data again for linking info
                    default_json_key = mapping['json_key'] # Key used to identify the primary object

                    items_processed_for_linking = 0
                    for item_data in section_data:
                        # Determine the correct JSON key based on section for lookup
                        # (Keep original logic here, assuming it was correct for other types)
                        current_json_key = default_json_key # Use default unless specific logic needed

                        # Find the already imported object using the correct key
                        unique_id_value = item_data.get(current_json_key)
                        if unique_id_value is None:
                            self.stdout.write(self.style.WARNING(f"  Skipping linking for item in section '{section_key}': Unique key '{current_json_key}' not found in item data: {item_data.keys()}"))
                            continue # Cannot find object if key is missing

                        # Retrieve the object instance stored earlier using the unique *model* field value
                        obj_to_link = processed_objects[section_key].get(unique_id_value)

                        # Get the list of identifiers to link to
                        link_identifiers = item_data.get(link_key_json)

                        if obj_to_link and link_identifiers:
                            items_processed_for_linking += 1
                            # Call the specific linking function (e.g., _link_pest_to_plants)
                            link_function(obj_to_link, link_identifiers, filename)
                        elif obj_to_link and not link_identifiers:
                            pass # Object exists but no linking data
                        elif not obj_to_link and link_identifiers:
                            self.stdout.write(self.style.WARNING(f"  Cannot link for item with ID '{unique_id_value}' in section '{section_key}': Object was not successfully imported/found."))

                    self.stdout.write(f"Processed linking for {items_processed_for_linking} items in section '{section_key}'.")
                else:
                    self.stdout.write(self.style.ERROR(f"Configured link function '{link_func_name}' not found for section '{section_key}'. Skipping linking."))

        self.stdout.write(self.style.SUCCESS(f"--- Finished Comprehensive Import: {filename} ---"))

    def _link_pest_to_plants(self, pest_obj, plant_identifiers, filename):
        """Links a Pest object to Plant objects based on identifiers."""
        # Use the configured key from COMPREHENSIVE_KEYS_MAPPING
        link_key_name = self.COMPREHENSIVE_KEYS_MAPPING['pests'].get('link_key', 'affected_plants') # Default if not set

        if not isinstance(plant_identifiers, list):
            self.stdout.write(self.style.WARNING(f"  '{link_key_name}' is not a list for pest '{pest_obj}' in {filename}. Skipping linking."))
            return

        total_linked = 0
        total_errors = 0
        processed_identifiers = set()

        for identifier in plant_identifiers:
            if not isinstance(identifier, str):
                self.stdout.write(self.style.WARNING(f"  Skipping non-string plant identifier '{identifier}' for pest '{pest_obj}'."))
                continue

            # Avoid processing the same general type multiple times if listed redundantly
            general_plant_type = identifier.split('(')[0].strip()
            if not general_plant_type or general_plant_type in processed_identifiers:
                continue
            processed_identifiers.add(general_plant_type)

            try:
                # Find plants where common_name *contains* the general type (case-insensitive)
                # Or where scientific_name *starts with* the general type (case-insensitive)
                matching_plants = Plant.objects.filter(
                    Q(common_name__icontains=general_plant_type) |
                    Q(scientific_name__istartswith=general_plant_type)
                ).distinct()

                if not matching_plants.exists():
                    self.stdout.write(self.style.WARNING(f"  No existing plants found matching general type '{general_plant_type}' for pest '{pest_obj}'. No links created for this identifier."))
                else:
                    self.stdout.write(self.style.NOTICE(f"  Found {matching_plants.count()} existing plant(s) matching type '{general_plant_type}' for pest '{pest_obj}'. Linking..."))
                    linked_count = 0
                    link_errors = 0
                    for plant_instance in matching_plants:
                        try:
                            # Use transaction.atomic for each link attempt
                            with transaction.atomic():
                                pp_obj, pp_created = PlantPest.objects.update_or_create(
                                    plant=plant_instance,
                                    pest=pest_obj,
                                    # Add defaults for PlantPest if any are needed, e.g., severity, notes
                                    # defaults={'severity': item_data.get('severity', 'Unknown')}
                                )
                                linked_count += 1
                        except IntegrityError as e_pp_integrity:
                            self.stdout.write(self.style.ERROR(f"    Integrity error creating relationship for {plant_instance} <-> {pest_obj}: {e_pp_integrity}"))
                            link_errors += 1
                        except Exception as e_pp_create:
                            self.stdout.write(self.style.ERROR(f"    Error creating relationship for {plant_instance} <-> {pest_obj}: {e_pp_create}"))
                            link_errors += 1

                    if linked_count > 0:
                         self.stdout.write(self.style.SUCCESS(f"    Successfully linked/updated {linked_count} plant(s) of type '{general_plant_type}' to pest '{pest_obj}'."))
                         total_linked += linked_count
                    if link_errors > 0:
                         self.stdout.write(self.style.ERROR(f"    Failed to link {link_errors} plant(s) of type '{general_plant_type}' to pest '{pest_obj}' due to errors."))
                         total_errors += link_errors

            except Exception as e_plant_lookup:
                self.stdout.write(self.style.ERROR(f"  Error querying plants matching type '{general_plant_type}' for identifier '{identifier}': {e_plant_lookup}"))
                total_errors += 1 # Count query error as a failure
                continue

        # Summary log for the specific pest object
        self.stdout.write(f"  Finished linking plants for pest '{pest_obj}'. Total linked: {total_linked}, Total errors: {total_errors}.")

    def _import_companionship(self, item_data, filename):
        """
        Imports a single companionship relationship.
        Returns: (success_boolean, error_message_or_None)
        """
        self.stdout.write(self.style.NOTICE(f"  Attempting to import companionship from item in {filename}..."))
        # --- Configuration ---
        subject_key = 'plant_subject' # Expected JSON key for subject plant identifier (e.g., scientific name)
        object_key = 'plant_object'   # Expected JSON key for object plant identifier (e.g., scientific name)
        interactions_key = 'interactions' # Expected JSON key for list of interaction names (strings)
        identifier_field = 'scientific_name' # Field on Plant model to match identifiers against

        # --- Extract Identifiers ---
        subject_identifier = item_data.get(subject_key)
        object_identifier = item_data.get(object_key)

        if not subject_identifier or not object_identifier:
            error_msg = f"  Skipping companionship item in {filename}: Missing '{subject_key}' ('{subject_identifier}') or '{object_key}' ('{object_identifier}')."
            self.stdout.write(self.style.WARNING(error_msg))
            return False, error_msg # Indicate failure

        # --- Find Plant Objects ---
        try:
            # Use get() for exact match on the identifier field
            plant_subject = Plant.objects.get(**{identifier_field: subject_identifier})
            plant_object = Plant.objects.get(**{identifier_field: object_identifier})
        except Plant.DoesNotExist as e:
            error_msg = f"  Skipping companionship in {filename}: Could not find Plant. {e}. Subject='{subject_identifier}', Object='{object_identifier}'."
            self.stdout.write(self.style.WARNING(error_msg))
            return False, error_msg # Indicate failure
        except Plant.MultipleObjectsReturned as e:
             error_msg = f"  Skipping companionship in {filename}: Multiple Plants found. {e}. Subject='{subject_identifier}', Object='{object_identifier}'. Identifiers must be unique."
             self.stdout.write(self.style.WARNING(error_msg))
             return False, error_msg # Indicate failure
        except Exception as e:
             error_msg = f"  Error finding plants for companionship ({subject_identifier} <-> {object_identifier}) in {filename}: {e}"
             self.stdout.write(self.style.ERROR(error_msg))
             return False, error_msg # Indicate failure

        # --- Create/Update Companionship ---
        try:
            # Prepare defaults by transforming JSON keys (excluding subject/object/interactions)
            defaults = {}
            valid_comp_fields = set(f.name for f in Companionship._meta.get_fields() if f.name not in ['id', 'plant_subject', 'plant_object', 'interactions'])
            for key, value in item_data.items():
                if key in [subject_key, object_key, interactions_key]:
                    continue
                potential_field = self.transform_json_key(key)
                if potential_field in valid_comp_fields:
                    # Add specific type handling if necessary for Companionship fields (e.g., relationship_type enum)
                    # field_object = Companionship._meta.get_field(potential_field)
                    # if isinstance(field_object, ...): ...
                    defaults[potential_field] = value

            # Use transaction.atomic for the companionship and its interactions
            with transaction.atomic():
                companionship, created = Companionship.objects.update_or_create(
                    plant_subject=plant_subject,
                    plant_object=plant_object,
                    defaults=defaults
                )
                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"    {action} companionship: {plant_subject} <-> {plant_object}"))

                # --- Handle Nested Interactions (M2M) ---
                interactions_data = item_data.get(interactions_key)
                notes_updated = False # Flag to track if notes were modified

                # Only modify interactions if the key is present in the JSON
                if interactions_data is not None:
                    if isinstance(interactions_data, list):
                        # Clear existing interactions before adding new ones based on JSON
                        companionship.interactions.clear()
                        self.stdout.write(self.style.NOTICE(f"      Cleared existing interactions for {plant_subject} <-> {plant_object}."))

                        interactions_added_count = 0
                        for interaction_data in interactions_data:
                            if not isinstance(interaction_data, dict):
                                self.stdout.write(self.style.WARNING(f"      Skipping invalid interaction item (must be an object): {interaction_data}"))
                                continue

                            interaction_type = interaction_data.get('interaction_type')
                            mechanism_description = interaction_data.get('mechanism_description')

                            if not interaction_type:
                                self.stdout.write(self.style.WARNING(f"      Skipping interaction item: Missing 'interaction_type' in {interaction_data}"))
                                continue

                            try:
                                # Find the first pre-existing interaction record by type
                                interaction_record = CompanionPlantingInteraction.objects.filter(interaction_type=interaction_type).first()

                                if interaction_record:
                                    companionship.interactions.add(interaction_record)
                                    interactions_added_count += 1
                                    self.stdout.write(self.style.SUCCESS(f"        Added interaction: {interaction_record.interaction_type} (using first found)"))

                                    # Append mechanism description to notes
                                    if mechanism_description:
                                        current_notes = companionship.notes if companionship.notes else ""
                                        if current_notes:
                                            companionship.notes = f"{current_notes}\nInteraction ({interaction_type}): {mechanism_description}"
                                        else:
                                            companionship.notes = f"Interaction ({interaction_type}): {mechanism_description}"
                                        notes_updated = True # Mark notes as updated
                                else:
                                    # Log a warning if no interaction record was found for the type
                                    self.stdout.write(self.style.WARNING(f"      Skipping interaction type '{interaction_type}': No existing CompanionPlantingInteraction record found."))

                            except Exception as e_int:
                                self.stdout.write(self.style.ERROR(f"      Error processing interaction type '{interaction_type}': {e_int}"))

                        if interactions_added_count > 0:
                            self.stdout.write(self.style.SUCCESS(f"      Finished processing interactions for {plant_subject} <-> {plant_object}. Added {interactions_added_count} interaction(s)."))
                        else:
                             self.stdout.write(self.style.NOTICE(f"      No valid interactions found or added for {plant_subject} <-> {plant_object} from the provided list."))

                        # Save the companionship object if notes were updated
                        if notes_updated:
                            try:
                                companionship.save()
                                self.stdout.write(self.style.SUCCESS(f"      Updated notes for companionship {plant_subject} <-> {plant_object}."))
                            except Exception as e_save:
                                self.stdout.write(self.style.ERROR(f"      Error saving companionship notes for {plant_subject} <-> {plant_object}: {e_save}"))

                    else:
                        self.stdout.write(self.style.WARNING(f"      Skipping interactions for {plant_subject} <-> {plant_object}: '{interactions_key}' key exists but is not a list (type: {type(interactions_data).__name__}). Existing interactions remain unchanged."))
                # else: interactions_key not present, leave existing M2M relations untouched.

            return True, None # Indicate success

        except IntegrityError as e:
            error_msg = f"  Database integrity error for companionship {plant_subject} <-> {plant_object} in {filename}: {e}"
            self.stdout.write(self.style.ERROR(error_msg))
            return False, error_msg # Indicate failure
        except Exception as e:
            error_msg = f"  Error importing companionship {plant_subject} <-> {plant_object} in {filename}: {e}"
            self.stdout.write(self.style.ERROR(error_msg))
            return False, error_msg # Indicate failure
