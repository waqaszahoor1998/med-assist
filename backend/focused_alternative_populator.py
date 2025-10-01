#!/usr/bin/env python3
"""
Focused Medicine Alternatives Population Script
Focuses on common medicines and uses multiple strategies to find alternatives
"""

import json
import os
import sys
import time
import requests
from typing import Dict, List, Optional, Set


class FocusedAlternativePopulator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Medicine-Assistant-App/1.0'
        })
        
        # Common medicine categories with alternatives
        self.medicine_categories = {
            # Pain relievers
            'pain_relievers': {
                'medicines': ['aspirin', 'ibuprofen', 'naproxen', 'acetaminophen', 'paracetamol', 'celecoxib', 'meloxicam', 'diclofenac'],
                'alternatives': ['Paracetamol', 'Ibuprofen', 'Aspirin', 'Naproxen', 'Celecoxib', 'Meloxicam', 'Diclofenac']
            },
            
            # Diabetes medications
            'diabetes': {
                'medicines': ['metformin', 'glipizide', 'glyburide', 'sitagliptin', 'pioglitazone', 'rosiglitazone', 'insulin'],
                'alternatives': ['Metformin', 'Glipizide', 'Glyburide', 'Sitagliptin', 'Pioglitazone', 'Rosiglitazone', 'Insulin']
            },
            
            # Blood pressure medications
            'blood_pressure': {
                'medicines': ['lisinopril', 'enalapril', 'captopril', 'ramipril', 'losartan', 'valsartan', 'amlodipine', 'hydrochlorothiazide'],
                'alternatives': ['Lisinopril', 'Enalapril', 'Captopril', 'Ramipril', 'Losartan', 'Valsartan', 'Amlodipine', 'Hydrochlorothiazide']
            },
            
            # Cholesterol medications
            'cholesterol': {
                'medicines': ['simvastatin', 'atorvastatin', 'lovastatin', 'pravastatin', 'rosuvastatin', 'fluvastatin'],
                'alternatives': ['Simvastatin', 'Atorvastatin', 'Lovastatin', 'Pravastatin', 'Rosuvastatin', 'Fluvastatin']
            },
            
            # Proton pump inhibitors
            'ppi': {
                'medicines': ['omeprazole', 'lansoprazole', 'pantoprazole', 'esomeprazole', 'rabeprazole', 'dexlansoprazole'],
                'alternatives': ['Omeprazole', 'Lansoprazole', 'Pantoprazole', 'Esomeprazole', 'Rabeprazole', 'Dexlansoprazole']
            },
            
            # Antibiotics
            'antibiotics': {
                'medicines': ['amoxicillin', 'azithromycin', 'cephalexin', 'penicillin', 'doxycycline', 'ciprofloxacin', 'clindamycin'],
                'alternatives': ['Amoxicillin', 'Azithromycin', 'Cephalexin', 'Penicillin V', 'Doxycycline', 'Ciprofloxacin', 'Clindamycin']
            },
            
            # Antihistamines
            'antihistamines': {
                'medicines': ['cetirizine', 'loratadine', 'fexofenadine', 'diphenhydramine', 'chlorpheniramine', 'brompheniramine'],
                'alternatives': ['Cetirizine', 'Loratadine', 'Fexofenadine', 'Diphenhydramine', 'Chlorpheniramine', 'Brompheniramine']
            },
            
            # Anticoagulants
            'anticoagulants': {
                'medicines': ['warfarin', 'apixaban', 'rivaroxaban', 'dabigatran', 'heparin', 'enoxaparin'],
                'alternatives': ['Warfarin', 'Apixaban', 'Rivaroxaban', 'Dabigatran', 'Heparin', 'Enoxaparin']
            },
            
            # Gout medications
            'gout': {
                'medicines': ['allopurinol', 'febuxostat', 'probenecid', 'colchicine', 'sulfinpyrazone'],
                'alternatives': ['Allopurinol', 'Febuxostat', 'Probenecid', 'Colchicine', 'Sulfinpyrazone']
            },
            
            # Corticosteroids
            'steroids': {
                'medicines': ['fluticasone', 'mometasone', 'budesonide', 'triamcinolone', 'prednisolone', 'dexamethasone'],
                'alternatives': ['Fluticasone', 'Mometasone', 'Budesonide', 'Triamcinolone', 'Prednisolone', 'Dexamethasone']
            }
        }
        
        self.populated_count = 0
        self.skipped_count = 0
    
    def get_alternatives_for_medicine(self, medicine_name: str) -> List[str]:
        """Get alternatives for a medicine using category-based matching"""
        medicine_lower = medicine_name.lower()
        
        for category, data in self.medicine_categories.items():
            medicines = data['medicines']
            alternatives = data['alternatives']
            
            # Check if medicine matches any in this category
            for med in medicines:
                if med in medicine_lower or medicine_lower in med:
                    # Return alternatives excluding the medicine itself
                    filtered_alternatives = [alt for alt in alternatives if alt.lower() != medicine_name.lower()]
                    return filtered_alternatives[:3]  # Limit to 3 alternatives
        
        return []
    
    def create_enhanced_database(self, input_db_path: str, output_db_path: str):
        """Create enhanced database with alternatives for common medicines"""
        print(f"Loading database from {input_db_path}...")
        
        with open(input_db_path, 'r') as f:
            db_data = json.load(f)
        
        if isinstance(db_data, dict) and 'medicines' in db_data:
            medicines = db_data['medicines']
        elif isinstance(db_data, list):
            medicines = db_data
        else:
            print("❌ Invalid database format")
            return
        
        print(f"Processing {len(medicines)} medicines...")
        
        # Focus on first 100 medicines for testing
        medicines_to_process = medicines[:100]
        
        for i, medicine in enumerate(medicines_to_process, 1):
            medicine_name = medicine.get('name', '')
            current_alternatives = medicine.get('alternatives', '')
            
            print(f"[{i}/100] {medicine_name}")
            
            # Skip if already has alternatives
            if current_alternatives and current_alternatives.strip() and current_alternatives != 'Not available':
                print(f"  ✅ Already has alternatives: {current_alternatives}")
                self.skipped_count += 1
                continue
            
            # Get alternatives
            alternatives = self.get_alternatives_for_medicine(medicine_name)
            
            if alternatives:
                medicine['alternatives'] = ', '.join(alternatives)
                print(f"  ✅ Added alternatives: {medicine['alternatives']}")
                self.populated_count += 1
            else:
                print(f"  ⚠️  No alternatives found")
                medicine['alternatives'] = 'Not available'
                self.skipped_count += 1
        
        # Save enhanced database
        print(f"\nSaving enhanced database to {output_db_path}...")
        
        if isinstance(db_data, dict):
            db_data['medicines'] = medicines
            updated_data = db_data
        else:
            updated_data = medicines
        
        with open(output_db_path, 'w') as f:
            json.dump(updated_data, f, indent=2)
        
        print(f"\n🎉 Enhanced database creation complete!")
        print(f"✅ Populated alternatives for: {self.populated_count} medicines")
        print(f"⚠️  Skipped (already had alternatives): {self.skipped_count} medicines")
        print(f"📁 Enhanced database saved to: {output_db_path}")
    
    def update_current_database(self):
        """Update the current medicines_database.json with alternatives"""
        current_db = 'medicines_database.json'
        
        if not os.path.exists(current_db):
            print(f"❌ Database not found: {current_db}")
            return
        
        print(f"Loading current database: {current_db}")
        
        with open(current_db, 'r') as f:
            medicines = json.load(f)
        
        print(f"Processing {len(medicines)} medicines...")
        
        for i, medicine in enumerate(medicines, 1):
            medicine_name = medicine.get('name', '')
            current_alternatives = medicine.get('alternatives', '')
            
            print(f"[{i}/{len(medicines)}] {medicine_name}")
            
            # Skip if already has alternatives
            if current_alternatives and current_alternatives.strip() and current_alternatives != 'Not available':
                print(f"  ✅ Already has alternatives: {current_alternatives}")
                self.skipped_count += 1
                continue
            
            # Get alternatives
            alternatives = self.get_alternatives_for_medicine(medicine_name)
            
            if alternatives:
                medicine['alternatives'] = ', '.join(alternatives)
                print(f"  ✅ Added alternatives: {medicine['alternatives']}")
                self.populated_count += 1
            else:
                print(f"  ⚠️  No alternatives found")
                medicine['alternatives'] = 'Not available'
                self.skipped_count += 1
        
        # Save updated database
        backup_db = 'medicines_database_backup.json'
        print(f"\nCreating backup: {backup_db}")
        with open(current_db, 'r') as src, open(backup_db, 'w') as dst:
            dst.write(src.read())
        
        print(f"Saving updated database: {current_db}")
        with open(current_db, 'w') as f:
            json.dump(medicines, f, indent=2)
        
        print(f"\n🎉 Database update complete!")
        print(f"✅ Populated alternatives for: {self.populated_count} medicines")
        print(f"⚠️  Skipped (already had alternatives): {self.skipped_count} medicines")
        print(f"📁 Updated database saved to: {current_db}")
        print(f"📁 Backup saved to: {backup_db}")


def main():
    """Main function"""
    print("🔍 Focused Medicine Alternatives Population Script")
    print("Focusing on common medicine categories")
    print("=" * 60)
    
    if not os.path.exists('api'):
        print("❌ Please run this script from the backend directory")
        return
    
    populator = FocusedAlternativePopulator()
    
    # Update current database
    print("📝 Updating current medicines_database.json...")
    populator.update_current_database()
    
    # Also create enhanced version of large database
    enhanced_db = '../datasets/processed/enhanced_medicine_database.json'
    if os.path.exists(enhanced_db):
        print(f"\n📝 Creating enhanced version of large database...")
        populator = FocusedAlternativePopulator()  # Reset counters
        populator.create_enhanced_database(enhanced_db, 'enhanced_medicines_with_alternatives.json')


if __name__ == '__main__':
    main()
