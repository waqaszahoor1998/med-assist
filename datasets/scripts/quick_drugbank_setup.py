#!/usr/bin/env python3
"""
Quick DrugBank Setup Script
A simplified script to get you started with the DrugBank data
"""

import json
import re
from typing import List, Dict

def extract_common_medicines(raw_data: str, limit: int = 50) -> List[Dict[str, str]]:
    """
    Extract the most common medicines from DrugBank data
    """
    # Split by drug entries
    drug_entries = re.split(r'"drugbank_id":\s*"DB\d+"', raw_data)
    
    medicines = []
    
    for i, entry in enumerate(drug_entries[:limit]):
        if not entry.strip():
            continue
        
        # Extract basic information
        name_match = re.search(r'"name":\s*"([^"]*)"', entry)
        indication_match = re.search(r'"indication":\s*"([^"]*)"', entry)
        description_match = re.search(r'"description":\s*"([^"]*)"', entry)
        dosage_match = re.search(r'"dosage":\s*"([^"]*)"', entry)
        
        if name_match:
            medicine = {
                "id": f"DB{i:05d}",
                "name": name_match.group(1),
                "indication": indication_match.group(1) if indication_match else "",
                "description": description_match.group(1) if description_match else "",
                "dosage": dosage_match.group(1) if dosage_match else ""
            }
            medicines.append(medicine)
    
    return medicines

def main():
    print("Quick DrugBank Setup")
    print("=" * 30)
    
    # Read the raw data
    try:
        with open("../../datasets/raw/drugbank_database.json", 'r') as f:
            raw_data = f.read()
        print("✓ DrugBank data loaded")
    except FileNotFoundError:
        print("❌ DrugBank database file not found!")
        return
    
    # Extract common medicines
    print("Extracting common medicines...")
    medicines = extract_common_medicines(raw_data, limit=100)
    print(f"✓ Extracted {len(medicines)} medicines")
    
    # Save to a simple format
    output_path = "../../datasets/processed/common_drugbank_medicines.json"
    with open(output_path, 'w') as f:
        json.dump({
            "version": "1.0",
            "source": "DrugBank 5.1.11",
            "total_medicines": len(medicines),
            "medicines": medicines
        }, f, indent=2)
    
    print(f"✓ Saved to {output_path}")
    
    # Show sample medicines
    print("\nSample medicines extracted:")
    for i, med in enumerate(medicines[:5]):
        print(f"{i+1}. {med['name']}")
        if med['indication']:
            print(f"   Indication: {med['indication'][:100]}...")
        print()

if __name__ == "__main__":
    main()
