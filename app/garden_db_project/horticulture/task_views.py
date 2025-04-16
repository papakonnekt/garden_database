from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from celery.result import AsyncResult

class TaskStatusView(APIView):
    """
    View to check the status of a Celery task.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id, format=None):
        """
        Get the status of a task by its ID.
        """
        task = AsyncResult(task_id)
        
        if task.state == 'PENDING':
            # Task is pending or does not exist
            response = {
                'status': 'pending',
                'message': 'Task is pending or does not exist'
            }
        elif task.state == 'FAILURE':
            # Task failed
            response = {
                'status': 'failed',
                'message': 'Task failed',
                'error': str(task.result) if task.result else 'Unknown error'
            }
        elif task.state == 'SUCCESS':
            # Task completed successfully
            response = {
                'status': 'completed',
                'result': task.result
            }
        else:
            # Task is in progress
            response = {
                'status': task.state.lower(),
                'message': 'Task is in progress'
            }
        
        return Response(response)
