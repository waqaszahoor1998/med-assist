#!/usr/bin/env python3
"""
Extract medical knowledge from enhanced database for database import
"""

import json
import os
from pathlib import Path


def extract_medical_knowledge():
    """Extract medical knowledge from enhanced database"""
    
    # Paths
    enhanced_db_path = Path("../datasets/processed/enhanced_ultimate_medicine_database.json")
    output_path = Path("../datasets/processed/wiki_medical_knowledge.json")
    
    print("Extracting medical knowledge from enhanced database...")
    
    if not enhanced_db_path.exists():
        print(f"❌ Enhanced database not found: {enhanced_db_path}")
        return
    
    # Load enhanced database
    with open(enhanced_db_path, 'r', encoding='utf-8') as f:
        enhanced_data = json.load(f)
    
    medicines = enhanced_data.get('medicines', [])
    print(f"Processing {len(medicines)} medicines...")
    
    # Extract medical knowledge
    medical_knowledge = []
    processed_terms = set()
    
    for medicine in medicines:
        if not isinstance(medicine, dict):
            continue
            
        # Extract medical explanation if available
        medical_explanation = medicine.get('medical_explanation', '')
        if medical_explanation and medical_explanation.strip():
            term = medicine.get('name', '').strip()
            if term and term not in processed_terms:
                medical_knowledge.append({
                    'term': term,
                    'explanation': medical_explanation.strip(),
                    'category': medicine.get('category', 'Medicine'),
                    'related_terms': medicine.get('brand_names', []) + [medicine.get('generic_name', '')],
                    'source': 'Enhanced Database'
                })
                processed_terms.add(term)
        
        # Extract from alternative names and brand names
        brand_names = medicine.get('brand_names', [])
        for brand in brand_names:
            if brand and brand not in processed_terms:
                medical_knowledge.append({
                    'term': brand,
                    'explanation': f"Brand name for {medicine.get('name', 'unknown medicine')}. {medical_explanation}",
                    'category': 'Brand Name',
                    'related_terms': [medicine.get('name', ''), medicine.get('generic_name', '')],
                    'source': 'Enhanced Database'
                })
                processed_terms.add(brand)
    
    # Save medical knowledge
    knowledge_data = {
        'medical_knowledge': medical_knowledge,
        'total_entries': len(medical_knowledge),
        'source': 'Enhanced Ultimate Medicine Database',
        'extraction_date': '2025-10-01'
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Medical knowledge extracted successfully!")
    print(f"   - Total entries: {len(medical_knowledge)}")
    print(f"   - Saved to: {output_path}")
    
    # Show sample entries
    if medical_knowledge:
        print("\n📋 Sample entries:")
        for i, entry in enumerate(medical_knowledge[:3]):
            print(f"   {i+1}. {entry['term']} - {entry['category']}")


if __name__ == "__main__":
    extract_medical_knowledge()
