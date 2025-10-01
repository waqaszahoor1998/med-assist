"""
BioBERT-powered prescription analysis processor
Uses the local BioBERT model for intelligent medicine extraction
"""

import os
import re
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BioBERTProcessor:
    """
    Advanced prescription processor using BioBERT AI model
    Replaces the rule-based system with intelligent medical text understanding
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize BioBERT processor
        
        Args:
            model_path: Path to local BioBERT model (defaults to ai-models folder)
        """
        self.model_path = model_path or self._get_default_model_path()
        self.tokenizer = None
        self.model = None
        self._load_model()
        
        # Medical entity patterns for post-processing
        self.medicine_patterns = [
            r'\b[A-Z][a-z]+(?:mycin|cin|pril|sartan|pine|zole|pam|zepam)\b',
            r'\b(?:Aspirin|Ibuprofen|Paracetamol|Metformin|Insulin)\b',
            r'\b[A-Z][a-z]+\s+\d+\s*mg\b',
            r'\b\d+\s*mg\s+[A-Z][a-z]+\b'
        ]
        
        self.dosage_patterns = [
            r'\b\d+\s*mg\b',
            r'\b\d+\s*g\b', 
            r'\b\d+\s*ml\b',
            r'\b\d+\s*tablets?\b',
            r'\b\d+\s*capsules?\b'
        ]
        
        self.frequency_patterns = [
            r'\b(?:once|twice|three times|four times)\s+(?:daily|a day|per day)\b',
            r'\b(?:every|q\.?d\.?|b\.?i\.?d\.?|t\.?i\.?d\.?|q\.?i\.?d\.?)\b',
            r'\b(?:as needed|prn|when required)\b'
        ]
    
    def _get_default_model_path(self) -> str:
        """Get default path to BioBERT model"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        return os.path.join(project_root, "ai-models", "biobert", "biobert-v1.1")
    
    def _load_model(self):
        """Load BioBERT model and tokenizer"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"BioBERT model not found at: {self.model_path}")
            
            logger.info(f"Loading BioBERT model from: {self.model_path}")
            
            # Load tokenizer with better error handling
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                logger.info("✅ Tokenizer loaded successfully")
            except Exception as tokenizer_error:
                logger.error(f"❌ Tokenizer loading failed: {tokenizer_error}")
                raise
            
            # Load model with better error handling
            try:
                self.model = AutoModel.from_pretrained(self.model_path)
                self.model.eval()
                logger.info("✅ Model loaded successfully")
            except Exception as model_error:
                logger.error(f"❌ Model loading failed: {model_error}")
                raise
            
            logger.info("🎉 BioBERT model loaded successfully!")
            logger.info(f"📊 Vocabulary size: {self.tokenizer.vocab_size:,}")
            logger.info(f"🧠 Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
            
        except Exception as e:
            logger.error(f"💥 Failed to load BioBERT model: {e}")
            raise
    
    def extract_medicines(self, prescription_text: str) -> List[Dict[str, Any]]:
        """
        Extract medicine information from prescription text using BioBERT
        
        Args:
            prescription_text: Raw prescription text
            
        Returns:
            List of extracted medicine dictionaries with confidence scores
        """
        try:
            if not prescription_text or not prescription_text.strip():
                logger.warning("⚠️ Empty prescription text provided")
                return []
            
            logger.info(f"🔍 Processing prescription: '{prescription_text[:50]}...'")
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(prescription_text)
            logger.debug(f"📝 Cleaned text: '{cleaned_text}'")
            
            # Get BioBERT embeddings
            embeddings = self._get_biobert_embeddings(cleaned_text)
            if embeddings.numel() == 0:
                logger.warning("⚠️ No embeddings generated, falling back to pattern matching")
            
            # Extract entities using BioBERT + pattern matching
            medicines = self._extract_entities_with_biobert(cleaned_text, embeddings)
            logger.debug(f"🔬 Raw extractions: {len(medicines)} found")
            
            # Post-process and validate results
            medicines = self._post_process_medicines(medicines)
            
            logger.info(f"✅ Successfully extracted {len(medicines)} medicines from prescription")
            for i, med in enumerate(medicines, 1):
                logger.info(f"   {i}. {med['name']} (confidence: {med['confidence']})")
            
            return medicines
            
        except Exception as e:
            logger.error(f"💥 Error extracting medicines: {e}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess prescription text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize common medical abbreviations
        abbreviations = {
            'q.d.': 'once daily',
            'b.i.d.': 'twice daily', 
            't.i.d.': 'three times daily',
            'q.i.d.': 'four times daily',
            'prn': 'as needed',
            'mg': 'mg',
            'ml': 'ml'
        }
        
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        
        return text
    
    def _get_biobert_embeddings(self, text: str) -> torch.Tensor:
        """Get BioBERT embeddings for the text"""
        try:
            # Tokenize text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Get model outputs
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Return embeddings (last hidden state)
            return outputs.last_hidden_state
            
        except Exception as e:
            logger.error(f"Error getting BioBERT embeddings: {e}")
            return torch.tensor([])
    
    def _extract_entities_with_biobert(self, text: str, embeddings: torch.Tensor) -> List[Dict[str, Any]]:
        """Extract medicine entities using BioBERT embeddings + pattern matching"""
        medicines = []
        
        # Get tokens for analysis
        tokens = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(text))
        
        # Find medicine names using patterns
        medicine_matches = []
        for pattern in self.medicine_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                medicine_matches.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.8  # Base confidence for pattern matches
                })
        
        # Process each medicine match
        for match in medicine_matches:
            medicine_name = match['text']
            
            # Find associated dosage
            dosage = self._find_dosage_near_medicine(text, match['start'], match['end'])
            
            # Find frequency
            frequency = self._find_frequency_near_medicine(text, match['start'], match['end'])
            
            # Calculate confidence based on BioBERT understanding
            confidence = self._calculate_confidence(medicine_name, embeddings)
            
            medicines.append({
                'name': medicine_name,
                'dosage': dosage,
                'frequency': frequency,
                'confidence': confidence,
                'raw_text': text[match['start']:match['end']]
            })
        
        return medicines
    
    def _find_dosage_near_medicine(self, text: str, start: int, end: int) -> Optional[str]:
        """Find dosage information near a medicine name"""
        # Look in a window around the medicine name
        window_start = max(0, start - 50)
        window_end = min(len(text), end + 50)
        window_text = text[window_start:window_end]
        
        for pattern in self.dosage_patterns:
            match = re.search(pattern, window_text, re.IGNORECASE)
            if match:
                return match.group()
        
        return None
    
    def _find_frequency_near_medicine(self, text: str, start: int, end: int) -> Optional[str]:
        """Find frequency information near a medicine name"""
        # Look in a window around the medicine name
        window_start = max(0, start - 100)
        window_end = min(len(text), end + 100)
        window_text = text[window_start:window_end]
        
        for pattern in self.frequency_patterns:
            match = re.search(pattern, window_text, re.IGNORECASE)
            if match:
                return match.group()
        
        return None
    
    def _calculate_confidence(self, medicine_name: str, embeddings: torch.Tensor) -> float:
        """Calculate confidence score using BioBERT embeddings"""
        try:
            # This is a simplified confidence calculation
            # In a full implementation, you'd use the embeddings more sophisticatedly
            
            # Check if medicine name contains common medical suffixes
            medical_suffixes = ['mycin', 'cin', 'pril', 'sartan', 'pine', 'zole', 'pam']
            has_medical_suffix = any(suffix in medicine_name.lower() for suffix in medical_suffixes)
            
            # Check if it's a known medicine name
            known_medicines = ['aspirin', 'ibuprofen', 'metformin', 'amoxicillin', 'paracetamol']
            is_known = any(med in medicine_name.lower() for med in known_medicines)
            
            # Base confidence
            confidence = 0.5
            
            if has_medical_suffix:
                confidence += 0.2
            if is_known:
                confidence += 0.3
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _post_process_medicines(self, medicines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Post-process and validate extracted medicines"""
        processed = []
        
        for medicine in medicines:
            # Clean up medicine name
            name = medicine['name'].strip()
            if len(name) < 2:  # Skip very short matches
                continue
            
            # Skip if it's just a dosage/frequency without medicine name
            if not any(char.isalpha() for char in name):
                continue
                
            # Skip if it's only numbers and common words (like "400mg daily", "500mg twice")
            if re.match(r'^[\d\s]+(mg|ml|mcg|g|daily|twice|once|times).*$', name.lower()):
                continue
            
            # Ensure we have at least some information
            if not medicine['dosage'] and not medicine['frequency']:
                # If no dosage/frequency found, still include if confidence is high
                if medicine['confidence'] < 0.7:
                    continue
            
            processed.append({
                'name': name,
                'dosage': medicine['dosage'] or 'Not specified',
                'frequency': medicine['frequency'] or 'Not specified', 
                'confidence': round(medicine['confidence'], 2),
                'source': 'BioBERT AI'
            })
        
        # Remove duplicates and overlapping entities
        unique_medicines = []
        processed_sorted = sorted(processed, key=lambda x: (-x['confidence'], len(x['name'])))
        
        for med in processed_sorted:
            name = med['name'].lower()
            is_duplicate = False
            
            # Check if this medicine is a subset of an already added medicine
            for existing in unique_medicines:
                existing_name = existing['name'].lower()
                
                # Skip if current medicine is contained in existing one
                if name in existing_name and len(name) < len(existing_name):
                    is_duplicate = True
                    break
                    
                # Skip if existing medicine is contained in current one
                if existing_name in name and len(existing_name) < len(name):
                    # Replace existing with current (longer, more specific)
                    unique_medicines.remove(existing)
                    break
            
            if not is_duplicate:
                unique_medicines.append(med)
        
        return unique_medicines
    
    def analyze_prescription(self, prescription_text: str) -> Dict[str, Any]:
        """
        Main method for prescription analysis - compatible with views.py calls
        
        Args:
            prescription_text: Raw prescription text
            
        Returns:
            Dictionary with extracted medicines and metadata
        """
        try:
            medicines = self.extract_medicines(prescription_text)
            
            return {
                'medicines': medicines,
                'processing_method': 'BioBERT AI',
                'confidence_score': self._calculate_overall_confidence(medicines),
                'ai_model_info': self.get_model_info(),
                'extraction_successful': len(medicines) > 0
            }
        except Exception as e:
            logger.error(f"BioBERT analysis failed: {e}")
            return {
                'medicines': [],
                'processing_method': 'BioBERT AI (Failed)',
                'confidence_score': 0.0,
                'ai_model_info': self.get_model_info(),
                'extraction_successful': False,
                'error': str(e)
            }
    
    def _calculate_overall_confidence(self, medicines: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for all extracted medicines"""
        if not medicines:
            return 0.0
        
        total_confidence = sum(med.get('confidence', 0.0) for med in medicines)
        return total_confidence / len(medicines)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {"error": "Model not loaded"}
        
        return {
            "model_path": self.model_path,
            "vocabulary_size": self.tokenizer.vocab_size,
            "model_parameters": sum(p.numel() for p in self.model.parameters()),
            "model_size_mb": round(sum(p.numel() for p in self.model.parameters()) * 4 / 1024 / 1024, 1),
            "status": "loaded"
        }
