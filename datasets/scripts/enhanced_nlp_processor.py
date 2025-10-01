#!/usr/bin/env python3
"""
Enhanced NLP Processor with Chemical Structure Support
Updated version that works with the integrated medicine database
"""

import re
import json
from typing import Dict, List, Any, Optional

class EnhancedNLPProcessor:
    """Enhanced NLP processor with chemical structure support"""
    
    def __init__(self, database_path: str = None):
        self.database_path = database_path or "../../datasets/processed/enhanced_medicine_database.json"
        self.medicine_database = self._load_database()
        self.medicine_names = self._extract_medicine_names()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load the enhanced medicine database"""
        try:
            with open(self.database_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Database not found at {self.database_path}")
            return {"medicines": []}
    
    def _extract_medicine_names(self) -> List[str]:
        """Extract all medicine names for pattern matching"""
        names = []
        
        for medicine in self.medicine_database.get("medicines", []):
            # Add primary name
            if medicine.get("name"):
                names.append(medicine["name"].lower())
            
            # Add generic name
            if medicine.get("generic_name"):
                names.append(medicine["generic_name"].lower())
            
            # Add brand names
            for brand in medicine.get("brand_names", []):
                names.append(brand.lower())
            
            # Add synonyms from chemical structure
            structure = medicine.get("chemical_structure", {})
            if structure:
                for synonym in structure.get("synonyms", []):
                    names.append(synonym.lower())
        
        # Remove duplicates and sort
        return sorted(list(set(names)))
    
    def extract_medicine_info(self, text: str) -> Dict[str, Any]:
        """Extract medicine information from prescription text with enhanced capabilities"""
        
        text_lower = text.lower()
        
        # Find medicines using enhanced name matching
        found_medicines = []
        for medicine_name in self.medicine_names:
            # Skip very short names that cause false positives
            if len(medicine_name) < 3:
                continue
            # Use word boundary matching for more precise detection
            if re.search(r'\b' + re.escape(medicine_name) + r'\b', text_lower):
                found_medicines.append(medicine_name.title())
        
        # Extract dosages
        dosage_pattern = r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|tablets?|capsules?|units?)'
        dosages = re.findall(dosage_pattern, text_lower)
        
        # Extract frequency
        frequency = self._extract_frequency(text_lower)
        
        # Extract duration
        duration = self._extract_duration(text_lower)
        
        # Get detailed medicine information
        detailed_medicines = self._get_detailed_medicine_info(found_medicines)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(found_medicines, dosages, frequency, duration)
        
        return {
            'medicines': found_medicines,
            'dosages': [f"{d[0]}{d[1]}" for d in dosages],
            'frequency': frequency,
            'duration': duration,
            'detailed_medicines': detailed_medicines,
            'confidence_score': confidence,
            'molecular_info': self._extract_molecular_info(detailed_medicines),
            'safety_alerts': self._generate_safety_alerts(detailed_medicines),
            'interactions': self._check_interactions(detailed_medicines)
        }
    
    def _extract_frequency(self, text: str) -> Optional[str]:
        """Extract frequency information"""
        frequency_patterns = {
            'once daily': ['once daily', 'once a day', 'qd', 'daily'],
            'twice daily': ['twice daily', 'twice a day', 'bid', '2x daily'],
            'three times daily': ['three times daily', 'thrice daily', 'tid', '3x daily'],
            'four times daily': ['four times daily', 'qid', '4x daily'],
            'every 6 hours': ['every 6 hours', 'q6h', '6 hourly'],
            'every 8 hours': ['every 8 hours', 'q8h', '8 hourly'],
            'every 12 hours': ['every 12 hours', 'q12h', '12 hourly'],
            'as needed': ['as needed', 'prn', 'when required']
        }
        
        for frequency, patterns in frequency_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return frequency
        
        return None
    
    def _extract_duration(self, text: str) -> Optional[str]:
        """Extract duration information"""
        duration_patterns = [
            r'for\s+(\d+)\s+(days?|weeks?|months?)',
            r'(\d+)\s+(days?|weeks?|months?)\s+course',
            r'continue\s+for\s+(\d+)\s+(days?|weeks?|months?)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)} {match.group(2)}"
        
        return None
    
    def _get_detailed_medicine_info(self, medicine_names: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information for found medicines"""
        detailed_info = []
        
        for medicine_name in medicine_names:
            # Find medicine in database
            for medicine in self.medicine_database.get("medicines", []):
                if (medicine.get("name", "").lower() == medicine_name.lower() or
                    medicine.get("generic_name", "").lower() == medicine_name.lower()):
                    
                    detailed_info.append({
                        "name": medicine.get("name", ""),
                        "generic_name": medicine.get("generic_name", ""),
                        "indication": medicine.get("indication", ""),
                        "dosage": medicine.get("dosage", ""),
                        "side_effects": medicine.get("side_effects", ""),
                        "drug_interactions": medicine.get("drug_interactions", ""),
                        "food_interactions": medicine.get("food_interactions", ""),
                        "has_structure": medicine.get("has_structure", False),
                        "chemical_structure": medicine.get("chemical_structure", {}),
                        "categories": medicine.get("categories", ""),
                        "groups": medicine.get("groups", [])
                    })
                    break
        
        return detailed_info
    
    def _extract_molecular_info(self, detailed_medicines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract molecular information for medicines with structures"""
        molecular_info = []
        
        for medicine in detailed_medicines:
            if medicine.get("has_structure"):
                structure = medicine.get("chemical_structure", {})
                molecular_info.append({
                    "name": medicine.get("name", ""),
                    "molecular_formula": structure.get("molecular_formula", ""),
                    "molecular_weight": structure.get("molecular_weight", 0),
                    "cas_number": structure.get("cas_number", ""),
                    "unii": structure.get("unii", ""),
                    "atom_count": structure.get("atom_count", 0),
                    "bond_count": structure.get("bond_count", 0),
                    "synonyms": structure.get("synonyms", [])
                })
        
        return molecular_info
    
    def _generate_safety_alerts(self, detailed_medicines: List[Dict[str, Any]]) -> List[str]:
        """Generate safety alerts based on medicine information"""
        alerts = []
        
        for medicine in detailed_medicines:
            # Check for high-risk categories
            categories = medicine.get("categories", "").lower()
            if any(risk in categories for risk in ["controlled", "narcotic", "addictive"]):
                alerts.append(f"⚠️ {medicine.get('name', '')} is a controlled substance")
            
            # Check for common side effects
            side_effects = medicine.get("side_effects", "").lower()
            if "severe" in side_effects or "serious" in side_effects:
                alerts.append(f"⚠️ {medicine.get('name', '')} may cause serious side effects")
            
            # Check for food interactions
            food_interactions = medicine.get("food_interactions", "").lower()
            if food_interactions and "avoid" in food_interactions:
                alerts.append(f"⚠️ {medicine.get('name', '')} has food interaction warnings")
        
        return alerts
    
    def _check_interactions(self, detailed_medicines: List[Dict[str, Any]]) -> List[str]:
        """Check for drug interactions between multiple medicines"""
        interactions = []
        
        if len(detailed_medicines) < 2:
            return interactions
        
        # Simple interaction checking (can be enhanced with more sophisticated algorithms)
        medicine_names = [med.get("name", "") for med in detailed_medicines]
        
        for i, medicine1 in enumerate(detailed_medicines):
            for medicine2 in detailed_medicines[i+1:]:
                # Check if either medicine has interaction warnings
                interactions1 = medicine1.get("drug_interactions", "").lower()
                interactions2 = medicine2.get("drug_interactions", "").lower()
                
                if interactions1 or interactions2:
                    interactions.append(
                        f"⚠️ Potential interaction between {medicine1.get('name', '')} and {medicine2.get('name', '')}"
                    )
        
        return interactions
    
    def _calculate_confidence(self, medicines: List[str], dosages: List[str], 
                            frequency: Optional[str], duration: Optional[str]) -> int:
        """Calculate confidence score for the extraction"""
        score = 0
        
        # Medicine identification (40 points)
        if medicines:
            score += 40
        
        # Dosage extraction (30 points)
        if dosages:
            score += 30
        
        # Frequency detection (20 points)
        if frequency:
            score += 20
        
        # Duration specification (10 points)
        if duration:
            score += 10
        
        return min(score, 100)
    
    def get_medicine_alternatives(self, medicine_name: str) -> List[Dict[str, Any]]:
        """Get alternative medicines based on chemical structure similarity"""
        alternatives = []
        
        # Find the target medicine
        target_medicine = None
        for medicine in self.medicine_database.get("medicines", []):
            if (medicine.get("name", "").lower() == medicine_name.lower() or
                medicine.get("generic_name", "").lower() == medicine_name.lower()):
                target_medicine = medicine
                break
        
        if not target_medicine or not target_medicine.get("has_structure"):
            return alternatives
        
        target_structure = target_medicine.get("chemical_structure", {})
        target_formula = target_structure.get("molecular_formula", "")
        
        # Find medicines with similar molecular formulas
        for medicine in self.medicine_database.get("medicines", []):
            if (medicine.get("has_structure") and 
                medicine.get("name", "").lower() != medicine_name.lower()):
                
                structure = medicine.get("chemical_structure", {})
                formula = structure.get("molecular_formula", "")
                
                # Simple similarity check (can be enhanced)
                if formula and self._calculate_formula_similarity(target_formula, formula) > 0.7:
                    alternatives.append({
                        "name": medicine.get("name", ""),
                        "generic_name": medicine.get("generic_name", ""),
                        "molecular_formula": formula,
                        "similarity_score": self._calculate_formula_similarity(target_formula, formula)
                    })
        
        # Sort by similarity score
        alternatives.sort(key=lambda x: x["similarity_score"], reverse=True)
        return alternatives[:5]  # Return top 5 alternatives
    
    def _calculate_formula_similarity(self, formula1: str, formula2: str) -> float:
        """Calculate similarity between two molecular formulas"""
        if not formula1 or not formula2:
            return 0.0
        
        # Simple character-based similarity (can be enhanced with proper chemical similarity)
        common_chars = sum(1 for c in set(formula1) if c in set(formula2))
        total_chars = len(set(formula1 + formula2))
        
        return common_chars / total_chars if total_chars > 0 else 0.0

def test_enhanced_processor():
    """Test the enhanced NLP processor"""
    print("Testing Enhanced NLP Processor")
    print("=" * 40)
    
    processor = EnhancedNLPProcessor()
    
    test_cases = [
        "Take Paracetamol 500mg twice daily for 7 days",
        "Ibuprofen 400mg every 6 hours as needed",
        "Take Amoxicillin 250mg three times daily for 10 days",
        "Metformin 500mg twice daily with meals",
        "Take one Lisinopril 10mg tablet once daily"
    ]
    
    for i, prescription in enumerate(test_cases, 1):
        print(f"\n{i}. Input: {prescription}")
        result = processor.extract_medicine_info(prescription)
        
        print(f"   → Medicines: {result['medicines']}")
        print(f"   → Dosages: {result['dosages']}")
        print(f"   → Frequency: {result['frequency']}")
        print(f"   → Duration: {result['duration']}")
        print(f"   → Confidence: {result['confidence_score']}%")
        
        if result['molecular_info']:
            print(f"   → Molecular Info: {result['molecular_info']}")
        
        if result['safety_alerts']:
            print(f"   → Safety Alerts: {result['safety_alerts']}")
        
        if result['interactions']:
            print(f"   → Interactions: {result['interactions']}")

def main():
    """Main function"""
    test_enhanced_processor()

if __name__ == "__main__":
    main()
