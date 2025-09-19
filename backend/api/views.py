from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from .nlp_processor import extract_medicine_info

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
    Analyze prescription text using real NLP processing (Day 2 upgrade)
    """
    try:
        prescription_text = request.data.get('text', '')
        
        if not prescription_text:
            return Response({
                'error': 'No prescription text provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use real NLP processing (Day 2 upgrade)
        nlp_result = extract_medicine_info(prescription_text)
        
        # Format extracted medicines for response
        extracted_medicines = []
        medicines = nlp_result.get('medicines', [])
        dosages = nlp_result.get('dosages', [])
        frequency = nlp_result.get('frequency')
        duration = nlp_result.get('duration')
        
        # Combine medicines with their dosages
        for i, medicine in enumerate(medicines):
            medicine_data = {
                'name': medicine,
                'dosage': dosages[i] if i < len(dosages) else 'Not specified',
                'frequency': frequency or 'Not specified',
                'duration': duration or 'Not specified'
            }
            extracted_medicines.append(medicine_data)
        
        # Calculate confidence score
        confidence = 0
        if medicines:
            confidence += 40
        if dosages:
            confidence += 30
        if frequency:
            confidence += 20
        if duration:
            confidence += 10
        
        response_data = {
            'status': 'success',
            'input_text': prescription_text,
            'extracted_medicines': extracted_medicines,
            'confidence_score': confidence,
            'message': f'Prescription analyzed successfully using NLP (Day 2 upgrade)',
            'nlp_version': '2.0'
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
