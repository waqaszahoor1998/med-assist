from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

@api_view(['GET'])
def ping(request):
    """
    Simple ping endpoint to test API connectivity
    """
    return Response({
        'message': 'API is running',
        'status': 'success',
        'version': '1.0.0'
    })

@api_view(['POST'])
def analyze_prescription(request):
    """
    Analyze prescription text (dummy implementation for Day 1)
    """
    try:
        prescription_text = request.data.get('text', '')
        
        if not prescription_text:
            return Response({
                'error': 'No prescription text provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Dummy response for Day 1 - will be replaced with actual NLP processing
        dummy_response = {
            'status': 'success',
            'input_text': prescription_text,
            'extracted_medicines': [
                {
                    'name': 'Sample Medicine',
                    'dosage': '500mg',
                    'frequency': 'twice daily',
                    'duration': '7 days'
                }
            ],
            'message': 'Prescription analyzed successfully (dummy response)'
        }
        
        return Response(dummy_response)
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
