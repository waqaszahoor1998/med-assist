#!/usr/bin/env python3
"""
Script to populate medicine alternatives from internet sources
Uses OpenFDA and RxNorm APIs to find alternative medicines
"""

import json
import os
import sys
import time
from typing import Dict, List, Optional

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.openfda_client import OpenFDAClient
from api.rxnorm_client import RxNormClient


class AlternativePopulator:
    def __init__(self):
        self.openfda_client = OpenFDAClient()
        self.rxnorm_client = RxNormClient()
        self.populated_count = 0
        self.skipped_count = 0
        
    def find_alternatives_from_apis(self, medicine_name: str) -> List[str]:
        """Find alternatives using OpenFDA and RxNorm APIs"""
        alternatives = set()
        
        try:
            # Try OpenFDA first
            print(f"  Checking OpenFDA for {medicine_name}...")
            openfda_data = self.openfda_client.get_drug_info(medicine_name)
            
            if openfda_data and 'drug_interactions' in openfda_data:
                interactions = openfda_data['drug_interactions']
                if isinstance(interactions, list):
                    for interaction in interactions:
                        if isinstance(interaction, dict) and 'drug_name' in interaction:
                            alternatives.add(interaction['drug_name'])
                elif isinstance(interactions, str):
                    # Parse comma-separated alternatives
                    for alt in interactions.split(','):
                        alternatives.add(alt.strip())
            
            # Try RxNorm for drug relationships
            print(f"  Checking RxNorm for {medicine_name}...")
            rxnorm_data = self.rxnorm_client.find_drug_by_name(medicine_name)
            
            if rxnorm_data and 'related_drugs' in rxnorm_data:
                for related in rxnorm_data['related_drugs']:
                    if isinstance(related, dict) and 'name' in related:
                        alternatives.add(related['name'])
                    elif isinstance(related, str):
                        alternatives.add(related)
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Error fetching alternatives: {e}")
        
        return list(alternatives)
    
    def get_therapeutic_alternatives(self, medicine_name: str) -> List[str]:
        """Get therapeutic alternatives based on medicine type"""
        medicine_lower = medicine_name.lower()
        
        # Pain relievers
        if any(pain in medicine_lower for pain in ['aspirin', 'ibuprofen', 'naproxen', 'acetaminophen', 'paracetamol']):
            return ['Paracetamol', 'Ibuprofen', 'Aspirin', 'Naproxen', 'Celecoxib']
        
        # Diabetes medications
        elif any(diabetes in medicine_lower for diabetes in ['metformin', 'glipizide', 'glyburide', 'sitagliptin']):
            return ['Metformin', 'Glipizide', 'Glyburide', 'Sitagliptin', 'Pioglitazone']
        
        # Blood pressure medications
        elif any(bp in medicine_lower for bp in ['lisinopril', 'enalapril', 'captopril', 'ramipril']):
            return ['Lisinopril', 'Enalapril', 'Captopril', 'Ramipril', 'Losartan']
        
        # Cholesterol medications
        elif any(chol in medicine_lower for chol in ['simvastatin', 'atorvastatin', 'lovastatin', 'pravastatin']):
            return ['Simvastatin', 'Atorvastatin', 'Lovastatin', 'Pravastatin', 'Rosuvastatin']
        
        # Proton pump inhibitors
        elif any(ppi in medicine_lower for ppi in ['omeprazole', 'lansoprazole', 'pantoprazole', 'esomeprazole']):
            return ['Omeprazole', 'Lansoprazole', 'Pantoprazole', 'Esomeprazole', 'Rabeprazole']
        
        # Antibiotics
        elif any(abx in medicine_lower for abx in ['amoxicillin', 'azithromycin', 'cephalexin', 'penicillin']):
            return ['Amoxicillin', 'Azithromycin', 'Cephalexin', 'Penicillin V', 'Doxycycline']
        
        # Antihistamines
        elif any(antihist in medicine_lower for antihist in ['cetirizine', 'loratadine', 'fexofenadine', 'diphenhydramine']):
            return ['Cetirizine', 'Loratadine', 'Fexofenadine', 'Diphenhydramine', 'Chlorpheniramine']
        
        # Anticoagulants
        elif any(anticoag in medicine_lower for anticoag in ['warfarin', 'apixaban', 'rivaroxaban', 'dabigatran']):
            return ['Warfarin', 'Apixaban', 'Rivaroxaban', 'Dabigatran', 'Heparin']
        
        # Gout medications
        elif any(gout in medicine_lower for gout in ['allopurinol', 'febuxostat', 'probenecid', 'colchicine']):
            return ['Allopurinol', 'Febuxostat', 'Probenecid', 'Colchicine', 'Sulfinpyrazone']
        
        # Corticosteroids
        elif any(steroid in medicine_lower for steroid in ['fluticasone', 'mometasone', 'budesonide', 'triamcinolone']):
            return ['Fluticasone', 'Mometasone', 'Budesonide', 'Triamcinolone', 'Prednisolone']
        
        return []
    
    def populate_database_alternatives(self, db_path: str, output_path: str = None):
        """Populate alternatives for medicines that don't have them"""
        if output_path is None:
            output_path = db_path
        
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
        
        print(f"Found {len(medicines)} medicines in database")
        
        # Process each medicine
        for i, medicine in enumerate(medicines, 1):
            medicine_name = medicine.get('name', '')
            current_alternatives = medicine.get('alternatives', '')
            
            print(f"\n[{i}/{len(medicines)}] Processing: {medicine_name}")
            
            # Skip if already has alternatives
            if current_alternatives and current_alternatives.strip() and current_alternatives != 'Not available':
                print(f"  ✅ Already has alternatives: {current_alternatives}")
                self.skipped_count += 1
                continue
            
            # Try to find alternatives
            alternatives = []
            
            # First try APIs
            api_alternatives = self.find_alternatives_from_apis(medicine_name)
            if api_alternatives:
                alternatives.extend(api_alternatives[:3])  # Limit to 3 from APIs
            
            # If no API alternatives, use therapeutic categories
            if not alternatives:
                therapeutic_alternatives = self.get_therapeutic_alternatives(medicine_name)
                if therapeutic_alternatives:
                    # Remove the medicine itself from alternatives
                    alternatives = [alt for alt in therapeutic_alternatives if alt.lower() != medicine_name.lower()]
                    alternatives = alternatives[:3]  # Limit to 3
            
            # Update medicine with alternatives
            if alternatives:
                medicine['alternatives'] = ', '.join(alternatives)
                print(f"  ✅ Added alternatives: {medicine['alternatives']}")
                self.populated_count += 1
            else:
                print(f"  ⚠️  No alternatives found")
                medicine['alternatives'] = 'Not available'
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
        print(f"⚠️  Skipped (already had alternatives): {self.skipped_count} medicines")
        print(f"📁 Updated database saved to: {output_path}")


def main():
    """Main function to run the alternative population script"""
    print("🔍 Medicine Alternatives Population Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('api'):
        print("❌ Please run this script from the backend directory")
        return
    
    # Initialize populator
    populator = AlternativePopulator()
    
    # Define database paths
    current_db = 'medicines_database.json'
    enhanced_db = '../datasets/processed/enhanced_medicine_database.json'
    backup_db = 'medicines_database_backup.json'
    
    # Create backup
    if os.path.exists(current_db):
        print(f"Creating backup: {backup_db}")
        with open(current_db, 'r') as src, open(backup_db, 'w') as dst:
            dst.write(src.read())
    
    # Choose which database to populate
    print(f"\nAvailable databases:")
    print(f"1. Current database ({current_db})")
    if os.path.exists(enhanced_db):
        print(f"2. Enhanced database ({enhanced_db})")
    
    choice = input("\nWhich database to populate? (1 or 2): ").strip()
    
    if choice == '2' and os.path.exists(enhanced_db):
        db_path = enhanced_db
        output_path = enhanced_db.replace('.json', '_with_alternatives.json')
    else:
        db_path = current_db
        output_path = current_db.replace('.json', '_enhanced.json')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    # Populate alternatives
    populator.populate_database_alternatives(db_path, output_path)


if __name__ == '__main__':
    main()
