#!/usr/bin/env python3
"""
Enhanced Medicine Alternatives Population Script
Uses official RxNorm and OpenFDA APIs to populate medicine alternatives
Based on official API documentation:
- RxNorm: https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
- OpenFDA: https://open.fda.gov/apis/
"""

import json
import os
import sys
import time
import requests
from typing import Dict, List, Optional, Set


class EnhancedAlternativePopulator:
    def __init__(self):
        self.rxnorm_base_url = "https://rxnav.nlm.nih.gov/REST"
        self.openfda_base_url = "https://api.fda.gov"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Medicine-Assistant-App/1.0'
        })
        self.populated_count = 0
        self.skipped_count = 0
        self.api_errors = 0
        
    def get_rxnorm_alternatives(self, medicine_name: str) -> List[str]:
        """Get alternatives using RxNorm API - findRxcuiByString and getRelatedByRelationship"""
        alternatives = set()
        
        try:
            # Step 1: Find RXCUI for the medicine name
            search_url = f"{self.rxnorm_base_url}/rxcui"
            params = {'name': medicine_name}
            
            print(f"    Searching RxNorm for: {medicine_name}")
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rxcui_list = data.get('idGroup', {}).get('rxnormId', [])
                
                if rxcui_list:
                    rxcui = rxcui_list[0]  # Use first RXCUI
                    print(f"    Found RXCUI: {rxcui}")
                    
                    # Step 2: Get related drugs using "has_tradename" and "has_generic" relationships
                    relationships = ['has_tradename', 'has_generic', 'tradename_of', 'generic_of']
                    
                    for relationship in relationships:
                        related_url = f"{self.rxnorm_base_url}/rxcui/{rxcui}/related"
                        related_params = {'rela': relationship}
                        
                        related_response = self.session.get(related_url, params=related_params, timeout=10)
                        
                        if related_response.status_code == 200:
                            related_data = related_response.json()
                            concept_groups = related_data.get('relatedGroup', {}).get('conceptGroup', [])
                            
                            for group in concept_groups:
                                concepts = group.get('conceptProperties', [])
                                for concept in concepts:
                                    if concept.get('name'):
                                        alternatives.add(concept['name'])
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    RxNorm API error: {e}")
            self.api_errors += 1
        
        return list(alternatives)[:5]  # Limit to 5 alternatives
    
    def get_openfda_alternatives(self, medicine_name: str) -> List[str]:
        """Get alternatives using OpenFDA API - drug/label endpoint"""
        alternatives = set()
        
        try:
            # Search OpenFDA drug labels
            search_url = f"{self.openfda_base_url}/drug/label.json"
            params = {
                'search': f'openfda.generic_name:"{medicine_name}" OR openfda.brand_name:"{medicine_name}"',
                'limit': 10
            }
            
            print(f"    Searching OpenFDA for: {medicine_name}")
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for result in results:
                    openfda = result.get('openfda', {})
                    
                    # Get generic names
                    generic_names = openfda.get('generic_name', [])
                    for name in generic_names:
                        if name and name.lower() != medicine_name.lower():
                            alternatives.add(name.title())
                    
                    # Get brand names
                    brand_names = openfda.get('brand_name', [])
                    for name in brand_names:
                        if name and name.lower() != medicine_name.lower():
                            alternatives.add(name.title())
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    OpenFDA API error: {e}")
            self.api_errors += 1
        
        return list(alternatives)[:5]  # Limit to 5 alternatives
    
    def get_therapeutic_alternatives(self, medicine_name: str) -> List[str]:
        """Get therapeutic alternatives based on medicine categories"""
        medicine_lower = medicine_name.lower()
        
        # Pain relievers and anti-inflammatory
        pain_meds = ['aspirin', 'ibuprofen', 'naproxen', 'acetaminophen', 'paracetamol', 'celecoxib', 'meloxicam']
        if any(pain in medicine_lower for pain in pain_meds):
            return ['Paracetamol', 'Ibuprofen', 'Aspirin', 'Naproxen', 'Celecoxib']
        
        # Diabetes medications
        diabetes_meds = ['metformin', 'glipizide', 'glyburide', 'sitagliptin', 'pioglitazone', 'rosiglitazone']
        if any(diabetes in medicine_lower for diabetes in diabetes_meds):
            return ['Metformin', 'Glipizide', 'Glyburide', 'Sitagliptin', 'Pioglitazone']
        
        # Blood pressure medications
        bp_meds = ['lisinopril', 'enalapril', 'captopril', 'ramipril', 'losartan', 'valsartan', 'amlodipine']
        if any(bp in medicine_lower for bp in bp_meds):
            return ['Lisinopril', 'Enalapril', 'Captopril', 'Ramipril', 'Losartan']
        
        # Cholesterol medications
        chol_meds = ['simvastatin', 'atorvastatin', 'lovastatin', 'pravastatin', 'rosuvastatin', 'fluvastatin']
        if any(chol in medicine_lower for chol in chol_meds):
            return ['Simvastatin', 'Atorvastatin', 'Lovastatin', 'Pravastatin', 'Rosuvastatin']
        
        # Proton pump inhibitors
        ppi_meds = ['omeprazole', 'lansoprazole', 'pantoprazole', 'esomeprazole', 'rabeprazole', 'dexlansoprazole']
        if any(ppi in medicine_lower for ppi in ppi_meds):
            return ['Omeprazole', 'Lansoprazole', 'Pantoprazole', 'Esomeprazole', 'Rabeprazole']
        
        # Antibiotics
        abx_meds = ['amoxicillin', 'azithromycin', 'cephalexin', 'penicillin', 'doxycycline', 'ciprofloxacin']
        if any(abx in medicine_lower for abx in abx_meds):
            return ['Amoxicillin', 'Azithromycin', 'Cephalexin', 'Penicillin V', 'Doxycycline']
        
        # Antihistamines
        antihist_meds = ['cetirizine', 'loratadine', 'fexofenadine', 'diphenhydramine', 'chlorpheniramine']
        if any(antihist in medicine_lower for antihist in antihist_meds):
            return ['Cetirizine', 'Loratadine', 'Fexofenadine', 'Diphenhydramine', 'Chlorpheniramine']
        
        # Anticoagulants
        anticoag_meds = ['warfarin', 'apixaban', 'rivaroxaban', 'dabigatran', 'heparin', 'enoxaparin']
        if any(anticoag in medicine_lower for anticoag in anticoag_meds):
            return ['Warfarin', 'Apixaban', 'Rivaroxaban', 'Dabigatran', 'Heparin']
        
        # Gout medications
        gout_meds = ['allopurinol', 'febuxostat', 'probenecid', 'colchicine', 'sulfinpyrazone']
        if any(gout in medicine_lower for gout in gout_meds):
            return ['Allopurinol', 'Febuxostat', 'Probenecid', 'Colchicine', 'Sulfinpyrazone']
        
        # Corticosteroids
        steroid_meds = ['fluticasone', 'mometasone', 'budesonide', 'triamcinolone', 'prednisolone']
        if any(steroid in medicine_lower for steroid in steroid_meds):
            return ['Fluticasone', 'Mometasone', 'Budesonide', 'Triamcinolone', 'Prednisolone']
        
        return []
    
    def populate_alternatives_for_medicine(self, medicine_name: str) -> str:
        """Get alternatives for a single medicine using all available sources"""
        print(f"  Processing: {medicine_name}")
        
        alternatives = set()
        
        # Try RxNorm API first
        rxnorm_alternatives = self.get_rxnorm_alternatives(medicine_name)
        alternatives.update(rxnorm_alternatives)
        
        # Try OpenFDA API
        openfda_alternatives = self.get_openfda_alternatives(medicine_name)
        alternatives.update(openfda_alternatives)
        
        # If no API alternatives found, use therapeutic categories
        if not alternatives:
            therapeutic_alternatives = self.get_therapeutic_alternatives(medicine_name)
            alternatives.update(therapeutic_alternatives)
        
        # Clean up alternatives (remove duplicates and the medicine itself)
        clean_alternatives = []
        for alt in alternatives:
            if alt and alt.lower() != medicine_name.lower():
                clean_alternatives.append(alt)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_alternatives = []
        for alt in clean_alternatives:
            if alt not in seen:
                seen.add(alt)
                unique_alternatives.append(alt)
        
        # Limit to 3 alternatives
        final_alternatives = unique_alternatives[:3]
        
        if final_alternatives:
            result = ', '.join(final_alternatives)
            print(f"    ✅ Found alternatives: {result}")
            return result
        else:
            print(f"    ⚠️  No alternatives found")
            return 'Not available'
    
    def populate_database_alternatives(self, db_path: str, output_path: str = None, limit: int = None):
        """Populate alternatives for medicines in the database"""
        if output_path is None:
            output_path = db_path.replace('.json', '_with_alternatives.json')
        
        print(f"Loading database from {db_path}...")
        
        # Load database
        with open(db_path, 'r') as f:
            db_data = json.load(f)
        
        if isinstance(db_data, dict) and 'medicines' in db_data:
            medicines = db_data['medicines']
            is_dict_format = True
        elif isinstance(db_data, list):
            medicines = db_data
            is_dict_format = False
        else:
            print("❌ Invalid database format")
            return
        
        # Limit processing if specified
        if limit:
            medicines = medicines[:limit]
        
        print(f"Processing {len(medicines)} medicines...")
        
        # Process each medicine
        for i, medicine in enumerate(medicines, 1):
            medicine_name = medicine.get('name', '')
            current_alternatives = medicine.get('alternatives', '')
            
            print(f"\n[{i}/{len(medicines)}] {medicine_name}")
            
            # Skip if already has alternatives
            if current_alternatives and current_alternatives.strip() and current_alternatives != 'Not available':
                print(f"  ✅ Already has alternatives: {current_alternatives}")
                self.skipped_count += 1
                continue
            
            # Get alternatives
            alternatives = self.populate_alternatives_for_medicine(medicine_name)
            medicine['alternatives'] = alternatives
            
            if alternatives != 'Not available':
                self.populated_count += 1
            else:
                self.skipped_count += 1
        
        # Save updated database
        print(f"\nSaving updated database to {output_path}...")
        
        if is_dict_format:
            updated_data = db_data
        else:
            updated_data = medicines
        
        with open(output_path, 'w') as f:
            json.dump(updated_data, f, indent=2)
        
        print(f"\n🎉 Database update complete!")
        print(f"✅ Populated alternatives for: {self.populated_count} medicines")
        print(f"⚠️  No alternatives found for: {self.skipped_count} medicines")
        print(f"❌ API errors encountered: {self.api_errors}")
        print(f"📁 Updated database saved to: {output_path}")


def main():
    """Main function to run the enhanced alternative population script"""
    print("🔍 Enhanced Medicine Alternatives Population Script")
    print("Using official RxNorm and OpenFDA APIs")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('api'):
        print("❌ Please run this script from the backend directory")
        return
    
    # Initialize populator
    populator = EnhancedAlternativePopulator()
    
    # Define database paths
    current_db = 'medicines_database.json'
    enhanced_db = '../datasets/processed/enhanced_medicine_database.json'
    
    # Test with a small sample first
    print("🧪 Testing with first 5 medicines from enhanced database...")
    
    if os.path.exists(enhanced_db):
        populator.populate_database_alternatives(enhanced_db, 'test_alternatives.json', limit=5)
        
        print(f"\n📊 Test Results:")
        print(f"  Populated: {populator.populated_count}")
        print(f"  Skipped: {populator.skipped_count}")
        print(f"  API Errors: {populator.api_errors}")
        
        if populator.api_errors == 0:
            print(f"\n✅ API integration working! Ready to process full database.")
            proceed = input("Process full database? (y/n): ").strip().lower()
            if proceed == 'y':
                populator = EnhancedAlternativePopulator()  # Reset counters
                populator.populate_database_alternatives(enhanced_db, 'enhanced_medicines_with_alternatives.json')
        else:
            print(f"\n⚠️  Some API errors occurred. Check network connection and API availability.")
    else:
        print(f"❌ Enhanced database not found: {enhanced_db}")


if __name__ == '__main__':
    main()
