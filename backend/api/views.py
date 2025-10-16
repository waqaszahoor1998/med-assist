"""
============================================================================
API VIEWS - Medicine Assistant Application
============================================================================

This file contains all main API endpoint handlers (view functions).
Each function processes HTTP requests, performs business logic, and returns
JSON responses to the Flutter frontend.

Request Flow:
1. Frontend sends HTTP request (GET, POST, PUT, DELETE)
2. api/urls.py routes request to function in this file
3. Function validates JWT token (@permission_classes decorator)
4. Function processes request (calls helpers, AI, database)
5. Function returns JSON response
6. Frontend receives and displays data

Key Endpoints in this file:
- analyze_prescription() - AI-powered prescription analysis
- create_reminder() - Create medication reminders
- get_notifications() - Retrieve user notifications
- trigger_reminder_notifications() - Check and notify due reminders
- get_prescription_history() - View past analyses
- search_medicines() - Search medicine database
- search_medical_knowledge() - Search medical terms

Helper Modules Used:
- biobert_processor.py - BioBERT AI for medicine extraction
- nlp_processor.py - Rule-based fallback extraction
- drug_interactions.py - Check medicine interactions
- allergy_checker.py - Validate against user allergies
- models.py - Database operations
- openfda_client.py - OpenFDA API integration
- rxnorm_client.py - RxNorm API integration

Authentication:
- @permission_classes([IsAuthenticated]) - Requires valid JWT token
- @permission_classes([AllowAny]) - No authentication required
- JWT token passed in header: Authorization: Bearer <token>

Frontend Integration:
- All functions called from Flutter via ApiService
- Request/Response format: JSON
- Error handling: Try-catch with user-friendly messages
============================================================================
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import logging
import re

logger = logging.getLogger(__name__)
from django.utils import timezone

# Import helper modules
from .nlp_processor import extract_medicine_info, processor           # Rule-based extraction
from .biobert_processor import BioBERTProcessor                        # AI extraction
from .unified_drug_interactions import unified_interaction_checker     # Unified checking (Both systems)
from .database_views import (                                          # Database operations
    analyze_prescription_with_safety as db_analyze_prescription,
    create_medication_reminder as db_create_reminder,
    get_medication_reminders as db_get_reminders,
    get_medicine_info as db_get_medicine_info,
    search_medical_knowledge as db_search_knowledge,
    get_medical_explanation as db_get_explanation,
    get_medical_knowledge_stats as db_get_stats
)

# Import database models
from .models import Medicine, UserProfile, MedicationReminder, PrescriptionHistory, Notification

# Import allergy validation
from .allergy_checker import allergy_checker

# ============================================================================
# BIOBERT AI PROCESSOR - Singleton Pattern
# ============================================================================
# BioBERT is loaded once and reused for all requests (memory efficient)
biobert_processor = None

def get_biobert_processor():
    """
    Get or create BioBERT processor instance (singleton pattern).
    
    Called by:
    - analyze_prescription() - Main prescription analysis function
    
    Returns:
    - BioBERTProcessor instance or None if loading failed
    
    Why singleton?
    - BioBERT model is large (~400MB in memory)
    - Loading it for each request would be slow
    - One instance serves all users
    
    Error handling:
    - Returns None if BioBERT fails to load
    - Allows fallback to rule-based extraction
    """
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
@permission_classes([AllowAny])  # No authentication required for health check
def ping(request):
    """
    Health check endpoint to verify API is running.
    
    URL: GET /api/ping/
    Authentication: None required (AllowAny)
    
    Called by:
    - Flutter app on startup (connectivity check)
    - Server monitoring tools
    - Frontend error recovery
    
    Returns:
    - {message: "API is running", status: "success", version: "1.0.0"}
    
    Use cases:
    - Verify backend is accessible
    - Check API version
    - Network connectivity test
    """
    return Response({
        'message': 'API is running',
        'status': 'success',
        'version': '1.0.0'
    })


# ============================================================================
# PRESCRIPTION ANALYSIS ENDPOINT - Core AI Feature
# ============================================================================
@api_view(['POST'])
@permission_classes([AllowAny])  # Open for testing; change to [IsAuthenticated] in production
def analyze_prescription(request):
    """
    Analyze prescription text using BioBERT AI with rule-based fallback.
    Core feature of the application (Day 1-10).
    
    URL: POST /api/prescription/analyze/
    Authentication: AllowAny (should be IsAuthenticated in production)
    
    Request Body:
    {
        "text": "Take Aspirin 100mg twice daily for 7 days",
        "allergies": ["Penicillin", "Peanuts"]  (optional)
    }
    
    Response:
    {
        "medicines": [
            {
                "name": "Aspirin",
                "dosage": "100mg",
                "frequency": "twice daily",
                "duration": "7 days",
                "confidence": 0.98,
                "extraction_source": "BioBERT AI",
                "side_effects": [...],
                "interactions": [...],
                "alternatives": [...]
            }
        ],
        "interactions": [...],
        "allergies": [...],
        "processing_method": "BioBERT AI",
        "confidence_score": 0.95
    }
    
    Processing Flow:
    1. Receive prescription text from Flutter
    2. Try BioBERT AI extraction first
       - Calls: biobert_processor.extract_medicines()
       - Uses: AI models in ai-models/biobert/
    3. If BioBERT fails, use rule-based extraction
       - Calls: nlp_processor.extract_medicine_info()
       - Uses: Regex patterns
    4. For each extracted medicine:
       - Query Medicine model for detailed info
       - Get alternatives from database
    5. Check drug interactions
       - Calls: drug_interactions.check()
       - Compares medicine pairs
    6. Check allergies
       - Calls: allergy_checker.check()
       - Validates against user's allergy list
    7. Save complete analysis to PrescriptionHistory model
    8. Return comprehensive JSON response
    
    Called by:
    - Flutter PrescriptionEntryScreen.analyzePrescription()
    - ApiService.analyzePrescription()
    
    Calls:
    - get_biobert_processor() - Get AI instance
    - biobert_processor.extract_medicines() - AI extraction
    - nlp_processor.extract_medicine_info() - Fallback extraction
    - Medicine.objects.filter() - Database queries
    - drug_interactions.check() - Interaction checking
    - allergy_checker.check() - Allergy validation
    - PrescriptionHistory.objects.create() - Save to database
    
    Side Effects:
    - Creates PrescriptionHistory record (auto-save feature, Day 16)
    - Updates user's last activity timestamp
    
    Error Handling:
    - BioBERT failure → falls back to rule-based
    - Invalid input → returns 400 Bad Request
    - Server error → returns 500 with error message
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
                        
                        # Get alternatives for this medicine
                        alternatives = _get_medicine_alternatives(med.get('name', ''))
                        if alternatives:
                            medicine_data['alternatives'] = alternatives
                        
                        extracted_medicines.append(medicine_data)
                    
                    # Calculate overall confidence
                    avg_confidence = sum(med.get('confidence', 0) for med in medicines) / len(medicines) if medicines else 0
                    
                    # Check for allergies if user is authenticated or allergies provided
                    allergy_check_result = None
                    if request.user.is_authenticated:
                        allergy_check_result = allergy_checker.check_prescription_allergies(
                            extracted_medicines, user=request.user
                        )
                    elif 'allergies' in request.data:
                        user_allergies = request.data.get('allergies', [])
                        if user_allergies:
                            allergy_check_result = allergy_checker.check_prescription_allergies(
                                extracted_medicines, allergies_list=user_allergies
                            )
                    
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
                    
                    # Add allergy check results if available
                    if allergy_check_result:
                        response_data['allergy_check'] = allergy_check_result
                    
                    # Check for drug interactions using unified system
                    medicine_names = [med.get('name', '') for med in extracted_medicines if med.get('name')]
                    if medicine_names:
                        try:
                            interaction_results = unified_interaction_checker.check_interactions(medicine_names)
                            response_data['drug_interactions'] = interaction_results
                            response_data['safety_level'] = interaction_results.get('overall_risk_level', 'UNKNOWN')
                        except Exception as e:
                            logging.error(f"Drug interaction checking failed: {e}")
                            response_data['drug_interactions'] = {
                                'status': 'error',
                                'error': 'Drug interaction checking temporarily unavailable',
                                'interactions_found': 0,
                                'overall_risk_level': 'UNKNOWN'
                            }
                    
                    # Save to prescription history if user is authenticated
                    if request.user.is_authenticated:
                        try:
                            PrescriptionHistory.objects.create(
                                user=request.user,
                                prescription_text=prescription_text,
                                extracted_data={'medicines': extracted_medicines},
                                analysis_results=response_data,
                                safety_alerts=allergy_check_result.get('warnings', []) if allergy_check_result else [],
                                processing_method=processing_method,
                                confidence_score=avg_confidence
                            )
                        except Exception as save_error:
                            logging.error(f"Failed to save prescription history: {save_error}")
                    
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
            
            # Get alternatives for this medicine
            alternatives = _get_medicine_alternatives(medicine)
            if alternatives:
                medicine_data['alternatives'] = alternatives
            
            extracted_medicines.append(medicine_data)
        
        # Check for allergies if user is authenticated or allergies provided
        allergy_check_result = None
        if request.user.is_authenticated:
            allergy_check_result = allergy_checker.check_prescription_allergies(
                extracted_medicines, user=request.user
            )
        elif 'allergies' in request.data:
            user_allergies = request.data.get('allergies', [])
            if user_allergies:
                allergy_check_result = allergy_checker.check_prescription_allergies(
                    extracted_medicines, allergies_list=user_allergies
                )
        
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
        
        # Add allergy check results if available
        if allergy_check_result:
            response_data['allergy_check'] = allergy_check_result
        
        # Check for drug interactions using unified system
        medicine_names = [med.get('name', '') for med in extracted_medicines if med.get('name')]
        if medicine_names:
            try:
                interaction_results = unified_interaction_checker.check_interactions(medicine_names)
                response_data['drug_interactions'] = interaction_results
                response_data['safety_level'] = interaction_results.get('overall_risk_level', 'UNKNOWN')
            except Exception as e:
                logging.error(f"Drug interaction checking failed: {e}")
                response_data['drug_interactions'] = {
                    'status': 'error',
                    'error': 'Drug interaction checking temporarily unavailable',
                    'interactions_found': 0,
                    'overall_risk_level': 'UNKNOWN'
                }
        
        # Save to prescription history if user is authenticated (rule-based fallback)
        if request.user.is_authenticated:
            try:
                PrescriptionHistory.objects.create(
                    user=request.user,
                    prescription_text=prescription_text,
                    extracted_data={'medicines': extracted_medicines},
                    analysis_results=response_data,
                    safety_alerts=allergy_check_result.get('warnings', []) if allergy_check_result else [],
                    processing_method=processing_method,
                    confidence_score=nlp_result.get('confidence_score', 0.5)
                )
            except Exception as save_error:
                logging.error(f"Failed to save prescription history: {save_error}")
        
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
    """Database-backed medication reminder creation"""
    return db_create_reminder(request)

@api_view(['GET'])
def get_reminders(request):
    """Database-backed medication reminders retrieval"""
    return db_get_reminders(request)

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
        'data_source': 'Enhanced Ultimate Medicine Database (18,802 medicines with Wiki Knowledge)',
        'source_details': {
            'database': 'enhanced_ultimate_medicine_database.json',
            'origin': 'DrugBank + Wiki Medical Terms + Molecular Structures + Enhanced Processing',
            'last_updated': '2025-01-27',
            'reliability': 'High - Official DrugBank medical database'
        }
    }

def _get_medicine_alternatives(medicine_name):
    """Get alternative medicines for a given medicine"""
    if not medicine_name:
        return []
    
    medicines = processor.medicine_database.get('medicines', [])
    
    # Clean the medicine name - remove dosage information for better matching
    clean_name = medicine_name.lower().strip()
    clean_name_no_dosage = re.sub(r'\s*\d+\s*(mg|mcg|g|ml|mcg)\s*', ' ', clean_name).strip()
    
    # Find the medicine
    medicine = None
    for med in medicines:
        if (med.get('name', '').lower() == clean_name or
            med.get('generic_name', '').lower() == clean_name or
            med.get('name', '').lower() == clean_name_no_dosage or
            med.get('generic_name', '').lower() == clean_name_no_dosage):
            medicine = med
            break
    
    if not medicine:
        return []
    
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
                            'indication': med.get('indications', '') or med.get('indication', ''),
                            'category': med.get('category', '') or med.get('categories', ''),
                            'reason': 'Direct alternative from database'
                        })
                        break
    
    # If no alternatives found in the alternatives field, try category matching
    if not alternatives:
        medicine_category = medicine.get('category', '') or medicine.get('categories', '')
        medicine_indication = medicine.get('indications', '') or medicine.get('indication', '')
        
        for med in medicines:
            if med.get('name') != medicine.get('name'):
                # Check if same category
                if medicine_category and medicine_category.lower() in (med.get('category', '') or med.get('categories', '')).lower():
                    alternatives.append({
                        'name': med.get('name', ''),
                        'generic_name': med.get('generic_name', ''),
                        'indication': med.get('indications', '') or med.get('indication', ''),
                        'category': med.get('category', '') or med.get('categories', ''),
                        'reason': 'Same therapeutic category'
                    })
                # Check if similar indication
                elif medicine_indication and any(word in (med.get('indications', '') or med.get('indication', '')).lower() for word in medicine_indication.lower().split()):
                    alternatives.append({
                        'name': med.get('name', ''),
                        'generic_name': med.get('generic_name', ''),
                        'indication': med.get('indications', '') or med.get('indication', ''),
                        'category': med.get('category', '') or med.get('categories', ''),
                        'reason': 'Similar therapeutic indication'
                    })
    
    # Limit to 5 alternatives
    alternatives = alternatives[:5]
    
    if not alternatives:
        # Fallback: return some common alternatives based on medicine type
        medicine_name_lower = medicine.get('name', '').lower()
        
        if 'aspirin' in medicine_name_lower or 'ibuprofen' in medicine_name_lower:
            alternatives = [
                {'name': 'Paracetamol', 'generic_name': 'Acetaminophen', 'indication': 'Pain relief, fever', 'category': 'Analgesic', 'reason': 'Alternative pain reliever'},
                {'name': 'Naproxen', 'generic_name': 'Naproxen', 'indication': 'Pain relief, inflammation', 'category': 'NSAID', 'reason': 'Alternative NSAID'},
                {'name': 'Celecoxib', 'generic_name': 'Celecoxib', 'indication': 'Pain relief, arthritis', 'category': 'NSAID', 'reason': 'COX-2 selective NSAID'}
            ]
        elif 'metformin' in medicine_name_lower:
            alternatives = [
                {'name': 'Glipizide', 'generic_name': 'Glipizide', 'indication': 'Type 2 diabetes', 'category': 'Sulfonylurea', 'reason': 'Alternative diabetes medication'},
                {'name': 'Sitagliptin', 'generic_name': 'Sitagliptin', 'indication': 'Type 2 diabetes', 'category': 'DPP-4 inhibitor', 'reason': 'Alternative diabetes medication'}
            ]
        elif 'penicillin' in medicine_name_lower or 'amoxicillin' in medicine_name_lower:
            alternatives = [
                {'name': 'Azithromycin', 'generic_name': 'Azithromycin', 'indication': 'Bacterial infections', 'category': 'Macrolide antibiotic', 'reason': 'Alternative antibiotic (non-penicillin)'},
                {'name': 'Ciprofloxacin', 'generic_name': 'Ciprofloxacin', 'indication': 'Bacterial infections', 'category': 'Fluoroquinolone antibiotic', 'reason': 'Alternative antibiotic (non-penicillin)'},
                {'name': 'Clindamycin', 'generic_name': 'Clindamycin', 'indication': 'Bacterial infections', 'category': 'Lincosamide antibiotic', 'reason': 'Alternative antibiotic (non-penicillin)'}
            ]
    
    return alternatives

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
@permission_classes([AllowAny])
def search_medical_knowledge(request):
    """Database-backed medical knowledge search"""
    try:
        query = request.GET.get('query', '')
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return Response({
                'error': 'Query parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in medical knowledge database
        from .models import MedicalKnowledge
        from django.db.models import Q
        
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
@permission_classes([AllowAny])
def get_medical_explanation(request, medicine_name):
    """Database-backed medical explanation"""
    try:
        # Try to find medicine in database
        from .models import Medicine
        from django.db.models import Q
        
        medicine = Medicine.objects.filter(
            Q(name__iexact=medicine_name) |
            Q(generic_name__iexact=medicine_name) |
            Q(brand_names__icontains=medicine_name)
        ).first()
        
        if medicine and medicine.medical_explanation:
            return Response({
                'status': 'success',
                'medicine_name': medicine_name,
                'explanation': medicine.medical_explanation,
                'source': 'Database'
            })
        else:
            return Response({
                'status': 'not_found',
                'medicine_name': medicine_name,
                'explanation': 'No detailed medical explanation available for this medicine.',
                'source': 'Database'
            })
            
    except Exception as e:
        logger.error(f"Error getting medical explanation: {e}")
        return Response({
            'error': f'Failed to get explanation: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_medical_knowledge_stats(request):
    """Database-backed medical knowledge stats"""
    try:
        from .models import Medicine, MedicalKnowledge, MedicationReminder, PrescriptionHistory
        from django.utils import timezone
        
        # Get statistics
        total_medicines = Medicine.objects.count()
        total_medical_knowledge = MedicalKnowledge.objects.count()
        total_reminders = MedicationReminder.objects.count()
        total_prescriptions = PrescriptionHistory.objects.count()
        
        # Get medicines with detailed explanations
        medicines_with_explanations = Medicine.objects.filter(
            medical_explanation__isnull=False
        ).exclude(medical_explanation='').count()
        
        # Calculate enhancement coverage
        enhancement_coverage = 0
        if total_medicines > 0:
            enhancement_coverage = round((medicines_with_explanations / total_medicines) * 100, 1)
        
        return Response({
            'status': 'success',
            'database_statistics': {
                'total_medicines': total_medicines,
                'total_medical_knowledge_entries': total_medical_knowledge,
                'total_medication_reminders': total_reminders,
                'total_prescription_analyses': total_prescriptions,
                'database_last_updated': timezone.now().isoformat()
            },
            'statistics': {
                'total_medicines': total_medicines,
                'with_detailed_explanations': medicines_with_explanations,
                'enhancement_coverage': enhancement_coverage
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting medical knowledge stats: {e}")
        return Response({
            'error': f'Failed to get stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_medicines(request):
    """Search medicines in the database"""
    try:
        query = request.GET.get('query', '')
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return Response({
                'error': 'Query parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in medicines database
        from .models import Medicine
        from django.db.models import Q
        
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) |
            Q(generic_name__icontains=query) |
            Q(brand_names__icontains=query)
        ).order_by('name')[:limit]
        
        results = []
        for medicine in medicines:
            results.append({
                'id': medicine.id,
                'name': medicine.name,
                'generic_name': medicine.generic_name,
                'brand_names': medicine.brand_names,
                'category': medicine.category,
                'description': medicine.description,
                'common_doses': medicine.common_doses,
                'side_effects': medicine.side_effects,
                'interactions': medicine.interactions,
                'alternatives': medicine.alternatives,
                'medical_explanation': medicine.medical_explanation,
                'data_sources': medicine.data_sources,
            })
        
        return Response({
            'status': 'success',
            'query': query,
            'medicines': results,
            'total_found': len(results),
            'database_size': Medicine.objects.count()
        })
        
    except Exception as e:
        logger.error(f"Error searching medicines: {e}")
        return Response({
            'error': f'Search failed: {str(e)}'
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
    """Database-backed prescription analysis with safety checks"""
    return db_analyze_prescription(request)

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


# ============================================================================
# NOTIFICATION SYSTEM API ENDPOINTS
# ============================================================================
# These endpoints manage user notifications including medicine reminders,
# allergy alerts, drug interactions, and system messages.
#
# All endpoints require JWT authentication via Authorization header.
# Returns JSON responses with status and data fields.
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """
    Get all notifications for authenticated user with optional filtering
    
    Query Parameters:
    - read: 'true' for read only, 'false' for unread only, omit for all
    - type: Filter by notification type (reminder, warning, etc.)
    - limit: Maximum number of results (default: 50)
    
    Returns:
    - status: 'success'
    - notifications: List of notification objects
    - total: Total count of notifications returned
    
    Each notification includes:
    - id, type, title, message, priority
    - related_medicine, related_reminder_id
    - is_read, read_at, created_at
    - metadata for additional context
    """
    try:
        # Get all notifications for the current user
        notifications = Notification.objects.filter(user=request.user)
        
        # Optional filter by read status
        read_filter = request.GET.get('read')
        if read_filter == 'false':
            notifications = notifications.filter(is_read=False)
        elif read_filter == 'true':
            notifications = notifications.filter(is_read=True)
        
        # Optional filter by type
        notification_type = request.GET.get('type')
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        
        # Limit results
        limit = int(request.GET.get('limit', 50))
        notifications = notifications[:limit]
        
        data = []
        for notification in notifications:
            data.append({
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority,
                'related_medicine': notification.related_medicine,
                'related_reminder_id': notification.related_reminder_id,
                'action_url': notification.action_url,
                'metadata': notification.metadata,
                'is_read': notification.is_read,
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
                'created_at': notification.created_at.isoformat()
            })
        
        return Response({
            'status': 'success',
            'notifications': data,
            'total': len(data)
        })
        
    except Exception as e:
        logging.error(f"Error getting notifications: {e}")
        return Response({
            'error': f'Error getting notifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """Get count of unread notifications for authenticated user"""
    try:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({
            'status': 'success',
            'unread_count': unread_count
        })
        
    except Exception as e:
        logging.error(f"Error getting unread count: {e}")
        return Response({
            'error': f'Error getting unread count: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        
        return Response({
            'status': 'success',
            'message': 'Notification marked as read'
        })
        
    except Notification.DoesNotExist:
        return Response({
            'error': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"Error marking notification as read: {e}")
        return Response({
            'error': f'Error marking notification as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read for authenticated user"""
    try:
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'status': 'success',
            'message': f'{updated_count} notifications marked as read'
        })
        
    except Exception as e:
        logging.error(f"Error marking all notifications as read: {e}")
        return Response({
            'error': f'Error marking all notifications as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Delete a notification"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.delete()
        
        return Response({
            'status': 'success',
            'message': 'Notification deleted'
        })
        
    except Notification.DoesNotExist:
        return Response({
            'error': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"Error deleting notification: {e}")
        return Response({
            'error': f'Error deleting notification: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notification(request):
    """Create a new notification for the authenticated user"""
    try:
        data = request.data
        
        notification = Notification.objects.create(
            user=request.user,
            notification_type=data.get('type', 'info'),
            title=data.get('title', ''),
            message=data.get('message', ''),
            priority=data.get('priority', 'medium'),
            related_medicine=data.get('related_medicine'),
            related_reminder_id=data.get('related_reminder_id'),
            action_url=data.get('action_url'),
            metadata=data.get('metadata', {})
        )
        
        return Response({
            'status': 'success',
            'notification': {
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority,
                'created_at': notification.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logging.error(f"Error creating notification: {e}")
        return Response({
            'error': f'Error creating notification: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# REMINDER SYSTEM API ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reminders(request):
    """Get all medicine reminders for authenticated user"""
    try:
        reminders = MedicationReminder.objects.filter(user=request.user)
        
        # Optional filter by active status
        active_filter = request.GET.get('active')
        if active_filter == 'true':
            reminders = reminders.filter(active=True)
        elif active_filter == 'false':
            reminders = reminders.filter(active=False)
        
        data = []
        for reminder in reminders:
            data.append({
                'id': reminder.id,
                'medicine_name': reminder.medicine_name,
                'dosage': reminder.dosage,
                'frequency': reminder.frequency,
                'start_date': reminder.start_date.isoformat(),
                'end_date': reminder.end_date.isoformat() if reminder.end_date else None,
                'reminder_times': reminder.reminder_times,
                'notes': reminder.notes,
                'active': reminder.active,
                'last_notified_at': reminder.last_notified_at.isoformat() if reminder.last_notified_at else None,
                'total_notifications_sent': reminder.total_notifications_sent,
                'next_reminder': reminder.get_next_reminder_time().strftime('%H:%M') if reminder.get_next_reminder_time() else None,
                'created_at': reminder.created_at.isoformat()
            })
        
        return Response({
            'status': 'success',
            'reminders': data,
            'total': len(data)
        })
        
    except Exception as e:
        logging.error(f"Error getting reminders: {e}")
        return Response({
            'error': f'Error getting reminders: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reminder(request):
    """
    Create a new medicine reminder for the authenticated user
    
    Request Body:
    - medicine_name: Name of the medicine (required)
    - dosage: Dosage amount (e.g., "400mg") (required)
    - frequency: How often (daily, twice_daily, etc.) (default: 'daily')
    - start_date: When to start reminders (default: now)
    - end_date: When to stop reminders (optional)
    - reminder_times: List of times (e.g., ["09:00", "14:00", "21:00"]) (default: [])
    - notes: Additional notes (optional)
    - active: Whether reminder is active (default: True)
    
    Automatically creates a confirmation notification when reminder is set.
    
    Returns:
    - status: 'success'
    - reminder: Created reminder object with id, medicine_name, etc.
    """
    try:
        data = request.data
        
        # Create the medication reminder in database
        reminder = MedicationReminder.objects.create(
            user=request.user,
            medicine_name=data.get('medicine_name'),
            dosage=data.get('dosage'),
            frequency=data.get('frequency', 'daily'),
            start_date=data.get('start_date', timezone.now()),
            end_date=data.get('end_date'),
            reminder_times=data.get('reminder_times', []),
            notes=data.get('notes', ''),
            active=data.get('active', True)
        )
        
        # Create a confirmation notification to let user know reminder is set
        # This provides immediate feedback and confirms the reminder schedule
        Notification.objects.create(
            user=request.user,
            notification_type='reminder',
            title=f'Reminder Set: {reminder.medicine_name}',
            message=f'You will be reminded to take {reminder.medicine_name} {reminder.dosage} at {", ".join(reminder.reminder_times)}',
            priority='medium',
            related_medicine=reminder.medicine_name,
            related_reminder_id=reminder.id
        )
        
        return Response({
            'status': 'success',
            'reminder': {
                'id': reminder.id,
                'medicine_name': reminder.medicine_name,
                'dosage': reminder.dosage,
                'frequency': reminder.frequency,
                'reminder_times': reminder.reminder_times,
                'created_at': reminder.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logging.error(f"Error creating reminder: {e}")
        return Response({
            'error': f'Error creating reminder: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_reminder(request, reminder_id):
    """Update an existing reminder"""
    try:
        reminder = MedicationReminder.objects.get(
            id=reminder_id,
            user=request.user
        )
        
        data = request.data
        reminder.medicine_name = data.get('medicine_name', reminder.medicine_name)
        reminder.dosage = data.get('dosage', reminder.dosage)
        reminder.frequency = data.get('frequency', reminder.frequency)
        reminder.reminder_times = data.get('reminder_times', reminder.reminder_times)
        reminder.notes = data.get('notes', reminder.notes)
        reminder.active = data.get('active', reminder.active)
        
        if 'end_date' in data:
            reminder.end_date = data['end_date']
        
        reminder.save()
        
        return Response({
            'status': 'success',
            'message': 'Reminder updated successfully'
        })
        
    except MedicationReminder.DoesNotExist:
        return Response({
            'error': 'Reminder not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"Error updating reminder: {e}")
        return Response({
            'error': f'Error updating reminder: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_reminder(request, reminder_id):
    """Delete a reminder"""
    try:
        reminder = MedicationReminder.objects.get(
            id=reminder_id,
            user=request.user
        )
        reminder.delete()
        
        return Response({
            'status': 'success',
            'message': 'Reminder deleted'
        })
        
    except MedicationReminder.DoesNotExist:
        return Response({
            'error': 'Reminder not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"Error deleting reminder: {e}")
        return Response({
            'error': f'Error deleting reminder: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# PRESCRIPTION HISTORY ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prescription_history(request):
    """
    Get user's prescription analysis history
    
    Returns a list of all past prescription analyses for the authenticated user.
    Includes extracted medicines, safety alerts, and analysis metadata.
    
    Query Parameters:
    - limit: Maximum number of records to return (default: 20)
    - offset: Number of records to skip for pagination (default: 0)
    
    Returns:
    - List of prescription history records ordered by most recent first
    """
    try:
        # Get query parameters for pagination
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # Get user's prescription history
        history = PrescriptionHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[offset:offset+limit]
        
        # Format response
        history_list = []
        for record in history:
            extracted_data = record.extracted_data or {}
            medicines = extracted_data.get('medicines', [])
            
            history_list.append({
                'id': record.id,
                'prescription_text': record.prescription_text,
                'medicine_count': len(medicines),
                'medicines': [med.get('name', 'Unknown') for med in medicines if isinstance(med, dict)],
                'processing_method': record.processing_method,
                'confidence_score': record.confidence_score,
                'has_safety_alerts': len(record.safety_alerts) > 0 if record.safety_alerts else False,
                'alert_count': len(record.safety_alerts) if record.safety_alerts else 0,
                'analyzed_at': record.created_at.isoformat(),
            })
        
        # Get total count for pagination
        total_count = PrescriptionHistory.objects.filter(user=request.user).count()
        
        return Response({
            'status': 'success',
            'history': history_list,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logging.error(f"Error fetching prescription history: {e}")
        return Response({
            'error': f'Error fetching prescription history: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prescription_detail(request, history_id):
    """
    Get detailed information about a specific prescription analysis
    
    Returns complete analysis results including:
    - Full prescription text
    - All extracted medicines with details
    - Drug interactions found
    - Allergy warnings
    - Alternative medicine suggestions
    - AI confidence scores
    
    Parameters:
    - history_id: ID of the prescription history record
    
    Returns:
    - Complete prescription analysis data
    """
    try:
        # Get prescription history record
        record = PrescriptionHistory.objects.get(
            id=history_id,
            user=request.user
        )
        
        # Return complete analysis results
        return Response({
            'status': 'success',
            'id': record.id,
            'prescription_text': record.prescription_text,
            'extracted_data': record.extracted_data,
            'analysis_results': record.analysis_results,
            'safety_alerts': record.safety_alerts,
            'processing_method': record.processing_method,
            'confidence_score': record.confidence_score,
            'analyzed_at': record.created_at.isoformat()
        })
        
    except PrescriptionHistory.DoesNotExist:
        return Response({
            'error': 'Prescription history not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"Error fetching prescription detail: {e}")
        return Response({
            'error': f'Error fetching prescription detail: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_reminder_notifications(request):
    """
    Manually trigger reminder notification checks for the authenticated user
    
    This endpoint checks all active reminders for the user and creates
    notifications for any reminders that are due. It uses the same logic
    as the scheduled management command but can be called on-demand.
    
    This is useful for:
    - Testing the notification system
    - Manual notification triggers
    - On-demand reminder checks when app opens
    
    Returns:
    - notifications_created: Number of new notifications created
    - reminders_checked: Number of active reminders checked
    - notifications: List of newly created notifications
    """
    from datetime import datetime, timedelta
    
    try:
        now = timezone.now()
        current_time = now.time()
        current_date = now.date()
        
        # Get all active reminders for this user
        reminders = MedicationReminder.objects.filter(
            user=request.user,
            active=True
        )
        
        notifications_created = []
        reminders_deactivated = []
        
        for reminder in reminders:
            # Check if reminder has ended
            if reminder.end_date and now > reminder.end_date:
                reminder.active = False
                reminder.save()
                reminders_deactivated.append({
                    'id': reminder.id,
                    'medicine_name': reminder.medicine_name,
                    'reason': 'Expired'
                })
                continue
            
            # Check if it's time to send notification
            should_notify = False
            
            # If we've already notified in the last hour, skip
            if reminder.last_notified_at:
                time_since_last = now - reminder.last_notified_at
                if time_since_last < timedelta(hours=1):
                    continue
            
            # Check each reminder time
            for time_str in reminder.reminder_times:
                hour, minute = map(int, time_str.split(':'))
                reminder_time = datetime.strptime(time_str, '%H:%M').time()
                
                # Check if we're within the notification window (15 minutes before to 15 minutes after)
                reminder_datetime = datetime.combine(current_date, reminder_time)
                now_datetime = datetime.combine(current_date, current_time)
                
                time_diff = (now_datetime - reminder_datetime).total_seconds() / 60  # in minutes
                
                # If within ±15 minutes of reminder time, send notification
                if -15 <= time_diff <= 15:
                    should_notify = True
                    break
            
            if should_notify:
                # Determine priority based on frequency
                priority = 'medium'
                if reminder.frequency in ['daily', 'twice_daily', 'three_times_daily', 'four_times_daily']:
                    priority = 'high'
                elif reminder.frequency == 'as_needed':
                    priority = 'low'
                
                # Create notification message
                title = f"Time to take {reminder.medicine_name}"
                
                message_parts = [
                    f"It's time to take your medication: {reminder.medicine_name}",
                    f"Dosage: {reminder.dosage}",
                ]
                
                if reminder.notes:
                    message_parts.append(f"Note: {reminder.notes}")
                
                message = "\n".join(message_parts)
                
                # Create the notification
                notification = Notification.objects.create(
                    user=request.user,
                    notification_type='reminder',
                    title=title,
                    message=message,
                    priority=priority,
                    related_medicine=reminder.medicine_name,
                    related_reminder_id=reminder.id,
                    metadata={
                        'dosage': reminder.dosage,
                        'frequency': reminder.frequency,
                        'reminder_time': now.strftime('%H:%M'),
                        'auto_generated': True,
                        'triggered_via': 'api'
                    }
                )
                
                # Update reminder tracking
                reminder.last_notified_at = now
                reminder.total_notifications_sent += 1
                reminder.save()
                
                notifications_created.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'priority': notification.priority,
                    'created_at': notification.created_at.isoformat()
                })
        
        return Response({
            'status': 'success',
            'notifications_created': len(notifications_created),
            'reminders_checked': reminders.count(),
            'reminders_deactivated': len(reminders_deactivated),
            'notifications': notifications_created,
            'deactivated_reminders': reminders_deactivated
        })
        
    except Exception as e:
        logging.error(f"Error triggering reminder notifications: {e}")
        return Response({
            'error': f'Error triggering reminder notifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reminder_stats(request):
    """
    Get statistics about user's medication reminders
    
    Returns:
    - total_reminders: Total number of reminders
    - active_reminders: Number of active reminders
    - total_notifications_sent: Total notifications sent across all reminders
    - next_reminder: Information about the next scheduled reminder
    - reminders_by_frequency: Count of reminders by frequency type
    """
    try:
        reminders = MedicationReminder.objects.filter(user=request.user)
        active_reminders = reminders.filter(active=True)
        
        # Calculate total notifications sent
        total_notifications = sum(r.total_notifications_sent for r in reminders)
        
        # Find next reminder
        from datetime import datetime, time as dt_time
        now = timezone.now()
        next_reminder_info = None
        
        for reminder in active_reminders:
            if reminder.reminder_times:
                current_time = now.time()
                times = []
                
                for time_str in reminder.reminder_times:
                    hour, minute = map(int, time_str.split(':'))
                    times.append((dt_time(hour, minute), time_str))
                
                times.sort()
                
                for reminder_time, time_str in times:
                    if current_time < reminder_time:
                        next_reminder_info = {
                            'medicine_name': reminder.medicine_name,
                            'dosage': reminder.dosage,
                            'time': time_str,
                            'today': True
                        }
                        break
                
                if next_reminder_info:
                    break
        
        # If no reminder found for today, get first reminder of tomorrow
        if not next_reminder_info and active_reminders.exists():
            first_reminder = active_reminders.first()
            if first_reminder.reminder_times:
                times = sorted(first_reminder.reminder_times)
                next_reminder_info = {
                    'medicine_name': first_reminder.medicine_name,
                    'dosage': first_reminder.dosage,
                    'time': times[0],
                    'today': False
                }
        
        # Count by frequency
        frequency_counts = {}
        for freq_choice in MedicationReminder.FREQUENCY_CHOICES:
            freq_key = freq_choice[0]
            count = reminders.filter(frequency=freq_key).count()
            if count > 0:
                frequency_counts[freq_choice[1]] = count
        
        return Response({
            'status': 'success',
            'total_reminders': reminders.count(),
            'active_reminders': active_reminders.count(),
            'inactive_reminders': reminders.filter(active=False).count(),
            'total_notifications_sent': total_notifications,
            'next_reminder': next_reminder_info,
            'reminders_by_frequency': frequency_counts
        })
        
    except Exception as e:
        logging.error(f"Error fetching reminder stats: {e}")
        return Response({
            'error': f'Error fetching reminder stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
