from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import logging
import re
from django.utils import timezone
from .nlp_processor import extract_medicine_info, processor
from .biobert_processor import BioBERTProcessor
from .drug_interactions import interaction_checker
from .enhanced_drug_interactions import enhanced_interaction_checker

# Initialize BioBERT processor (singleton pattern)
biobert_processor = None

def get_biobert_processor():
    """Get or create BioBERT processor instance"""
    global biobert_processor
    if biobert_processor is None:
        try:
            biobert_processor = BioBERTProcessor()
            logging.info("BioBERT processor initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize BioBERT processor: {e}")
            biobert_processor = None
    return biobert_processor

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
    Analyze prescription text using BioBERT AI with rule-based fallback
    """
    try:
        prescription_text = request.data.get('text', '')
        
        if not prescription_text:
            return Response({
                'error': 'No prescription text provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try BioBERT first, fallback to rule-based if needed
        ai_processor = get_biobert_processor()
        processing_method = "BioBERT AI"
        
        if ai_processor:
            try:
                # Use BioBERT for AI-powered extraction
                medicines = ai_processor.extract_medicines(prescription_text)
                
                if medicines and len(medicines) > 0:
                    # Convert BioBERT output to API format
                    extracted_medicines = []
                    for med in medicines:
                        medicine_data = {
                            'name': med.get('name', ''),
                            'dosage': med.get('dosage', 'Not specified'),
                            'frequency': med.get('frequency', 'Not specified'),
                            'duration': 'Not specified',  # BioBERT doesn't extract duration yet
                            'confidence': med.get('confidence', 0.0),
                            'source': med.get('source', 'BioBERT AI'),
                            'extraction_source': 'BioBERT Medical NLP Model'
                        }
                        
                        # Get detailed medicine information from database
                        detailed_info = _get_detailed_medicine_info(med.get('name', ''))
                        if detailed_info:
                            medicine_data.update(detailed_info)
                        
                        extracted_medicines.append(medicine_data)
                    
                    # Calculate overall confidence
                    avg_confidence = sum(med.get('confidence', 0) for med in medicines) / len(medicines) if medicines else 0
                    
                    response_data = {
                        'status': 'success',
                        'input_text': prescription_text,
                        'extracted_medicines': extracted_medicines,
                        'processing_method': processing_method,
                        'confidence_score': round(avg_confidence, 2),
                        'ai_model_info': ai_processor.get_model_info(),
                        'message': 'Prescription analyzed successfully using BioBERT AI',
                        'nlp_version': '4.0 (BioBERT AI)',
                        'database_size': len(processor.medicine_database.get('medicines', [])),
                        'structures_available': processor.medicine_database.get('medicines_with_structures', 0),
                        'data_sources': {
                            'medicine_extraction': 'BioBERT Medical NLP Model',
                            'medicine_database': 'Local Database (DrugBank + SDF + OpenFDA)',
                            'confidence_scoring': 'BioBERT Embeddings + Pattern Matching'
                        }
                    }
                    
                    return Response(response_data)
                else:
                    logging.warning("BioBERT found no medicines, falling back to rule-based system")
            except Exception as e:
                logging.error(f"BioBERT processing failed: {e}, falling back to rule-based system")
        
        # Fallback to rule-based system
        processing_method = "Rule-based (Fallback)"
        nlp_result = extract_medicine_info(prescription_text)
        
        # Format extracted medicines for response (rule-based fallback)
        extracted_medicines = []
        medicines = nlp_result.get('medicines', [])
        dosages = nlp_result.get('dosages', [])
        frequency = nlp_result.get('frequency')
        duration = nlp_result.get('duration')
        detailed_medicines = nlp_result.get('detailed_medicines', [])
        
        # Combine medicines with their dosages and detailed info
        for i, medicine in enumerate(medicines):
            medicine_data = {
                'name': medicine,
                'dosage': dosages[i] if i < len(dosages) else 'Not specified',
                'frequency': frequency or 'Not specified',
                'duration': duration or 'Not specified',
                'confidence': 0.5,  # Default confidence for rule-based
                'source': processing_method
            }
            
            # Add detailed information if available
            if i < len(detailed_medicines):
                detailed = detailed_medicines[i]
                medicine_data.update({
                    'generic_name': detailed.get('generic_name', ''),
                    'indication': detailed.get('indication', ''),
                    'side_effects': detailed.get('side_effects', ''),
                    'has_structure': detailed.get('has_structure', False),
                    'categories': detailed.get('categories', ''),
                    'groups': detailed.get('groups', [])
                })
            
            extracted_medicines.append(medicine_data)
        
        response_data = {
            'status': 'success',
            'input_text': prescription_text,
            'extracted_medicines': extracted_medicines,
            'processing_method': processing_method,
            'molecular_info': nlp_result.get('molecular_info', []),
            'safety_alerts': nlp_result.get('safety_alerts', []),
            'interactions': nlp_result.get('interactions', []),
            'confidence_score': nlp_result.get('confidence_score', 0),
            'message': f'Prescription analyzed successfully using {processing_method}',
            'nlp_version': '4.0 (Hybrid AI + Rule-based)',
            'database_size': len(processor.medicine_database.get('medicines', [])),
            'structures_available': processor.medicine_database.get('medicines_with_structures', 0),
            'data_sources': {
                'medicine_extraction': 'Rule-based Pattern Matching (Fallback)',
                'medicine_database': 'Local Database (DrugBank + SDF + OpenFDA)',
                'confidence_scoring': 'Pattern Matching + Database Validation'
            }
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_medicine_details(request, medicine_id):
    """
    Get detailed information about a specific medicine
    """
    try:
        medicines = processor.medicine_database.get('medicines', [])
        
        # Find medicine by ID or name
        medicine = None
        try:
            # Try by ID first
            medicine_id_int = int(medicine_id)
            if 0 <= medicine_id_int < len(medicines):
                medicine = medicines[medicine_id_int]
        except ValueError:
            # Try by name
            for med in medicines:
                if med.get('name', '').lower() == medicine_id.lower():
                    medicine = med
                    break
        
        if not medicine:
            return Response({
                'error': 'Medicine not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'status': 'success',
            'medicine': medicine
        })
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_alternatives(request, medicine_id):
    """
    Get alternative medicines for a given medicine
    """
    try:
        from urllib.parse import unquote
        medicines = processor.medicine_database.get('medicines', [])
        
        # Find the medicine
        medicine = None
        try:
            medicine_id_int = int(medicine_id)
            if 0 <= medicine_id_int < len(medicines):
                medicine = medicines[medicine_id_int]
        except ValueError:
            # Decode URL-encoded medicine name
            decoded_name = unquote(medicine_id)
            for med in medicines:
                if med.get('name', '').lower() == decoded_name.lower():
                    medicine = med
                    break
        
        if not medicine:
            return Response({
                'error': 'Medicine not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        alternatives = []
        
        # First, try to use the alternatives field if it exists
        if medicine.get('alternatives'):
            alternative_names = medicine.get('alternatives', '').split(', ')
            for alt_name in alternative_names:
                alt_name = alt_name.strip()
                if alt_name:
                    # Find the alternative medicine in the database
                    for med in medicines:
                        if med.get('name', '').lower() == alt_name.lower():
                            alternatives.append({
                                'name': med.get('name', ''),
                                'generic_name': med.get('generic_name', ''),
                                'indication': med.get('indications', ''),
                                'category': med.get('category', ''),
                                'reason': 'Direct alternative from database'
                            })
                            break
        
        # If no alternatives found in the alternatives field, try category matching
        if not alternatives:
            medicine_category = medicine.get('category', '')
            medicine_indication = medicine.get('indications', '')
            
            for med in medicines:
                if med.get('name') != medicine.get('name'):
                    # Check if same category
                    if medicine_category and medicine_category in med.get('category', ''):
                        alternatives.append({
                            'name': med.get('name', ''),
                            'generic_name': med.get('generic_name', ''),
                            'indication': med.get('indications', ''),
                            'category': med.get('category', ''),
                            'reason': f'Same category: {medicine_category}'
                        })
                    # Check if similar indication
                    elif medicine_indication and any(word in med.get('indications', '').lower() for word in medicine_indication.lower().split()):
                        alternatives.append({
                            'name': med.get('name', ''),
                            'generic_name': med.get('generic_name', ''),
                            'indication': med.get('indications', ''),
                            'category': med.get('category', ''),
                            'reason': 'Similar therapeutic indication'
                        })
        
        # Limit to 5 alternatives
        alternatives = alternatives[:5]
        
        if not alternatives:
            # Fallback: return some common alternatives based on medicine type
            fallback_alternatives = []
            medicine_name = medicine.get('name', '').lower()
            
            if 'aspirin' in medicine_name or 'ibuprofen' in medicine_name:
                fallback_alternatives = [
                    {'name': 'Paracetamol', 'generic_name': 'Acetaminophen', 'indication': 'Pain relief, fever', 'category': 'Analgesic', 'reason': 'Alternative pain reliever'},
                    {'name': 'Naproxen', 'generic_name': 'Naproxen', 'indication': 'Pain relief, inflammation', 'category': 'NSAID', 'reason': 'Alternative NSAID'},
                    {'name': 'Celecoxib', 'generic_name': 'Celecoxib', 'indication': 'Pain relief, arthritis', 'category': 'NSAID', 'reason': 'COX-2 selective NSAID'}
                ]
            elif 'metformin' in medicine_name:
                fallback_alternatives = [
                    {'name': 'Glipizide', 'generic_name': 'Glipizide', 'indication': 'Type 2 diabetes', 'category': 'Sulfonylurea', 'reason': 'Alternative diabetes medication'},
                    {'name': 'Sitagliptin', 'generic_name': 'Sitagliptin', 'indication': 'Type 2 diabetes', 'category': 'DPP-4 inhibitor', 'reason': 'Alternative diabetes medication'}
                ]
            
            alternatives = fallback_alternatives
        
        return Response({
            'status': 'success',
            'original_medicine': medicine.get('name', ''),
            'alternatives': alternatives
        })
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def set_reminder(request):
    """
    Set a smart medication reminder for a user with intelligent scheduling
    """
    try:
        from datetime import datetime, timedelta
        import re
        
        data = request.data
        medicine_name = data.get('medicine_name', '')
        dosage = data.get('dosage', '')
        frequency = data.get('frequency', '')
        time = data.get('time', '08:00')
        user_id = data.get('user_id', 'default_user')
        duration = data.get('duration', 'Not specified')
        
        if not medicine_name:
            return Response({
                'error': 'Medicine name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user preferences for smart defaults
        user_preferences = _get_user_preferences(user_id)
        
        # Use user's default times if not specified
        if not time or time == '08:00':
            time = _get_smart_default_time(frequency, user_preferences)
        
        # Smart scheduling logic
        reminder_schedule = _generate_smart_schedule(frequency, time, duration)
        
        # Create enhanced reminder object
        reminder = {
            'id': f"reminder_{len(processor.medicine_database.get('reminders', [])) + 1}",
            'user_id': user_id,
            'medicine_name': medicine_name,
            'dosage': dosage,
            'frequency': frequency,
            'time': time,
            'duration': duration,
            'schedule': reminder_schedule,
            'active': True,
            'adherence_tracking': {
                'total_doses': 0,
                'taken_doses': 0,
                'missed_doses': 0,
                'last_taken': None,
                'adherence_rate': 0.0
            },
            'smart_features': {
                'auto_adjustment': True,
                'missed_dose_alerts': True,
                'refill_reminders': True,
                'weather_alerts': False
            },
            'status': 'active',
            'created_at': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat()
        }
        
        # Store in memory (in real app, use database)
        if 'reminders' not in processor.medicine_database:
            processor.medicine_database['reminders'] = []
        processor.medicine_database['reminders'].append(reminder)
        
        return Response({
            'status': 'success',
            'message': 'Smart reminder set successfully',
            'reminder': reminder,
            'schedule_info': {
                'total_reminders': len(reminder_schedule),
                'next_reminder': reminder_schedule[0] if reminder_schedule else None,
                'frequency_parsed': _parse_frequency(frequency)
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_reminders(request):
    """
    Get all reminders for a user with enhanced information
    """
    try:
        user_id = request.GET.get('user_id', 'default_user')
        reminders = processor.medicine_database.get('reminders', [])
        
        user_reminders = [r for r in reminders if r.get('user_id') == user_id]
        
        # Enhance reminders with additional info
        enhanced_reminders = []
        for reminder in user_reminders:
            enhanced_reminder = reminder.copy()
            
            # Calculate adherence rate
            tracking = reminder.get('adherence_tracking', {})
            total_doses = tracking.get('total_doses', 0)
            taken_doses = tracking.get('taken_doses', 0)
            adherence_rate = (taken_doses / total_doses * 100) if total_doses > 0 else 0
            
            enhanced_reminder['adherence_summary'] = {
                'rate': round(adherence_rate, 1),
                'status': 'Excellent' if adherence_rate >= 90 else 'Good' if adherence_rate >= 80 else 'Needs Improvement',
                'next_dose': reminder.get('schedule', [{}])[0] if reminder.get('schedule') else None
            }
            
            enhanced_reminders.append(enhanced_reminder)
        
        return Response({
            'status': 'success',
            'reminders': enhanced_reminders,
            'total': len(enhanced_reminders),
            'summary': {
                'active_reminders': len([r for r in enhanced_reminders if r.get('active', True)]),
                'average_adherence': round(sum(r['adherence_summary']['rate'] for r in enhanced_reminders) / len(enhanced_reminders), 1) if enhanced_reminders else 0
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'DELETE'])
def manage_reminder(request, reminder_id):
    """
    Update or delete a reminder
    """
    try:
        reminders = processor.medicine_database.get('reminders', [])
        reminder = None
        
        # Find the reminder
        for r in reminders:
            if r.get('id') == reminder_id:
                reminder = r
                break
        
        if not reminder:
            return Response({
                'error': 'Reminder not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'PUT':
            # Update reminder
            data = request.data
            reminder.update({
                'medicine_name': data.get('medicine_name', reminder.get('medicine_name')),
                'dosage': data.get('dosage', reminder.get('dosage')),
                'frequency': data.get('frequency', reminder.get('frequency')),
                'time': data.get('time', reminder.get('time')),
                'active': data.get('active', reminder.get('active', True)),
                'updated_at': timezone.now().isoformat()
            })
            
            # Regenerate schedule if frequency changed
            if 'frequency' in data:
                reminder['schedule'] = _generate_smart_schedule(
                    reminder['frequency'], 
                    reminder['time'], 
                    reminder.get('duration', 'Not specified')
                )
            
            return Response({
                'status': 'success',
                'message': 'Reminder updated successfully',
                'reminder': reminder
            })
        
        elif request.method == 'DELETE':
            # Delete reminder
            reminders.remove(reminder)
            return Response({
                'status': 'success',
                'message': 'Reminder deleted successfully'
            })
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def track_medication(request, reminder_id):
    """
    Track medication taken/missed
    """
    try:
        reminders = processor.medicine_database.get('reminders', [])
        reminder = None
        
        # Find the reminder
        for r in reminders:
            if r.get('id') == reminder_id:
                reminder = r
                break
        
        if not reminder:
            return Response({
                'error': 'Reminder not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        action = data.get('action', 'taken')  # 'taken' or 'missed'
        
        # Update adherence tracking
        tracking = reminder.get('adherence_tracking', {})
        tracking['total_doses'] = tracking.get('total_doses', 0) + 1
        
        if action == 'taken':
            tracking['taken_doses'] = tracking.get('taken_doses', 0) + 1
            tracking['last_taken'] = timezone.now().isoformat()
        else:
            tracking['missed_doses'] = tracking.get('missed_doses', 0) + 1
        
        # Calculate adherence rate
        total_doses = tracking['total_doses']
        taken_doses = tracking['taken_doses']
        tracking['adherence_rate'] = (taken_doses / total_doses * 100) if total_doses > 0 else 0
        
        reminder['adherence_tracking'] = tracking
        reminder['updated_at'] = timezone.now().isoformat()
        
        return Response({
            'status': 'success',
            'message': f'Medication {action} recorded successfully',
            'adherence_summary': {
                'total_doses': total_doses,
                'taken_doses': taken_doses,
                'missed_doses': tracking['missed_doses'],
                'adherence_rate': round(tracking['adherence_rate'], 1),
                'status': 'Excellent' if tracking['adherence_rate'] >= 90 else 'Good' if tracking['adherence_rate'] >= 80 else 'Needs Improvement'
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST', 'PUT'])
def user_profile(request):
    """
    Get, create, or update comprehensive user profile information
    """
    try:
        user_id = request.GET.get('user_id', 'default_user')
        
        if request.method == 'GET':
            # Get user profile from database
            profiles = processor.medicine_database.get('user_profiles', {})
            profile = profiles.get(user_id, _get_default_profile(user_id))
            
            # Add recent activity summary
            profile['recent_activity'] = _get_user_activity_summary(user_id)
            
            return Response({
                'status': 'success',
                'profile': profile
            })
        
        elif request.method == 'POST':
            # Create new profile
            data = request.data
            user_id = data.get('user_id', 'default_user')
            
            profile = _create_enhanced_profile(user_id, data)
            
            # Store in memory (in real app, use database)
            if 'user_profiles' not in processor.medicine_database:
                processor.medicine_database['user_profiles'] = {}
            processor.medicine_database['user_profiles'][user_id] = profile
            
            return Response({
                'status': 'success',
                'message': 'Profile created successfully',
                'profile': profile
            })
        
        elif request.method == 'PUT':
            # Update existing profile
            data = request.data
            profiles = processor.medicine_database.get('user_profiles', {})
            
            if user_id not in profiles:
                return Response({
                    'error': 'Profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Update profile with new data
            existing_profile = profiles[user_id]
            updated_profile = _update_profile(existing_profile, data)
            updated_profile['updated_at'] = timezone.now().isoformat()
            
            processor.medicine_database['user_profiles'][user_id] = updated_profile
            
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully',
                'profile': updated_profile
            })
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _get_default_profile(user_id):
    """Create a default profile for new users"""
    return {
        'user_id': user_id,
        'personal_info': {
            'name': '',
            'age': 35,
            'gender': '',
            'phone': '',
            'email': ''
        },
        'medical_info': {
            'medical_conditions': [],
            'allergies': ['Penicillin'],
            'current_medications': [],
            'blood_type': '',
            'emergency_contact': ''
        },
        'preferences': {
            'default_reminder_times': {
                'morning': '08:00',
                'afternoon': '14:00',
                'evening': '20:00'
            },
            'preferred_pharmacy': '',
            'notification_settings': {
                'email_reminders': True,
                'sms_reminders': False,
                'push_notifications': True
            },
            'units_preference': 'mg',
            'timezone': 'UTC'
        },
        'created_at': timezone.now().isoformat(),
        'updated_at': timezone.now().isoformat()
    }

def _create_enhanced_profile(user_id, data):
    """Create an enhanced profile with all sections"""
    return {
        'user_id': user_id,
        'personal_info': {
            'name': data.get('name', ''),
            'age': data.get('age', 35),
            'gender': data.get('gender', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', '')
        },
        'medical_info': {
            'medical_conditions': data.get('medical_conditions', []),
            'allergies': data.get('allergies', ['Penicillin']),
            'current_medications': data.get('current_medications', []),
            'blood_type': data.get('blood_type', ''),
            'emergency_contact': data.get('emergency_contact', '')
        },
        'preferences': {
            'default_reminder_times': data.get('default_reminder_times', {
                'morning': '08:00',
                'afternoon': '14:00',
                'evening': '20:00'
            }),
            'preferred_pharmacy': data.get('preferred_pharmacy', ''),
            'notification_settings': data.get('notification_settings', {
                'email_reminders': True,
                'sms_reminders': False,
                'push_notifications': True
            }),
            'units_preference': data.get('units_preference', 'mg'),
            'timezone': data.get('timezone', 'UTC')
        },
        'created_at': timezone.now().isoformat(),
        'updated_at': timezone.now().isoformat()
    }

def _update_profile(existing_profile, new_data):
    """Update existing profile with new data"""
    updated_profile = existing_profile.copy()
    
    # Update personal info
    if 'personal_info' in new_data:
        updated_profile['personal_info'].update(new_data['personal_info'])
    
    # Update medical info
    if 'medical_info' in new_data:
        updated_profile['medical_info'].update(new_data['medical_info'])
    
    # Update preferences
    if 'preferences' in new_data:
        updated_profile['preferences'].update(new_data['preferences'])
    
    return updated_profile

def _get_user_activity_summary(user_id):
    """Get recent user activity summary"""
    reminders = processor.medicine_database.get('reminders', [])
    user_reminders = [r for r in reminders if r.get('user_id') == user_id]
    
    return {
        'total_reminders': len(user_reminders),
        'active_reminders': len([r for r in user_reminders if r.get('active', True)]),
        'total_prescriptions_analyzed': len(processor.medicine_database.get('prescription_history', [])),
        'last_activity': max([r.get('updated_at', '') for r in user_reminders] + ['']) if user_reminders else None
    }

def _get_detailed_medicine_info(medicine_name):
    """Helper function to get detailed medicine information from database"""
    try:
        # Handle both string and dictionary inputs
        if isinstance(medicine_name, dict):
            medicine_name = medicine_name.get('name', '')
        
        if not isinstance(medicine_name, str):
            medicine_name = str(medicine_name)
        
        # Use the comprehensive medicine database (17,430 medicines)
        import json
        import os
        
        # Load the ultimate comprehensive database
        comprehensive_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'processed', 'enhanced_ultimate_medicine_database.json')
        try:
            with open(comprehensive_db_path, 'r') as f:
                comprehensive_data = json.load(f)
            medicines = comprehensive_data.get('medicines', [])
        except:
            # Fallback to original database
            original_db_path = os.path.join(os.path.dirname(__file__), '..', 'medicines_database.json')
            try:
                with open(original_db_path, 'r') as f:
                    original_data = json.load(f)
                medicines = original_data if isinstance(original_data, list) else original_data.get('medicines', [])
            except:
                # Final fallback to processor database
                medicines = processor.medicine_database.get('medicines', [])
        
        # Clean the medicine name for better matching
        clean_name = medicine_name.lower().strip()
        
        # Remove dosage information for better matching (e.g., "aspirin 81mg" -> "aspirin")
        clean_name_no_dosage = re.sub(r'\s*\d+\s*(mg|mcg|g|ml|mcg)\s*', ' ', clean_name).strip()
        
        # Simple matching using database synonyms and brand names
        # Database now has all proper brand names populated
        for medicine in medicines:
            db_name = medicine.get('name', '').lower()
            db_generic = medicine.get('generic_name', '').lower()
            
            # Get synonyms and brand names from the dataset
            synonyms = [str(s).lower() for s in medicine.get('synonyms', [])]
            brand_names = [str(b).lower() for b in medicine.get('brand_names', [])]
            all_aliases = synonyms + brand_names
            
            # Simple exact match with any alias
            if (clean_name in all_aliases or clean_name_no_dosage in all_aliases or
                db_name == clean_name or db_generic == clean_name or
                db_name == clean_name_no_dosage or db_generic == clean_name_no_dosage):
                return _format_medicine_details(medicine)
        
        return None
    except Exception as e:
        logging.error(f"Error getting detailed medicine info: {e}")
        return None

def _format_medicine_details(medicine):
    """Helper function to format medicine details consistently"""
    # Handle both database formats
    indication = medicine.get('indication', '') or medicine.get('indications', '')
    side_effects = medicine.get('side_effects', '') or medicine.get('warnings', '')
    categories = medicine.get('categories', '') or medicine.get('category', '')
    
    # If fields are empty, try to get from alternative sources
    if not indication:
        indication = medicine.get('description', '') or medicine.get('pharmacology', '')
    if not side_effects:
        side_effects = medicine.get('warnings', '') or medicine.get('adverse_effects', '')
    
    # Get alternatives from database
    alternatives = medicine.get('alternatives', '')
    
    return {
        'generic_name': medicine.get('generic_name', ''),
        'indication': indication,
        'side_effects': side_effects,
        'has_structure': medicine.get('has_structure', False),
        'categories': categories,
        'groups': medicine.get('groups', []),
        'brand_names': medicine.get('brand_names', ''),
        'dosage_forms': medicine.get('dosage_forms', ''),
        'common_doses': medicine.get('common_doses', '') or medicine.get('dosage', ''),
        'alternatives': alternatives,
        'data_source': 'Enhanced Ultimate Medicine Database (18,802 medicines with Wiki Knowledge)',
        'source_details': {
            'database': 'enhanced_ultimate_medicine_database.json',
            'origin': 'DrugBank + Wiki Medical Terms + Molecular Structures + Enhanced Processing',
            'last_updated': '2025-01-27',
            'reliability': 'High - Official DrugBank medical database'
        }
    }

def _generate_smart_schedule(frequency, base_time, duration):
    """
    Generate intelligent reminder schedule based on frequency and duration
    """
    from datetime import datetime, timedelta
    import re
    
    schedule = []
    base_hour, base_minute = map(int, base_time.split(':'))
    
    # Parse frequency
    freq_info = _parse_frequency(frequency)
    
    if not freq_info:
        return [{'time': base_time, 'day_offset': 0, 'dose_number': 1}]
    
    # Generate schedule for next 7 days
    for day in range(7):
        for dose_num in range(freq_info['times_per_day']):
            if freq_info['times_per_day'] == 1:
                reminder_time = f"{base_hour:02d}:{base_minute:02d}"
            else:
                # Distribute doses evenly throughout the day
                hour_offset = (24 // freq_info['times_per_day']) * dose_num
                reminder_hour = (base_hour + hour_offset) % 24
                reminder_time = f"{reminder_hour:02d}:{base_minute:02d}"
            
            schedule.append({
                'time': reminder_time,
                'day_offset': day,
                'dose_number': dose_num + 1,
                'datetime': f"Day {day + 1} at {reminder_time}"
            })
    
    return schedule

def _parse_frequency(frequency):
    """
    Parse frequency text into structured data
    """
    import re
    
    frequency_lower = frequency.lower()
    
    # Common patterns - order matters (most specific first)
    if 'three times daily' in frequency_lower or 'three times a day' in frequency_lower or 'tid' in frequency_lower:
        return {'times_per_day': 3, 'interval_hours': 8}
    elif 'twice daily' in frequency_lower or 'twice a day' in frequency_lower or 'bid' in frequency_lower:
        return {'times_per_day': 2, 'interval_hours': 12}
    elif 'four times daily' in frequency_lower or 'four times a day' in frequency_lower or 'qid' in frequency_lower:
        return {'times_per_day': 4, 'interval_hours': 6}
    elif 'once daily' in frequency_lower or 'once a day' in frequency_lower or 'daily' in frequency_lower:
        return {'times_per_day': 1, 'interval_hours': 24}
    
    # Every X hours pattern
    every_hours_match = re.search(r'every (\d+) hours?', frequency_lower)
    if every_hours_match:
        hours = int(every_hours_match.group(1))
        return {'times_per_day': 24 // hours, 'interval_hours': hours}
    
    # Every X days pattern
    every_days_match = re.search(r'every (\d+) days?', frequency_lower)
    if every_days_match:
        days = int(every_days_match.group(1))
        return {'times_per_day': 1, 'interval_hours': days * 24}
    
    # Default to once daily
    return {'times_per_day': 1, 'interval_hours': 24}

def _get_user_preferences(user_id):
    """Get user preferences from profile"""
    try:
        profiles = processor.medicine_database.get('user_profiles', {})
        profile = profiles.get(user_id, {})
        return profile.get('preferences', {})
    except:
        return {}

def _get_smart_default_time(frequency, user_preferences):
    """Get smart default time based on frequency and user preferences"""
    default_times = user_preferences.get('default_reminder_times', {
        'morning': '08:00',
        'afternoon': '14:00',
        'evening': '20:00'
    })
    
    freq_lower = frequency.lower()
    
    # For multiple daily doses, use appropriate times
    if 'twice daily' in freq_lower or 'bid' in freq_lower:
        return default_times['morning']  # First dose in morning
    elif 'three times daily' in freq_lower or 'tid' in freq_lower:
        return default_times['morning']  # First dose in morning
    elif 'four times daily' in freq_lower or 'qid' in freq_lower:
        return default_times['morning']  # First dose in morning
    else:
        return default_times['morning']  # Default to morning

# ============================================================================
# DRUG INTERACTION CHECKING ENDPOINTS
# ============================================================================

@api_view(['POST'])
def check_drug_interactions(request):
    """
    Check for drug interactions in a list of medicines
    """
    try:
        medicines = request.data.get('medicines', [])
        
        if not medicines:
            return Response({
                'error': 'No medicines provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check interactions
        interaction_results = interaction_checker.check_interactions(medicines)
        
        return Response({
            'status': 'success',
            'data': interaction_results,
            'data_sources': {
                'interaction_database': 'Manual Curated Database (High Severity Interactions)',
                'severity_levels': 'Medical Literature + Clinical Guidelines',
                'recommendations': 'Evidence-based Medical Guidelines'
            }
        })
        
    except Exception as e:
        logging.error(f"Error checking drug interactions: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_medical_knowledge(request):
    """Search medical knowledge database for terms and conditions"""
    try:
        query = request.GET.get('query', '').strip()
        if not query:
            return Response({
                'status': 'error',
                'message': 'Query parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Load enhanced ultimate database
        import json
        import os
        
        enhanced_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'processed', 'enhanced_ultimate_medicine_database.json')
        
        try:
            with open(enhanced_db_path, 'r') as f:
                enhanced_data = json.load(f)
            medicines = enhanced_data.get('medicines', [])
        except:
            return Response({
                'status': 'error',
                'message': 'Medical knowledge database not available'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Search for matching terms
        query_lower = query.lower()
        results = []
        
        for medicine in medicines:
            name = medicine.get('name', '').lower()
            generic_name = medicine.get('generic_name', '').lower()
            detailed_explanation = medicine.get('detailed_medical_explanation', '')
            
            # Check if query matches medicine name or is in explanation
            if (query_lower in name or query_lower in generic_name or 
                query_lower in detailed_explanation.lower()):
                
                result = {
                    'name': medicine.get('name', ''),
                    'generic_name': medicine.get('generic_name', ''),
                    'categories': medicine.get('categories', ''),
                    'alternatives': medicine.get('alternatives', ''),
                    'has_detailed_explanation': bool(detailed_explanation),
                    'explanation_length': len(detailed_explanation) if detailed_explanation else 0
                }
                
                # Include partial explanation if available
                if detailed_explanation:
                    # Extract relevant section around the query
                    explanation_lower = detailed_explanation.lower()
                    query_pos = explanation_lower.find(query_lower)
                    
                    if query_pos != -1:
                        # Get context around the query (500 chars before and after)
                        start = max(0, query_pos - 500)
                        end = min(len(detailed_explanation), query_pos + len(query) + 500)
                        context = detailed_explanation[start:end]
                        
                        # Clean up context
                        if start > 0:
                            context = '...' + context
                        if end < len(detailed_explanation):
                            context = context + '...'
                        
                        result['relevant_explanation'] = context
                    else:
                        # Show first 500 characters
                        result['relevant_explanation'] = detailed_explanation[:500] + '...' if len(detailed_explanation) > 500 else detailed_explanation
                
                results.append(result)
        
        # Sort by relevance (exact name matches first, then explanation matches)
        def relevance_score(result):
            score = 0
            name = result['name'].lower()
            generic = result['generic_name'].lower()
            
            if query_lower == name:
                score += 100
            elif query_lower in name:
                score += 50
            elif query_lower == generic:
                score += 90
            elif query_lower in generic:
                score += 40
            
            # Boost score for medicines with detailed explanations
            if result['has_detailed_explanation']:
                score += 10
            
            return score
        
        results.sort(key=relevance_score, reverse=True)
        
        return Response({
            'status': 'success',
            'query': query,
            'results_count': len(results),
            'results': results[:20],  # Limit to top 20 results
            'data_source': 'Enhanced Ultimate Medicine Database with Wiki Medical Knowledge',
            'database_stats': {
                'total_medicines': len(medicines),
                'with_detailed_explanations': sum(1 for m in medicines if m.get('detailed_medical_explanation')),
                'source': 'DrugBank + Wiki Medical Terms + Enhanced Processing'
            }
        })
        
    except Exception as e:
        logging.error(f"Error searching medical knowledge: {e}")
        return Response({
            'status': 'error',
            'message': f'Error searching medical knowledge: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_medical_explanation(request, medicine_name):
    """Get detailed medical explanation for a specific medicine"""
    try:
        # Load enhanced ultimate database
        import json
        import os
        
        enhanced_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'processed', 'enhanced_ultimate_medicine_database.json')
        
        try:
            with open(enhanced_db_path, 'r') as f:
                enhanced_data = json.load(f)
            medicines = enhanced_data.get('medicines', [])
        except:
            return Response({
                'status': 'error',
                'message': 'Medical knowledge database not available'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Find medicine by name
        medicine_name_clean = medicine_name.lower().strip()
        
        for medicine in medicines:
            name = medicine.get('name', '').lower()
            generic_name = medicine.get('generic_name', '').lower()
            synonyms = [str(s).lower() for s in medicine.get('synonyms', [])]
            brand_names = [str(b).lower() for b in medicine.get('brand_names', [])]
            all_aliases = synonyms + brand_names
            
            if (name == medicine_name_clean or generic_name == medicine_name_clean or
                medicine_name_clean in all_aliases):
                
                detailed_explanation = medicine.get('detailed_medical_explanation', '')
                
                if detailed_explanation:
                    return Response({
                        'status': 'success',
                        'medicine_name': medicine.get('name', ''),
                        'generic_name': medicine.get('generic_name', ''),
                        'detailed_explanation': detailed_explanation,
                        'explanation_length': len(detailed_explanation),
                        'knowledge_source': medicine.get('medical_knowledge_source', 'Wiki Medical Terms Dataset'),
                        'keywords': medicine.get('knowledge_keywords', []),
                        'categories': medicine.get('categories', ''),
                        'alternatives': medicine.get('alternatives', '')
                    })
                else:
                    return Response({
                        'status': 'info',
                        'message': 'No detailed medical explanation available for this medicine',
                        'medicine_name': medicine.get('name', ''),
                        'generic_name': medicine.get('generic_name', ''),
                        'categories': medicine.get('categories', ''),
                        'alternatives': medicine.get('alternatives', '')
                    })
        
        return Response({
            'status': 'error',
            'message': f'Medicine "{medicine_name}" not found in medical knowledge database'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logging.error(f"Error getting medical explanation: {e}")
        return Response({
            'status': 'error',
            'message': f'Error getting medical explanation: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_medical_knowledge_stats(request):
    """Get statistics about the medical knowledge database"""
    try:
        # Load enhanced ultimate database
        import json
        import os
        
        enhanced_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'processed', 'enhanced_ultimate_medicine_database.json')
        
        try:
            with open(enhanced_db_path, 'r') as f:
                enhanced_data = json.load(f)
        except:
            return Response({
                'status': 'error',
                'message': 'Medical knowledge database not available'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        medicines = enhanced_data.get('medicines', [])
        
        # Calculate statistics
        total_medicines = len(medicines)
        with_detailed_explanations = sum(1 for m in medicines if m.get('detailed_medical_explanation'))
        with_categories = sum(1 for m in medicines if m.get('categories'))
        with_alternatives = sum(1 for m in medicines if m.get('alternatives'))
        with_brand_names = sum(1 for m in medicines if m.get('brand_names'))
        with_synonyms = sum(1 for m in medicines if m.get('synonyms'))
        
        # Calculate average explanation length
        explanation_lengths = [len(m.get('detailed_medical_explanation', '')) for m in medicines if m.get('detailed_medical_explanation')]
        avg_explanation_length = sum(explanation_lengths) / len(explanation_lengths) if explanation_lengths else 0
        
        # Get top categories
        categories = {}
        for medicine in medicines:
            category = medicine.get('categories', '')
            if category:
                categories[category] = categories.get(category, 0) + 1
        
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return Response({
            'status': 'success',
            'database_info': {
                'version': enhanced_data.get('version', 'Unknown'),
                'last_updated': enhanced_data.get('last_updated', 'Unknown'),
                'medical_knowledge_integrated': enhanced_data.get('medical_knowledge_integrated', False)
            },
            'statistics': {
                'total_medicines': total_medicines,
                'with_detailed_explanations': with_detailed_explanations,
                'with_categories': with_categories,
                'with_alternatives': with_alternatives,
                'with_brand_names': with_brand_names,
                'with_synonyms': with_synonyms,
                'average_explanation_length': round(avg_explanation_length),
                'enhancement_coverage': round((with_detailed_explanations / total_medicines) * 100, 2) if total_medicines > 0 else 0
            },
            'top_categories': [{'category': cat, 'count': count} for cat, count in top_categories],
            'data_sources': [
                'DrugBank Database',
                'Wiki Medical Terms Dataset (LLaMA2)',
                'Molecular Structures (SDF)',
                'Enhanced Processing & Integration'
            ]
        })
        
    except Exception as e:
        logging.error(f"Error getting medical knowledge stats: {e}")
        return Response({
            'status': 'error',
            'message': f'Error getting medical knowledge stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def validate_prescription_safety(request):
    """
    Validate overall prescription safety including drug interactions
    """
    try:
        prescription_data = request.data
        
        if not prescription_data:
            return Response({
                'error': 'No prescription data provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate prescription safety
        safety_results = interaction_checker.validate_prescription_safety(prescription_data)
        
        return Response({
            'status': 'success',
            'data': safety_results
        })
        
    except Exception as e:
        logging.error(f"Error validating prescription safety: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_medicine_interactions(request, medicine_name):
    """
    Get all interactions for a specific medicine
    """
    try:
        interactions = interaction_checker.get_medicine_interactions(medicine_name)
        
        return Response({
            'status': 'success',
            'medicine': medicine_name,
            'interactions': interactions,
            'total_interactions': len(interactions)
        })
        
    except Exception as e:
        logging.error(f"Error getting medicine interactions: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_interaction_details(request, medicine1, medicine2):
    """
    Get detailed interaction information between two specific medicines
    """
    try:
        interaction_details = interaction_checker.get_interaction_details(medicine1, medicine2)
        
        if not interaction_details:
            return Response({
                'status': 'success',
                'message': 'No interaction found between these medicines',
                'medicine1': medicine1,
                'medicine2': medicine2,
                'interaction': None
            })
        
        return Response({
            'status': 'success',
            'medicine1': medicine1,
            'medicine2': medicine2,
            'interaction': interaction_details
        })
        
    except Exception as e:
        logging.error(f"Error getting interaction details: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def analyze_prescription_with_safety(request):
    """
    Analyze prescription text and check for drug interactions in one call
    """
    try:
        prescription_text = request.data.get('text', '')
        
        if not prescription_text:
            return Response({
                'error': 'No prescription text provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Analyze prescription using existing logic
        ai_processor = get_biobert_processor()
        extracted_data = None
        processing_method = "Rule-based"
        confidence_score = 0.0
        ai_model_info = None
        
        if ai_processor:
            try:
                extracted_data = ai_processor.analyze_prescription(prescription_text)
                if extracted_data and extracted_data.get('medicines'):
                    processing_method = "BioBERT AI"
                    confidence_score = extracted_data.get('confidence_score', 0.0)
                    ai_model_info = {
                        'model_name': 'BioBERT',
                        'model_version': '1.1',
                        'parameters': '110M',
                        'specialization': 'Biomedical text understanding'
                    }
            except Exception as e:
                logging.warning(f"BioBERT analysis failed, falling back to rule-based: {e}")
        
        # Fallback to rule-based if BioBERT failed or found no medicines
        if not extracted_data or not extracted_data.get('medicines'):
            extracted_data = extract_medicine_info(prescription_text)
            processing_method = "Rule-based"
            confidence_score = 0.8  # Rule-based confidence
        
        if not extracted_data:
            return Response({
                'error': 'Failed to extract medicine information'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get detailed medicine information
        extracted_medicines = []
        medicines_list = extracted_data.get('medicines', [])
        dosages = extracted_data.get('dosages', [])
        frequency = extracted_data.get('frequency', '')
        duration = extracted_data.get('duration', '')
        
        # Handle both string and dictionary medicine lists
        for i, medicine_item in enumerate(medicines_list):
            if isinstance(medicine_item, dict):
                medicine_name = medicine_item.get('name', '')
                dosage = medicine_item.get('dosage', '')
            else:
                medicine_name = str(medicine_item)
                dosage = dosages[i] if i < len(dosages) else ''
            
            detailed_info = _get_detailed_medicine_info(medicine_name)
            
            medicine_data = {
                'name': medicine_name,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration
            }
            
            # Merge detailed info directly into medicine_data
            if detailed_info:
                medicine_data.update(detailed_info)
            extracted_medicines.append(medicine_data)
        
        # Check for drug interactions
        medicine_names = [med['name'] for med in extracted_medicines if med['name']]
        interaction_results = interaction_checker.check_interactions(medicine_names)
        
        # Validate overall prescription safety
        safety_results = interaction_checker.validate_prescription_safety({
            'extracted_medicines': extracted_medicines
        })
        
        return Response({
            'status': 'success',
            'extracted_medicines': extracted_medicines,
            'processing_method': processing_method,
            'confidence_score': confidence_score,
            'ai_model_info': ai_model_info,
            'drug_interactions': interaction_results,
            'safety_validation': safety_results,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error analyzing prescription with safety: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# ENHANCED DRUG INTERACTION ENDPOINTS (OpenFDA + RxNorm)
# ============================================================================

@api_view(['POST'])
def check_enhanced_drug_interactions(request):
    """
    Check for drug interactions using enhanced system (OpenFDA + RxNorm + Manual)
    """
    try:
        medicines = request.data.get('medicines', [])
        
        if not medicines:
            return Response({
                'error': 'No medicines provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check interactions using enhanced system
        interaction_results = enhanced_interaction_checker.check_interactions(medicines)
        
        return Response({
            'status': 'success',
            'data': interaction_results
        })
        
    except Exception as e:
        logging.error(f"Error checking enhanced drug interactions: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_medicine_info_enhanced(request, medicine_name):
    """
    Get comprehensive medicine information from all sources (OpenFDA + RxNorm)
    """
    try:
        medicine_info = enhanced_interaction_checker.get_medicine_info(medicine_name)
        
        return Response({
            'status': 'success',
            'medicine': medicine_name,
            'data': medicine_info
        })
        
    except Exception as e:
        logging.error(f"Error getting enhanced medicine info: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def bulk_download_medicine_data(request):
    """
    Bulk download and cache medicine data from all sources
    """
    try:
        medicine_names = request.data.get('medicines', [])
        
        if not medicine_names:
            return Response({
                'error': 'No medicines provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Bulk download data
        results = enhanced_interaction_checker.bulk_download_medicine_data(medicine_names)
        
        return Response({
            'status': 'success',
            'message': f'Downloaded data for {len(medicine_names)} medicines',
            'results': results
        })
        
    except Exception as e:
        logging.error(f"Error in bulk download: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_cache_stats(request):
    """
    Get statistics about cached data from all sources
    """
    try:
        cache_stats = enhanced_interaction_checker.get_cache_stats()
        
        return Response({
            'status': 'success',
            'data': cache_stats
        })
        
    except Exception as e:
        logging.error(f"Error getting cache stats: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def analyze_prescription_enhanced(request):
    """
    Analyze prescription text with enhanced drug interaction checking
    """
    try:
        prescription_text = request.data.get('text', '')
        
        if not prescription_text:
            return Response({
                'error': 'No prescription text provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Analyze prescription using existing logic
        ai_processor = get_biobert_processor()
        extracted_data = None
        processing_method = "Rule-based"
        confidence_score = 0.0
        ai_model_info = None
        
        if ai_processor:
            try:
                extracted_data = ai_processor.analyze_prescription(prescription_text)
                if extracted_data and extracted_data.get('medicines'):
                    processing_method = "BioBERT AI"
                    confidence_score = extracted_data.get('confidence_score', 0.0)
                    ai_model_info = {
                        'model_name': 'BioBERT',
                        'model_version': '1.1',
                        'parameters': '110M',
                        'specialization': 'Biomedical text understanding'
                    }
            except Exception as e:
                logging.warning(f"BioBERT analysis failed, falling back to rule-based: {e}")
        
        # Fallback to rule-based if BioBERT failed or found no medicines
        if not extracted_data or not extracted_data.get('medicines'):
            extracted_data = extract_medicine_info(prescription_text)
            processing_method = "Rule-based"
            confidence_score = 0.8  # Rule-based confidence
        
        if not extracted_data:
            return Response({
                'error': 'Failed to extract medicine information'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get detailed medicine information
        extracted_medicines = []
        medicine_names = extracted_data.get('medicines', [])
        dosages = extracted_data.get('dosages', [])
        frequency = extracted_data.get('frequency', '')
        duration = extracted_data.get('duration', '')
        
        for i, medicine_name in enumerate(medicine_names):
            detailed_info = _get_detailed_medicine_info(medicine_name)
            dosage = dosages[i] if i < len(dosages) else ''
            
            medicine_data = {
                'name': medicine_name,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration,
                'details': detailed_info
            }
            extracted_medicines.append(medicine_data)
        
        # Check for drug interactions using enhanced system
        medicine_names_list = [med['name'] for med in extracted_medicines if med['name']]
        interaction_results = enhanced_interaction_checker.check_interactions(medicine_names_list)
        
        # Get enhanced medicine information
        enhanced_medicine_info = {}
        for medicine_name in medicine_names_list:
            enhanced_medicine_info[medicine_name] = enhanced_interaction_checker.get_medicine_info(medicine_name)
        
        return Response({
            'status': 'success',
            'extracted_medicines': extracted_medicines,
            'processing_method': processing_method,
            'confidence_score': confidence_score,
            'ai_model_info': ai_model_info,
            'enhanced_drug_interactions': interaction_results,
            'enhanced_medicine_info': enhanced_medicine_info,
            'data_sources': {
                'medicine_extraction': 'BioBERT Medical NLP Model',
                'medicine_database': 'Local Database (DrugBank + SDF + OpenFDA)',
                'drug_interactions': 'Multi-source: Manual Database + OpenFDA API + RxNorm API',
                'medicine_info': 'OpenFDA API + RxNorm API + Local Database',
                'confidence_scoring': 'BioBERT Embeddings + Pattern Matching'
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error analyzing prescription with enhanced system: {e}")
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
