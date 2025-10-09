"""
Database-backed views for the Medicine Assistant API
This replaces the in-memory storage with persistent database models
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q
import json
import logging
from datetime import datetime, timedelta

from .models import (
    Medicine, UserProfile, MedicationReminder, 
    PrescriptionHistory, MedicalKnowledge, UserFeedback
)
from .nlp_processor import extract_medicine_info, processor as nlp_processor
from .biobert_processor import BioBERTProcessor

logger = logging.getLogger(__name__)

# Initialize processors
biobert_processor = BioBERTProcessor()


def _get_or_create_user(user_id='default_user'):
    """Get or create a default user for testing"""
    if user_id == 'default_user':
        user, created = User.objects.get_or_create(
            username='default_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Default',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('default_password')
            user.save()
        return user
    else:
        try:
            return User.objects.get(username=user_id)
        except User.DoesNotExist:
            return None


def _get_or_create_profile(user):
    """Get or create user profile"""
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'medical_history': [],
            'allergies': [],
            'current_conditions': [],
            'medications': [],
            'emergency_contact': {},
            'preferences': {}
        }
    )
    return profile


@api_view(['POST'])
def analyze_prescription_with_safety(request):
    """Analyze prescription with safety checks using database"""
    try:
        prescription_text = request.data.get('prescription_text', '')
        user_id = request.data.get('user_id', 'default_user')
        
        if not prescription_text:
            return Response({
                'error': 'Prescription text is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user
        user = _get_or_create_user(user_id)
        if not user:
            return Response({
                'error': f'User {user_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Try BioBERT first, fallback to rule-based
        try:
            extracted_data = biobert_processor.analyze_prescription(prescription_text)
            processing_method = 'BioBERT AI'
            logger.info("BioBERT analysis successful")
        except Exception as e:
            logger.warning(f"BioBERT analysis failed, falling back to rule-based: {e}")
            extracted_data = extract_medicine_info(prescription_text)
            processing_method = 'Rule-based Pattern Matching (Fallback)'
        
        # Process extracted medicines with database lookup
        extracted_medicines = []
        medicines_list = extracted_data.get('medicines', [])
        dosages = extracted_data.get('dosages', [])
        frequency = extracted_data.get('frequency', '')
        duration = extracted_data.get('duration', '')
        
        for i, medicine_item in enumerate(medicines_list):
            if isinstance(medicine_item, dict):
                medicine_name = medicine_item.get('name', '')
                dosage = medicine_item.get('dosage', '')
            else:
                medicine_name = str(medicine_item)
                dosage = dosages[i] if i < len(dosages) else ''
            
            # Get detailed medicine info from database
            detailed_info = _get_detailed_medicine_info_from_db(medicine_name)
            
            medicine_data = {
                'name': medicine_name,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration
            }
            
            # Merge detailed info
            if detailed_info:
                medicine_data.update(detailed_info)
            
            extracted_medicines.append(medicine_data)
        
        # Get user profile for safety checks
        profile = _get_or_create_profile(user)
        
        # Safety analysis
        safety_alerts = _analyze_safety_from_db(extracted_medicines, profile)
        
        # Store prescription history
        prescription_history = PrescriptionHistory.objects.create(
            user=user,
            prescription_text=prescription_text,
            extracted_data=extracted_data,
            analysis_results={
                'medicines': extracted_medicines,
                'safety_alerts': safety_alerts
            },
            safety_alerts=safety_alerts,
            processing_method=processing_method,
            confidence_score=extracted_data.get('confidence_score', 0.8)
        )
        
        # Get database statistics
        total_medicines = Medicine.objects.count()
        total_knowledge = MedicalKnowledge.objects.count()
        
        return Response({
            'status': 'success',
            'extracted_medicines': extracted_medicines,
            'safety_alerts': safety_alerts,
            'processing_method': processing_method,
            'confidence_score': extracted_data.get('confidence_score', 0.8),
            'message': f'Prescription analyzed successfully using {processing_method}',
            'nlp_version': '5.0 (Database-backed)',
            'database_size': total_medicines,
            'medical_knowledge_size': total_knowledge,
            'data_sources': {
                'medicine_extraction': processing_method,
                'medicine_database': f'Database ({total_medicines} medicines)',
                'medical_knowledge': f'Database ({total_knowledge} entries)',
                'safety_analysis': 'Database-backed safety checks'
            },
            'prescription_id': prescription_history.id,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in prescription analysis: {e}")
        return Response({
            'error': f'Analysis failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_detailed_medicine_info_from_db(medicine_name):
    """Get detailed medicine information from database"""
    try:
        if not medicine_name:
            return None
        
        # Clean the medicine name for better matching
        clean_name = medicine_name.lower().strip()
        
        # Try exact match first
        medicine = Medicine.objects.filter(
            Q(name__iexact=medicine_name) |
            Q(generic_name__iexact=medicine_name)
        ).first()
        
        # If no exact match, try partial matches in brand names
        if not medicine:
            medicine = Medicine.objects.filter(
                brand_names__icontains=medicine_name
            ).first()
        
        if medicine:
            return {
                'generic_name': medicine.generic_name,
                'brand_names': medicine.brand_names,
                'category': medicine.category,
                'description': medicine.description,
                'common_doses': medicine.common_doses,
                'side_effects': medicine.side_effects,
                'interactions': medicine.interactions,
                'contraindications': medicine.contraindications,
                'alternatives': medicine.alternatives,
                'cost_analysis': medicine.cost_analysis,
                'molecular_structure': medicine.molecular_structure,
                'medical_explanation': medicine.medical_explanation,
                'data_sources': medicine.data_sources
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting medicine info from database: {e}")
        return None


def _analyze_safety_from_db(medicines, profile):
    """Analyze safety using database information"""
    safety_alerts = []
    
    try:
        user_allergies = profile.allergies or []
        user_conditions = profile.current_conditions or []
        
        for medicine_data in medicines:
            medicine_name = medicine_data.get('name', '')
            medicine = Medicine.objects.filter(
                Q(name__iexact=medicine_name) |
                Q(generic_name__iexact=medicine_name) |
                Q(brand_names__icontains=medicine_name)
            ).first()
            
            if medicine:
                # Check allergies
                for allergy in user_allergies:
                    if allergy.lower() in str(medicine.contraindications).lower():
                        safety_alerts.append({
                            'type': 'allergy_warning',
                            'severity': 'high',
                            'medicine': medicine_name,
                            'message': f'⚠️ ALLERGY WARNING: {medicine_name} may contain {allergy}',
                            'recommendation': 'Consult your doctor before taking this medication'
                        })
                
                # Check interactions
                if medicine.interactions:
                    safety_alerts.append({
                        'type': 'interaction_warning',
                        'severity': 'medium',
                        'medicine': medicine_name,
                        'message': f'⚠️ DRUG INTERACTION: {medicine_name} may interact with other medications',
                        'interactions': medicine.interactions[:3]  # Show first 3
                    })
                
                # Check contraindications
                if medicine.contraindications:
                    for condition in user_conditions:
                        if condition.lower() in str(medicine.contraindications).lower():
                            safety_alerts.append({
                                'type': 'contraindication_warning',
                                'severity': 'high',
                                'medicine': medicine_name,
                                'message': f'⚠️ CONTRAINDICATION: {medicine_name} may not be suitable for {condition}',
                                'recommendation': 'Consult your doctor before taking this medication'
                            })
    
    except Exception as e:
        logger.error(f"Error in safety analysis: {e}")
    
    return safety_alerts


@api_view(['POST'])
def create_medication_reminder(request):
    """Create medication reminder using database"""
    try:
        user_id = request.data.get('user_id', 'default_user')
        medicine_name = request.data.get('medicine_name', '')
        dosage = request.data.get('dosage', '')
        frequency = request.data.get('frequency', 'daily')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        reminder_times = request.data.get('reminder_times', [])
        notes = request.data.get('notes', '')
        
        if not medicine_name:
            return Response({
                'error': 'Medicine name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user
        user = _get_or_create_user(user_id)
        if not user:
            return Response({
                'error': f'User {user_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start_date = timezone.now()
        
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Create reminder
        reminder = MedicationReminder.objects.create(
            user=user,
            medicine_name=medicine_name,
            dosage=dosage,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            reminder_times=reminder_times,
            notes=notes,
            active=True
        )
        
        return Response({
            'status': 'success',
            'message': 'Medication reminder created successfully',
            'reminder': {
                'id': reminder.id,
                'medicine_name': reminder.medicine_name,
                'dosage': reminder.dosage,
                'frequency': reminder.frequency,
                'start_date': reminder.start_date.isoformat(),
                'end_date': reminder.end_date.isoformat() if reminder.end_date else None,
                'reminder_times': reminder.reminder_times,
                'notes': reminder.notes,
                'active': reminder.active,
                'created_at': reminder.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        return Response({
            'error': f'Failed to create reminder: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_medication_reminders(request):
    """Get user's medication reminders from database"""
    try:
        user_id = request.GET.get('user_id', 'default_user')
        
        # Get user
        user = _get_or_create_user(user_id)
        if not user:
            return Response({
                'error': f'User {user_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get reminders
        reminders = MedicationReminder.objects.filter(user=user).order_by('-created_at')
        
        reminder_list = []
        for reminder in reminders:
            reminder_list.append({
                'id': reminder.id,
                'medicine_name': reminder.medicine_name,
                'dosage': reminder.dosage,
                'frequency': reminder.frequency,
                'start_date': reminder.start_date.isoformat(),
                'end_date': reminder.end_date.isoformat() if reminder.end_date else None,
                'reminder_times': reminder.reminder_times,
                'notes': reminder.notes,
                'active': reminder.active,
                'created_at': reminder.created_at.isoformat(),
                'updated_at': reminder.updated_at.isoformat()
            })
        
        return Response({
            'status': 'success',
            'reminders': reminder_list,
            'total_count': len(reminder_list),
            'active_count': len([r for r in reminder_list if r['active']])
        })
        
    except Exception as e:
        logger.error(f"Error getting reminders: {e}")
        return Response({
            'error': f'Failed to get reminders: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_medicine_info(request, medicine_id):
    """Get detailed medicine information from database"""
    try:
        # Try to find medicine by ID or name
        medicine = None
        
        # First try by ID
        if medicine_id.isdigit():
            medicine = Medicine.objects.filter(id=int(medicine_id)).first()
        
        # If not found by ID, try by name
        if not medicine:
            medicine = Medicine.objects.filter(
                Q(name__iexact=medicine_id) |
                Q(generic_name__iexact=medicine_id) |
                Q(brand_names__icontains=medicine_id)
            ).first()
        
        if not medicine:
            return Response({
                'error': f'Medicine not found: {medicine_id}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'status': 'success',
            'medicine': {
                'id': medicine.id,
                'name': medicine.name,
                'generic_name': medicine.generic_name,
                'brand_names': medicine.brand_names,
                'category': medicine.category,
                'description': medicine.description,
                'common_doses': medicine.common_doses,
                'side_effects': medicine.side_effects,
                'interactions': medicine.interactions,
                'contraindications': medicine.contraindications,
                'alternatives': medicine.alternatives,
                'cost_analysis': medicine.cost_analysis,
                'molecular_structure': medicine.molecular_structure,
                'medical_explanation': medicine.medical_explanation,
                'data_sources': medicine.data_sources,
                'created_at': medicine.created_at.isoformat(),
                'updated_at': medicine.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting medicine info: {e}")
        return Response({
            'error': f'Failed to get medicine info: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def search_medical_knowledge(request):
    """Search medical knowledge database"""
    try:
        query = request.GET.get('query', '')
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return Response({
                'error': 'Query parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in medical knowledge database
        knowledge_entries = MedicalKnowledge.objects.filter(
            Q(term__icontains=query) |
            Q(explanation__icontains=query) |
            Q(category__icontains=query)
        ).order_by('term')[:limit]
        
        results = []
        for entry in knowledge_entries:
            results.append({
                'term': entry.term,
                'explanation': entry.explanation,
                'category': entry.category,
                'related_terms': entry.related_terms,
                'source': entry.source,
                'created_at': entry.created_at.isoformat()
            })
        
        return Response({
            'status': 'success',
            'query': query,
            'results': results,
            'total_found': len(results),
            'database_size': MedicalKnowledge.objects.count()
        })
        
    except Exception as e:
        logger.error(f"Error searching medical knowledge: {e}")
        return Response({
            'error': f'Search failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_medical_explanation(request, medicine_name):
    """Get detailed medical explanation for a medicine from database"""
    try:
        # Try to find medicine in database
        medicine = Medicine.objects.filter(
            Q(name__iexact=medicine_name) |
            Q(generic_name__iexact=medicine_name) |
            Q(brand_names__icontains=medicine_name)
        ).first()
        
        if not medicine:
            return Response({
                'error': f'Medicine not found: {medicine_name}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'status': 'success',
            'medicine_name': medicine.name,
            'medical_explanation': medicine.medical_explanation,
            'description': medicine.description,
            'category': medicine.category,
            'side_effects': medicine.side_effects,
            'interactions': medicine.interactions,
            'contraindications': medicine.contraindications,
            'alternatives': medicine.alternatives,
            'data_sources': medicine.data_sources
        })
        
    except Exception as e:
        logger.error(f"Error getting medical explanation: {e}")
        return Response({
            'error': f'Failed to get explanation: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_medical_knowledge_stats(request):
    """Get statistics about the medical knowledge database"""
    try:
        medicine_count = Medicine.objects.count()
        knowledge_count = MedicalKnowledge.objects.count()
        reminder_count = MedicationReminder.objects.count()
        prescription_count = PrescriptionHistory.objects.count()
        
        return Response({
            'status': 'success',
            'database_statistics': {
                'total_medicines': medicine_count,
                'total_medical_knowledge_entries': knowledge_count,
                'total_medication_reminders': reminder_count,
                'total_prescription_analyses': prescription_count,
                'database_last_updated': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return Response({
            'error': f'Failed to get stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
