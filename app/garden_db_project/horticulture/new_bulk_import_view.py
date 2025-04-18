"""
New Bulk Import View for Garden Database

This module provides a clean implementation of the bulk import view
that uses the BulkImportHandler to process JSON data.
"""

import logging
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .bulk_import_handler import BulkImportHandler

logger = logging.getLogger(__name__)

class NewBulkImportView(LoginRequiredMixin, View):
    """
    View for handling bulk import of various entity types from JSON files.
    Uses the BulkImportHandler to process the data.
    """
    template_name = 'horticulture/bulk_import.html'

    def get(self, request):
        """
        Handle GET requests - display the bulk import form.
        """
        return render(request, self.template_name)

    def post(self, request):
        """
        Handle POST requests - process the uploaded JSON file.
        """
        # Get form data
        entity_type = request.POST.get('entity_type')
        update_existing = request.POST.get('update_existing') == 'on'
        json_file = request.FILES.get('json_file')

        if not entity_type or not json_file:
            result = {
                'success': False,
                'message': 'Missing required fields.',
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'total': 0,
                'errors': []
            }
            return render(request, self.template_name, {'result': result})

        # Use the bulk import handler to process the file
        handler = BulkImportHandler(update_existing=update_existing)
        result = handler.process_json_file(json_file, entity_type)

        return render(request, self.template_name, {'result': result})
