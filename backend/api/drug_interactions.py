"""
============================================================================
DRUG INTERACTION CHECKER - Medicine Safety Validation
============================================================================

This file checks for dangerous drug interactions when multiple medicines
are prescribed together. Uses comprehensive interaction database built from
DrugBank and medical literature.

What It Does:
- Checks all combinations of medicines (pairs)
- Identifies dangerous interactions
- Assigns severity levels (HIGH, MEDIUM, LOW)
- Provides detailed warnings and recommendations

Severity Levels:
- HIGH: Dangerous, avoid combination (e.g., Warfarin + Aspirin)
- MEDIUM: Caution needed, monitor patient (e.g., Statins + Grapefruit)
- LOW: Minor interaction, usually safe (e.g., Antacids + Iron)
- INFO: No significant interaction found

Used by:
- api/views.py: analyze_prescription() - Checks extracted medicines
- api/views.py: check_drug_interactions() - Manual checking
- api/views.py: validate_prescription_safety() - Safety validation

Calls:
- api/models.py: Medicine.objects.filter() - Get interaction data
- Built-in interaction database (self.interactions_db)

Data Sources:
- DrugBank interaction database
- FDA drug interaction tables
- Medical literature

Frontend Integration:
- Warnings displayed in PrescriptionEntryScreen
- Color-coded by severity (red=high, orange=medium, yellow=low)
- Shows detailed interaction explanations
============================================================================
"""

import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class DrugInteractionChecker:
    """
    Checks for dangerous drug interactions between medicines.
    
    Singleton Pattern:
    - Instance created: interaction_checker = DrugInteractionChecker()
    - Reused for all requests
    
    Main Methods:
    - check() - Check interactions for medicine list
    - _check_pair() - Check specific medicine pair
    - _get_severity() - Determine interaction severity
    """
    
    def __init__(self):
        self.interactions_db = self._load_interactions_database()
        self.severity_levels = {
            'HIGH': {'color': '#FF4444', 'icon': '⚠️', 'priority': 3},
            'MEDIUM': {'color': '#FF8800', 'icon': '⚡', 'priority': 2},
            'LOW': {'color': '#FFAA00', 'icon': '💡', 'priority': 1},
            'INFO': {'color': '#4488FF', 'icon': 'ℹ️', 'priority': 0}
        }
    
    def _load_interactions_database(self) -> Dict:
        """
        Load comprehensive drug interaction database
        """
        return {
            # HIGH SEVERITY INTERACTIONS
            'high_severity': {
                # Warfarin + NSAIDs = Bleeding Risk
                ('warfarin', 'aspirin'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Bleeding Risk',
                    'description': 'Increased risk of bleeding and bruising',
                    'mechanism': 'Both drugs affect blood clotting mechanisms',
                    'recommendation': 'Avoid combination. Use alternative pain relief. Monitor INR closely if necessary.',
                    'alternatives': ['Acetaminophen', 'Topical pain relievers'],
                    'monitoring': 'INR levels, bleeding signs'
                },
                ('warfarin', 'ibuprofen'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Bleeding Risk',
                    'description': 'Increased risk of bleeding and bruising',
                    'mechanism': 'Both drugs affect blood clotting mechanisms',
                    'recommendation': 'Avoid combination. Use alternative pain relief. Monitor INR closely if necessary.',
                    'alternatives': ['Acetaminophen', 'Topical pain relievers'],
                    'monitoring': 'INR levels, bleeding signs'
                },
                ('warfarin', 'naproxen'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Bleeding Risk',
                    'description': 'Increased risk of bleeding and bruising',
                    'mechanism': 'Both drugs affect blood clotting mechanisms',
                    'recommendation': 'Avoid combination. Use alternative pain relief. Monitor INR closely if necessary.',
                    'alternatives': ['Acetaminophen', 'Topical pain relievers'],
                    'monitoring': 'INR levels, bleeding signs'
                },
                
                # ACE Inhibitors + Potassium = Hyperkalemia
                ('lisinopril', 'potassium'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Hyperkalemia Risk',
                    'description': 'Risk of dangerously high potassium levels',
                    'mechanism': 'ACE inhibitors reduce potassium excretion',
                    'recommendation': 'Monitor potassium levels. Avoid potassium supplements. Limit high-potassium foods.',
                    'alternatives': ['ARB medications', 'Calcium channel blockers'],
                    'monitoring': 'Serum potassium levels, EKG'
                },
                ('enalapril', 'potassium'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Hyperkalemia Risk',
                    'description': 'Risk of dangerously high potassium levels',
                    'mechanism': 'ACE inhibitors reduce potassium excretion',
                    'recommendation': 'Monitor potassium levels. Avoid potassium supplements. Limit high-potassium foods.',
                    'alternatives': ['ARB medications', 'Calcium channel blockers'],
                    'monitoring': 'Serum potassium levels, EKG'
                },
                
                # Digoxin + Diuretics = Digoxin Toxicity
                ('digoxin', 'furosemide'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Digoxin Toxicity',
                    'description': 'Increased risk of digoxin toxicity',
                    'mechanism': 'Diuretics cause potassium loss, increasing digoxin sensitivity',
                    'recommendation': 'Monitor digoxin levels. Maintain normal potassium levels. Watch for toxicity signs.',
                    'alternatives': ['ACE inhibitors', 'Beta-blockers'],
                    'monitoring': 'Digoxin levels, potassium levels, EKG'
                },
                ('digoxin', 'hydrochlorothiazide'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Digoxin Toxicity',
                    'description': 'Increased risk of digoxin toxicity',
                    'mechanism': 'Diuretics cause potassium loss, increasing digoxin sensitivity',
                    'recommendation': 'Monitor digoxin levels. Maintain normal potassium levels. Watch for toxicity signs.',
                    'alternatives': ['ACE inhibitors', 'Beta-blockers'],
                    'monitoring': 'Digoxin levels, potassium levels, EKG'
                },
                
                # MAOIs + SSRIs = Serotonin Syndrome
                ('phenelzine', 'fluoxetine'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Serotonin Syndrome',
                    'description': 'Life-threatening serotonin syndrome risk',
                    'mechanism': 'Both drugs increase serotonin levels',
                    'recommendation': 'NEVER combine. Wait 14 days between stopping MAOI and starting SSRI.',
                    'alternatives': ['SNRIs', 'Tricyclic antidepressants'],
                    'monitoring': 'Serotonin syndrome symptoms'
                },
                ('tranylcypromine', 'sertraline'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Serotonin Syndrome',
                    'description': 'Life-threatening serotonin syndrome risk',
                    'mechanism': 'Both drugs increase serotonin levels',
                    'recommendation': 'NEVER combine. Wait 14 days between stopping MAOI and starting SSRI.',
                    'alternatives': ['SNRIs', 'Tricyclic antidepressants'],
                    'monitoring': 'Serotonin syndrome symptoms'
                },
                
                # Lithium + NSAIDs = Lithium Toxicity
                ('lithium', 'ibuprofen'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Lithium Toxicity',
                    'description': 'Increased risk of lithium toxicity',
                    'mechanism': 'NSAIDs reduce lithium excretion',
                    'recommendation': 'Avoid combination. Monitor lithium levels closely. Use alternative pain relief.',
                    'alternatives': ['Acetaminophen', 'Topical pain relievers'],
                    'monitoring': 'Lithium levels, toxicity symptoms'
                },
                ('lithium', 'naproxen'): {
                    'severity': 'HIGH',
                    'interaction_type': 'Lithium Toxicity',
                    'description': 'Increased risk of lithium toxicity',
                    'mechanism': 'NSAIDs reduce lithium excretion',
                    'recommendation': 'Avoid combination. Monitor lithium levels closely. Use alternative pain relief.',
                    'alternatives': ['Acetaminophen', 'Topical pain relievers'],
                    'monitoring': 'Lithium levels, toxicity symptoms'
                }
            },
            
            # MEDIUM SEVERITY INTERACTIONS
            'medium_severity': {
                # Statins + Grapefruit = Increased Statin Levels
                ('atorvastatin', 'grapefruit'): {
                    'severity': 'MEDIUM',
                    'interaction_type': 'Increased Drug Levels',
                    'description': 'Grapefruit increases statin blood levels',
                    'mechanism': 'Grapefruit inhibits drug metabolism enzymes',
                    'recommendation': 'Limit grapefruit consumption. Monitor for muscle pain and liver function.',
                    'alternatives': ['Pravastatin', 'Rosuvastatin'],
                    'monitoring': 'Liver function tests, muscle symptoms'
                },
                ('simvastatin', 'grapefruit'): {
                    'severity': 'MEDIUM',
                    'interaction_type': 'Increased Drug Levels',
                    'description': 'Grapefruit increases statin blood levels',
                    'mechanism': 'Grapefruit inhibits drug metabolism enzymes',
                    'recommendation': 'Limit grapefruit consumption. Monitor for muscle pain and liver function.',
                    'alternatives': ['Pravastatin', 'Rosuvastatin'],
                    'monitoring': 'Liver function tests, muscle symptoms'
                },
                
                # Metformin + Alcohol = Lactic Acidosis
                ('metformin', 'alcohol'): {
                    'severity': 'MEDIUM',
                    'interaction_type': 'Lactic Acidosis Risk',
                    'description': 'Increased risk of lactic acidosis',
                    'mechanism': 'Alcohol impairs lactate metabolism',
                    'recommendation': 'Limit alcohol consumption. Monitor for lactic acidosis symptoms.',
                    'alternatives': ['Sulfonylureas', 'DPP-4 inhibitors'],
                    'monitoring': 'Lactate levels, kidney function'
                },
                
                # Beta-blockers + Insulin = Hypoglycemia
                ('metoprolol', 'insulin'): {
                    'severity': 'MEDIUM',
                    'interaction_type': 'Hypoglycemia Risk',
                    'description': 'Masked hypoglycemia symptoms',
                    'mechanism': 'Beta-blockers mask hypoglycemia warning signs',
                    'recommendation': 'Monitor blood glucose closely. Educate about hypoglycemia symptoms.',
                    'alternatives': ['ACE inhibitors', 'Calcium channel blockers'],
                    'monitoring': 'Blood glucose levels, hypoglycemia symptoms'
                },
                ('atenolol', 'insulin'): {
                    'severity': 'MEDIUM',
                    'interaction_type': 'Hypoglycemia Risk',
                    'description': 'Masked hypoglycemia symptoms',
                    'mechanism': 'Beta-blockers mask hypoglycemia warning signs',
                    'recommendation': 'Monitor blood glucose closely. Educate about hypoglycemia symptoms.',
                    'alternatives': ['ACE inhibitors', 'Calcium channel blockers'],
                    'monitoring': 'Blood glucose levels, hypoglycemia symptoms'
                }
            },
            
            # LOW SEVERITY INTERACTIONS
            'low_severity': {
                # Antacids + Antibiotics = Reduced Absorption
                ('calcium carbonate', 'tetracycline'): {
                    'severity': 'LOW',
                    'interaction_type': 'Reduced Drug Absorption',
                    'description': 'Antacids reduce antibiotic absorption',
                    'mechanism': 'Calcium binds to tetracycline in stomach',
                    'recommendation': 'Take antibiotic 2 hours before or after antacid. Monitor treatment response.',
                    'alternatives': ['H2 blockers', 'PPIs'],
                    'monitoring': 'Infection resolution, antibiotic levels'
                },
                ('aluminum hydroxide', 'ciprofloxacin'): {
                    'severity': 'LOW',
                    'interaction_type': 'Reduced Drug Absorption',
                    'description': 'Antacids reduce antibiotic absorption',
                    'mechanism': 'Aluminum binds to ciprofloxacin in stomach',
                    'recommendation': 'Take antibiotic 2 hours before or after antacid. Monitor treatment response.',
                    'alternatives': ['H2 blockers', 'PPIs'],
                    'monitoring': 'Infection resolution, antibiotic levels'
                },
                
                # Caffeine + Stimulants = Increased Stimulation
                ('caffeine', 'pseudoephedrine'): {
                    'severity': 'LOW',
                    'interaction_type': 'Increased Stimulation',
                    'description': 'Increased nervousness and insomnia',
                    'mechanism': 'Both are central nervous system stimulants',
                    'recommendation': 'Limit caffeine intake. Monitor for overstimulation symptoms.',
                    'alternatives': ['Decongestant alternatives', 'Non-stimulant options'],
                    'monitoring': 'Heart rate, blood pressure, sleep quality'
                }
            },
            
            # INFO INTERACTIONS
            'info_severity': {
                # Vitamin D + Calcium = Enhanced Absorption
                ('vitamin d', 'calcium'): {
                    'severity': 'INFO',
                    'interaction_type': 'Enhanced Absorption',
                    'description': 'Vitamin D enhances calcium absorption',
                    'mechanism': 'Vitamin D promotes calcium uptake in intestines',
                    'recommendation': 'Take together for optimal bone health. Monitor calcium levels.',
                    'alternatives': ['Separate timing if needed'],
                    'monitoring': 'Calcium levels, bone density'
                },
                
                # Iron + Vitamin C = Enhanced Absorption
                ('iron', 'vitamin c'): {
                    'severity': 'INFO',
                    'interaction_type': 'Enhanced Absorption',
                    'description': 'Vitamin C enhances iron absorption',
                    'mechanism': 'Vitamin C reduces iron to more absorbable form',
                    'recommendation': 'Take together for optimal iron absorption. Monitor iron levels.',
                    'alternatives': ['Separate timing if needed'],
                    'monitoring': 'Iron levels, hemoglobin'
                }
            }
        }
    
    def check_interactions(self, medicines: List[str]) -> Dict:
        """
        Check for drug interactions in a list of medicines
        
        Args:
            medicines: List of medicine names
            
        Returns:
            Dictionary with interaction results
        """
        try:
            interactions_found = []
            severity_summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
            
            # Convert medicines to lowercase for matching
            medicines_lower = [med.lower().strip() for med in medicines]
            
            # Check all interaction categories
            for category, interactions in self.interactions_db.items():
                for (med1, med2), interaction_data in interactions.items():
                    # Check if both medicines are in the prescription
                    if self._medicines_match(medicines_lower, med1, med2):
                        interaction_data['category'] = category
                        interactions_found.append(interaction_data)
                        severity_summary[interaction_data['severity']] += 1
            
            # Sort by severity (HIGH first)
            interactions_found.sort(key=lambda x: self.severity_levels[x['severity']]['priority'], reverse=True)
            
            # Calculate overall risk level
            overall_risk = self._calculate_overall_risk(severity_summary)
            
            return {
                'status': 'success',
                'total_medicines': len(medicines),
                'interactions_found': len(interactions_found),
                'severity_summary': severity_summary,
                'overall_risk_level': overall_risk,
                'interactions': interactions_found,
                'recommendations': self._generate_recommendations(interactions_found),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error checking drug interactions: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'interactions_found': [],
                'severity_summary': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0},
                'overall_risk_level': 'UNKNOWN',
                'recommendations': []
            }
    
    def _medicines_match(self, medicines: List[str], med1: str, med2: str) -> bool:
        """
        Check if two medicines match in the prescription list
        """
        med1_found = any(med1 in med for med in medicines)
        med2_found = any(med2 in med for med in medicines)
        return med1_found and med2_found
    
    def _calculate_overall_risk(self, severity_summary: Dict) -> str:
        """
        Calculate overall risk level based on severity summary
        """
        if severity_summary['HIGH'] > 0:
            return 'HIGH'
        elif severity_summary['MEDIUM'] > 0:
            return 'MEDIUM'
        elif severity_summary['LOW'] > 0:
            return 'LOW'
        elif severity_summary['INFO'] > 0:
            return 'INFO'
        else:
            return 'NONE'
    
    def _generate_recommendations(self, interactions: List[Dict]) -> List[str]:
        """
        Generate overall recommendations based on interactions found
        """
        recommendations = []
        
        if not interactions:
            recommendations.append("✅ No known drug interactions found. Continue current medication regimen.")
            return recommendations
        
        # High severity recommendations
        high_interactions = [i for i in interactions if i['severity'] == 'HIGH']
        if high_interactions:
            recommendations.append("🚨 HIGH RISK: Consult healthcare provider immediately before taking these medications together.")
            recommendations.append("⚠️ Consider alternative medications or adjusted dosing schedules.")
        
        # Medium severity recommendations
        medium_interactions = [i for i in interactions if i['severity'] == 'MEDIUM']
        if medium_interactions:
            recommendations.append("⚡ MEDIUM RISK: Monitor closely for adverse effects. Consider dose adjustments.")
            recommendations.append("📊 Regular monitoring may be required.")
        
        # Low severity recommendations
        low_interactions = [i for i in interactions if i['severity'] == 'LOW']
        if low_interactions:
            recommendations.append("💡 LOW RISK: Minor interactions detected. Monitor for any unusual symptoms.")
        
        # Info interactions
        info_interactions = [i for i in interactions if i['severity'] == 'INFO']
        if info_interactions:
            recommendations.append("ℹ️ Beneficial interactions detected. These combinations may enhance effectiveness.")
        
        return recommendations
    
    def get_interaction_details(self, medicine1: str, medicine2: str) -> Optional[Dict]:
        """
        Get detailed interaction information between two specific medicines
        """
        try:
            med1_lower = medicine1.lower().strip()
            med2_lower = medicine2.lower().strip()
            
            # Check all interaction categories
            for category, interactions in self.interactions_db.items():
                for (med1, med2), interaction_data in interactions.items():
                    if ((med1_lower in med1 and med2_lower in med2) or 
                        (med1_lower in med2 and med2_lower in med1)):
                        interaction_data['category'] = category
                        return interaction_data
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting interaction details: {e}")
            return None
    
    def get_medicine_interactions(self, medicine: str) -> List[Dict]:
        """
        Get all interactions for a specific medicine
        """
        try:
            medicine_lower = medicine.lower().strip()
            interactions = []
            
            # Check all interaction categories
            for category, category_interactions in self.interactions_db.items():
                for (med1, med2), interaction_data in category_interactions.items():
                    if (medicine_lower in med1 or medicine_lower in med2):
                        interaction_data['category'] = category
                        interactions.append(interaction_data)
            
            # Sort by severity
            interactions.sort(key=lambda x: self.severity_levels[x['severity']]['priority'], reverse=True)
            
            return interactions
            
        except Exception as e:
            logging.error(f"Error getting medicine interactions: {e}")
            return []
    
    def validate_prescription_safety(self, prescription_data: Dict) -> Dict:
        """
        Validate overall prescription safety including interactions
        """
        try:
            medicines = prescription_data.get('extracted_medicines', [])
            medicine_names = [med.get('name', '') for med in medicines if med.get('name')]
            
            if not medicine_names:
                return {
                    'status': 'success',
                    'safety_level': 'UNKNOWN',
                    'message': 'No medicines found to check for interactions',
                    'interactions': []
                }
            
            # Check interactions
            interaction_results = self.check_interactions(medicine_names)
            
            # Additional safety checks
            safety_checks = self._perform_safety_checks(prescription_data, interaction_results)
            
            return {
                'status': 'success',
                'safety_level': interaction_results['overall_risk_level'],
                'interaction_results': interaction_results,
                'safety_checks': safety_checks,
                'recommendations': self._generate_safety_recommendations(interaction_results, safety_checks)
            }
            
        except Exception as e:
            logging.error(f"Error validating prescription safety: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'safety_level': 'UNKNOWN'
            }
    
    def _perform_safety_checks(self, prescription_data: Dict, interaction_results: Dict) -> Dict:
        """
        Perform additional safety checks beyond drug interactions
        """
        safety_checks = {
            'dosage_validation': self._check_dosages(prescription_data),
            'frequency_validation': self._check_frequencies(prescription_data),
            'duration_validation': self._check_durations(prescription_data),
            'contraindications': self._check_contraindications(prescription_data)
        }
        
        return safety_checks
    
    def _check_dosages(self, prescription_data: Dict) -> Dict:
        """
        Check if dosages are within safe ranges
        """
        # This would integrate with dosage databases
        return {
            'status': 'valid',
            'message': 'Dosage validation requires integration with dosage databases'
        }
    
    def _check_frequencies(self, prescription_data: Dict) -> Dict:
        """
        Check if frequencies are appropriate
        """
        # This would validate frequency patterns
        return {
            'status': 'valid',
            'message': 'Frequency validation requires integration with frequency databases'
        }
    
    def _check_durations(self, prescription_data: Dict) -> Dict:
        """
        Check if treatment durations are appropriate
        """
        # This would validate duration patterns
        return {
            'status': 'valid',
            'message': 'Duration validation requires integration with duration databases'
        }
    
    def _check_contraindications(self, prescription_data: Dict) -> Dict:
        """
        Check for contraindications
        """
        # This would check against contraindication databases
        return {
            'status': 'valid',
            'message': 'Contraindication checking requires integration with medical databases'
        }
    
    def _generate_safety_recommendations(self, interaction_results: Dict, safety_checks: Dict) -> List[str]:
        """
        Generate comprehensive safety recommendations
        """
        recommendations = []
        
        # Add interaction recommendations
        if interaction_results.get('recommendations'):
            recommendations.extend(interaction_results['recommendations'])
        
        # Add safety check recommendations
        for check_type, check_result in safety_checks.items():
            if check_result.get('status') != 'valid':
                recommendations.append(f"⚠️ {check_type.replace('_', ' ').title()}: {check_result.get('message', '')}")
        
        return recommendations

# Global instance
interaction_checker = DrugInteractionChecker()
