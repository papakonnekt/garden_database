"""
Management command to fix relationships between plants, pests, and diseases.
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from horticulture.relationship_fixer import fix_all_relationships, fix_relationships_from_json

class Command(BaseCommand):
    help = 'Fix relationships between plants, pests, and diseases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            help='Path to a JSON file to use for fixing relationships',
        )

    def handle(self, *args, **options):
        json_file = options.get('json_file')
        
        if json_file:
            # Make sure the path is absolute
            if not os.path.isabs(json_file):
                json_file = os.path.join(settings.BASE_DIR, '..', json_file)
            
            self.stdout.write(self.style.SUCCESS(f'Fixing relationships from JSON file: {json_file}'))
            pest_count, disease_count = fix_relationships_from_json(json_file)
            self.stdout.write(self.style.SUCCESS(f'Fixed {pest_count} plant-pest relationships and {disease_count} plant-disease relationships from JSON file'))
        else:
            self.stdout.write(self.style.SUCCESS('Fixing all relationships'))
            result = fix_all_relationships()
            self.stdout.write(self.style.SUCCESS(f'Fixed {result["pest_fixed_count"]} plant-pest relationships with {result["pest_error_count"]} errors'))
            self.stdout.write(self.style.SUCCESS(f'Fixed {result["disease_fixed_count"]} plant-disease relationships with {result["disease_error_count"]} errors'))
