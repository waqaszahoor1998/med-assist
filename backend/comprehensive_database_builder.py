#!/usr/bin/env python3
"""
Comprehensive Medicine Database Builder
Parses DrugBank CSV, enhances with OpenFDA API, and integrates molecular structures
"""

import json
import csv
import os
import sys
import time
import requests
import re
from typing import Dict, List, Any, Optional
import logging

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.openfda_client import OpenFDAClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveDatabaseBuilder:
    def __init__(self):
        self.drugbank_csv_path = '../datasets/raw/drugbank vocabulary.csv'
        self.sdf_path = '../datasets/raw/open structures.sdf'
        self.output_path = '../datasets/processed/comprehensive_medicine_database.json'
        self.openfda_client = OpenFDAClient()
        self.medicines = []
        self.processed_count = 0
        self.api_enhanced_count = 0
        
    def parse_drugbank_csv(self) -> List[Dict[str, Any]]:
        """Parse DrugBank CSV and extract medicine information"""
        logger.info(f"Parsing DrugBank CSV: {self.drugbank_csv_path}")
        
        medicines = []
        
        try:
            with open(self.drugbank_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    if row_num % 1000 == 0:
                        logger.info(f"Processed {row_num} entries...")
                    
                    # Extract medicine information
                    medicine = self._parse_medicine_row(row)
                    if medicine:
                        medicines.append(medicine)
                        
        except Exception as e:
            logger.error(f"Error parsing DrugBank CSV: {e}")
            return []
        
        logger.info(f"Successfully parsed {len(medicines)} medicines from DrugBank CSV")
        return medicines
    
    def _parse_medicine_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Parse a single row from DrugBank CSV"""
        try:
            drugbank_id = row.get('DrugBank ID', '').strip()
            common_name = row.get('Common name', '').strip()
            cas = row.get('CAS', '').strip()
            unii = row.get('UNII', '').strip()
            synonyms = row.get('Synonyms', '').strip()
            inchi_key = row.get('Standard InChI Key', '').strip()
            
            # Skip if no common name
            if not common_name:
                return None
            
            # Parse synonyms
            synonym_list = []
            if synonyms:
                # Split by common delimiters
                synonyms = re.sub(r'[\[\]]', '', synonyms)  # Remove brackets
                synonym_list = [s.strip() for s in synonyms.split('|') if s.strip()]
                synonym_list = synonym_list[:10]  # Limit to 10 synonyms
            
            # Clean common name
            common_name = self._clean_medicine_name(common_name)
            
            medicine = {
                'drugbank_id': drugbank_id,
                'name': common_name,
                'generic_name': common_name,
                'brand_names': synonym_list[:5] if synonym_list else [],  # First 5 as brand names
                'synonyms': synonym_list,
                'cas_number': cas,
                'unii': unii,
                'inchi_key': inchi_key,
                'source': 'DrugBank',
                'has_structure': bool(inchi_key),
                'chemical_structure': {
                    'inchi_key': inchi_key,
                    'cas_number': cas,
                    'unii': unii
                } if inchi_key else None,
                
                # Fields to be populated by API enhancement
                'indications': '',
                'side_effects': '',
                'dosage': '',
                'warnings': '',
                'contraindications': '',
                'pregnancy_category': '',
                'storage_instructions': '',
                'administration_instructions': '',
                'drug_interactions': '',
                'food_interactions': '',
                'overdose_information': '',
                'pharmacology': '',
                'pharmacokinetics': '',
                'monitoring_requirements': '',
                'patient_counseling': '',
                'cost_information': '',
                'alternatives': '',
                'categories': '',
                'dosage_forms': '',
                'common_doses': '',
                'max_daily_dose': '',
                'frequency': '',
                
                # API enhancement flags
                'api_enhanced': False,
                'enhancement_date': None
            }
            
            return medicine
            
        except Exception as e:
            logger.error(f"Error parsing medicine row: {e}")
            return None
    
    def _clean_medicine_name(self, name: str) -> str:
        """Clean and standardize medicine name"""
        if not name:
            return ''
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common suffixes in brackets
        name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
        
        # Capitalize first letter of each word
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name.strip()
    
    def enhance_with_openfda(self, medicines: List[Dict[str, Any]], limit: int = None) -> List[Dict[str, Any]]:
        """Enhance medicines with OpenFDA API data"""
        logger.info(f"Enhancing {len(medicines)} medicines with OpenFDA API...")
        
        if limit:
            medicines = medicines[:limit]
        
        enhanced_medicines = []
        
        for i, medicine in enumerate(medicines, 1):
            if i % 100 == 0:
                logger.info(f"Enhanced {i}/{len(medicines)} medicines...")
            
            try:
                # Get OpenFDA data
                openfda_data = self.openfda_client.get_drug_info(medicine['name'])
                
                if openfda_data:
                    # Enhance medicine with OpenFDA data
                    enhanced_medicine = self._merge_openfda_data(medicine, openfda_data)
                    enhanced_medicine['api_enhanced'] = True
                    enhanced_medicine['enhancement_date'] = time.strftime('%Y-%m-%d')
                    self.api_enhanced_count += 1
                else:
                    enhanced_medicine = medicine
                
                enhanced_medicines.append(enhanced_medicine)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error enhancing {medicine['name']}: {e}")
                enhanced_medicines.append(medicine)
        
        logger.info(f"Successfully enhanced {self.api_enhanced_count} medicines with OpenFDA API")
        return enhanced_medicines
    
    def _merge_openfda_data(self, medicine: Dict[str, Any], openfda_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge OpenFDA data into medicine record"""
        enhanced = medicine.copy()
        
        # Extract useful fields from OpenFDA data
        if 'openfda' in openfda_data:
            openfda = openfda_data['openfda']
            
            # Brand names
            if 'brand_name' in openfda and openfda['brand_name']:
                existing_brands = enhanced.get('brand_names', [])
                new_brands = [b for b in openfda['brand_name'] if b not in existing_brands]
                enhanced['brand_names'].extend(new_brands[:5])  # Limit to 5 additional
            
            # Generic names
            if 'generic_name' in openfda and openfda['generic_name']:
                if not enhanced.get('generic_name'):
                    enhanced['generic_name'] = openfda['generic_name'][0]
            
            # Dosage forms
            if 'dosage_form' in openfda and openfda['dosage_form']:
                enhanced['dosage_forms'] = ', '.join(openfda['dosage_form'][:5])
        
        # Drug interactions
        if 'drug_interactions' in openfda_data:
            interactions = openfda_data['drug_interactions']
            if isinstance(interactions, list):
                enhanced['drug_interactions'] = ', '.join(interactions[:10])
            elif isinstance(interactions, str):
                enhanced['drug_interactions'] = interactions
        
        # Warnings and precautions
        if 'warnings' in openfda_data:
            warnings = openfda_data['warnings']
            if isinstance(warnings, list):
                enhanced['warnings'] = '; '.join(warnings[:5])
            elif isinstance(warnings, str):
                enhanced['warnings'] = warnings
        
        # Indications
        if 'indications_and_usage' in openfda_data:
            enhanced['indications'] = openfda_data['indications_and_usage']
        
        # Dosage and administration
        if 'dosage_and_administration' in openfda_data:
            enhanced['administration_instructions'] = openfda_data['dosage_and_administration']
        
        # Adverse reactions
        if 'adverse_reactions' in openfda_data:
            enhanced['side_effects'] = openfda_data['adverse_reactions']
        
        # Contraindications
        if 'contraindications' in openfda_data:
            enhanced['contraindications'] = openfda_data['contraindications']
        
        # Pregnancy category
        if 'pregnancy' in openfda_data:
            enhanced['pregnancy_category'] = openfda_data['pregnancy']
        
        # Storage
        if 'storage_and_handling' in openfda_data:
            enhanced['storage_instructions'] = openfda_data['storage_and_handling']
        
        return enhanced
    
    def add_molecular_structures(self, medicines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add molecular structure information from SDF file"""
        logger.info("Adding molecular structures from SDF file...")
        
        # For now, we'll mark medicines that have InChI keys as having structures
        # The full SDF parsing can be implemented later
        enhanced_medicines = []
        
        for medicine in medicines:
            enhanced = medicine.copy()
            
            # If medicine has InChI key, mark as having structure
            if enhanced.get('inchi_key'):
                enhanced['has_structure'] = True
                enhanced['chemical_structure'] = {
                    'inchi_key': enhanced['inchi_key'],
                    'cas_number': enhanced.get('cas_number', ''),
                    'unii': enhanced.get('unii', ''),
                    'source': 'DrugBank'
                }
            
            enhanced_medicines.append(enhanced)
        
        logger.info(f"Added molecular structure information for {len([m for m in enhanced_medicines if m.get('has_structure')])} medicines")
        return enhanced_medicines
    
    def populate_categories_and_alternatives(self, medicines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Populate medicine categories and alternatives based on therapeutic classes"""
        logger.info("Populating categories and alternatives...")
        
        # Define therapeutic categories
        categories = {
            'analgesic': ['Paracetamol', 'Ibuprofen', 'Aspirin', 'Naproxen', 'Morphine', 'Codeine', 'Tramadol'],
            'antibiotic': ['Amoxicillin', 'Azithromycin', 'Cephalexin', 'Penicillin', 'Doxycycline', 'Ciprofloxacin'],
            'antihistamine': ['Cetirizine', 'Loratadine', 'Fexofenadine', 'Diphenhydramine', 'Chlorpheniramine'],
            'anticoagulant': ['Warfarin', 'Heparin', 'Aspirin', 'Clopidogrel', 'Apixaban', 'Rivaroxaban'],
            'antidiabetic': ['Metformin', 'Insulin', 'Glipizide', 'Glyburide', 'Sitagliptin', 'Pioglitazone'],
            'antihypertensive': ['Lisinopril', 'Enalapril', 'Captopril', 'Ramipril', 'Losartan', 'Valsartan', 'Amlodipine'],
            'anticholesterol': ['Simvastatin', 'Atorvastatin', 'Lovastatin', 'Pravastatin', 'Rosuvastatin'],
            'ppi': ['Omeprazole', 'Lansoprazole', 'Pantoprazole', 'Esomeprazole', 'Rabeprazole'],
            'steroid': ['Prednisolone', 'Dexamethasone', 'Hydrocortisone', 'Fluticasone', 'Budesonide'],
            'antidepressant': ['Fluoxetine', 'Sertraline', 'Citalopram', 'Paroxetine', 'Escitalopram']
        }
        
        enhanced_medicines = []
        
        for medicine in medicines:
            enhanced = medicine.copy()
            medicine_name = enhanced['name'].lower()
            
            # Find category
            found_category = None
            for category, medicines_in_category in categories.items():
                if any(med.lower() in medicine_name for med in medicines_in_category):
                    found_category = category
                    break
            
            if found_category:
                enhanced['categories'] = found_category
                # Get alternatives from same category
                alternatives = [med for med in categories[found_category] if med.lower() != medicine_name]
                enhanced['alternatives'] = ', '.join(alternatives[:5])  # Limit to 5 alternatives
            
            enhanced_medicines.append(enhanced)
        
        logger.info("Categories and alternatives populated")
        return enhanced_medicines
    
    def save_database(self, medicines: List[Dict[str, Any]]) -> str:
        """Save comprehensive medicine database to file"""
        logger.info(f"Saving comprehensive database with {len(medicines)} medicines...")
        
        database = {
            'version': '3.0',
            'source': 'DrugBank + OpenFDA + Molecular Structures',
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_medicines': len(medicines),
            'api_enhanced': self.api_enhanced_count,
            'with_structures': len([m for m in medicines if m.get('has_structure')]),
            'medicines': medicines
        }
        
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Database saved to: {self.output_path}")
            return self.output_path
            
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            return None
    
    def build_comprehensive_database(self, limit: int = None, enhance_with_api: bool = True):
        """Build comprehensive medicine database"""
        logger.info("Starting comprehensive medicine database build...")
        
        # Step 1: Parse DrugBank CSV
        medicines = self.parse_drugbank_csv()
        if not medicines:
            logger.error("Failed to parse DrugBank CSV")
            return None
        
        # Step 2: Enhance with OpenFDA API (if requested)
        if enhance_with_api:
            medicines = self.enhance_with_openfda(medicines, limit)
        
        # Step 3: Add molecular structures
        medicines = self.add_molecular_structures(medicines)
        
        # Step 4: Populate categories and alternatives
        medicines = self.populate_categories_and_alternatives(medicines)
        
        # Step 5: Save database
        output_path = self.save_database(medicines)
        
        if output_path:
            logger.info(f"Comprehensive database build complete!")
            logger.info(f"Total medicines: {len(medicines)}")
            logger.info(f"API enhanced: {self.api_enhanced_count}")
            logger.info(f"With structures: {len([m for m in medicines if m.get('has_structure')])}")
            logger.info(f"Saved to: {output_path}")
        
        return output_path


def main():
    """Main function"""
    print("Comprehensive Medicine Database Builder")
    print("=" * 50)
    
    builder = ComprehensiveDatabaseBuilder()
    
    # Ask user for options
    print("\nOptions:")
    print("1. Parse DrugBank CSV only (fast)")
    print("2. Parse + enhance with OpenFDA API (slow, comprehensive)")
    print("3. Parse + enhance limited medicines (balanced)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        # Parse only
        output_path = builder.build_comprehensive_database(enhance_with_api=False)
    elif choice == '2':
        # Parse + enhance all
        output_path = builder.build_comprehensive_database(enhance_with_api=True)
    elif choice == '3':
        # Parse + enhance limited
        limit = int(input("How many medicines to enhance with API? (default 100): ") or "100")
        output_path = builder.build_comprehensive_database(limit=limit, enhance_with_api=True)
    else:
        print("Invalid choice")
        return
    
    if output_path:
        print(f"\nDatabase built successfully: {output_path}")
    else:
        print("\nDatabase build failed")


if __name__ == '__main__':
    main()
