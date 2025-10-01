#!/usr/bin/env python3
"""
DrugBank Database Processing Script
Converts DrugBank data into a format compatible with the medicine assistant system
"""

import json
import re
from typing import Dict, List, Any

def parse_drugbank_data(raw_data: str) -> List[Dict[str, Any]]:
    """
    Parse the raw DrugBank data string into structured JSON
    """
    # Split by drug entries (look for "drugbank_id": "DB")
    drug_entries = re.split(r'"drugbank_id":\s*"DB\d+"', raw_data)
    
    # Remove empty first entry
    if drug_entries and not drug_entries[0].strip():
        drug_entries = drug_entries[1:]
    
    drugs = []
    
    for i, entry in enumerate(drug_entries):
        if not entry.strip():
            continue
            
        # Extract drug ID
        drug_id_match = re.search(r'"drugbank_id":\s*"DB(\d+)"', raw_data)
        if drug_id_match:
            drug_id = f"DB{drug_id_match.group(1)}"
        else:
            drug_id = f"DB{i:05d}"
        
        # Extract key fields using regex patterns
        drug_info = {
            "id": drug_id,
            "name": extract_field(entry, "name"),
            "type": extract_field(entry, "type"),
            "groups": extract_array_field(entry, "groups"),
            "description": extract_field(entry, "description"),
            "indication": extract_field(entry, "indication"),
            "pharmacology": extract_field(entry, "pharmacology"),
            "mechanism_of_action": extract_field(entry, "mechanism_of_action"),
            "toxicity": extract_field(entry, "toxicity"),
            "metabolism": extract_field(entry, "metabolism"),
            "absorption": extract_field(entry, "absorption"),
            "half_life": extract_field(entry, "half_life"),
            "protein_binding": extract_field(entry, "protein_binding"),
            "route_of_elimination": extract_field(entry, "route_of_elimination"),
            "volume_of_distribution": extract_field(entry, "volume_of_distribution"),
            "clearance": extract_field(entry, "clearance"),
            "dosage": extract_field(entry, "dosage"),
            "food_interactions": extract_field(entry, "food_interactions"),
            "drug_interactions": extract_field(entry, "drug_interactions"),
            "brands": extract_field(entry, "brands"),
            "mixtures": extract_field(entry, "mixtures"),
            "packagers": extract_field(entry, "packagers"),
            "manufacturers": extract_field(entry, "manufacturers"),
            "prices": extract_field(entry, "prices"),
            "categories": extract_field(entry, "categories"),
            "affected_organisms": extract_field(entry, "affected_organisms"),
            "ahfs_codes": extract_field(entry, "ahfs_codes"),
            "pdb_entries": extract_field(entry, "pdb_entries"),
            "fda_label": extract_field(entry, "fda_label"),
            "msds": extract_field(entry, "msds"),
            "patents": extract_field(entry, "patents"),
            "sequences": extract_field(entry, "sequences"),
            "experimental_properties": extract_field(entry, "experimental_properties"),
            "external_identifiers": extract_field(entry, "external_identifiers"),
            "external_links": extract_field(entry, "external_links"),
            "pathways": extract_field(entry, "pathways"),
            "reactions": extract_field(entry, "reactions"),
            "snp_effects": extract_field(entry, "snp_effects"),
            "snp_adverse_drug_reactions": extract_field(entry, "snp_adverse_drug_reactions"),
            "targets": extract_field(entry, "targets"),
            "enzymes": extract_field(entry, "enzymes"),
            "carriers": extract_field(entry, "carriers"),
            "transporters": extract_field(entry, "transporters")
        }
        
        drugs.append(drug_info)
    
    return drugs

def extract_field(text: str, field_name: str) -> str:
    """Extract a specific field value from the text"""
    pattern = rf'"{field_name}":\s*"([^"]*)"'
    match = re.search(pattern, text)
    return match.group(1) if match else ""

def extract_array_field(text: str, field_name: str) -> List[str]:
    """Extract an array field value from the text"""
    pattern = rf'"{field_name}":\s*\[(.*?)\]'
    match = re.search(pattern, text)
    if match:
        # Split by comma and clean up
        items = [item.strip().strip('"') for item in match.group(1).split(',')]
        return [item for item in items if item]
    return []

def create_medicine_database(drugs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert DrugBank data to the format used by the medicine assistant
    """
    medicine_database = {
        "version": "2.0",
        "source": "DrugBank 5.1.11",
        "last_updated": "2025-01-27",
        "total_medicines": len(drugs),
        "medicines": []
    }
    
    for drug in drugs:
        # Extract common names and aliases
        names = [drug["name"]] if drug["name"] else []
        
        # Add brand names if available
        if drug["brands"]:
            brand_names = [brand.strip() for brand in drug["brands"].split(',')]
            names.extend(brand_names)
        
        # Create medicine entry in our format
        medicine_entry = {
            "id": drug["id"],
            "name": drug["name"],
            "generic_name": drug["name"],  # DrugBank name is usually generic
            "brand_names": brand_names if drug["brands"] else [],
            "description": drug["description"],
            "indication": drug["indication"],
            "pharmacology": drug["pharmacology"],
            "mechanism_of_action": drug["mechanism_of_action"],
            "dosage": drug["dosage"],
            "side_effects": drug["toxicity"],
            "metabolism": drug["metabolism"],
            "half_life": drug["half_life"],
            "protein_binding": drug["protein_binding"],
            "route_of_elimination": drug["route_of_elimination"],
            "volume_of_distribution": drug["volume_of_distribution"],
            "clearance": drug["clearance"],
            "food_interactions": drug["food_interactions"],
            "drug_interactions": drug["drug_interactions"],
            "categories": drug["categories"],
            "groups": drug["groups"],
            "manufacturers": drug["manufacturers"],
            "prices": drug["prices"],
            "fda_label": drug["fda_label"],
            "external_links": drug["external_links"],
            "targets": drug["targets"],
            "enzymes": drug["enzymes"],
            "carriers": drug["carriers"],
            "transporters": drug["transporters"]
        }
        
        medicine_database["medicines"].append(medicine_entry)
    
    return medicine_database

def update_nlp_processor_medicines(drugs: List[Dict[str, Any]]) -> List[str]:
    """
    Extract medicine names for the NLP processor
    """
    medicine_names = []
    
    for drug in drugs:
        if drug["name"]:
            medicine_names.append(drug["name"].lower())
        
        # Add brand names
        if drug["brands"]:
            brand_names = [brand.strip().lower() for brand in drug["brands"].split(',')]
            medicine_names.extend(brand_names)
    
    # Remove duplicates and sort
    return sorted(list(set(medicine_names)))

def main():
    """Main processing function"""
    print("DrugBank Database Processing Script")
    print("=" * 50)
    
    # Read the raw DrugBank data
    try:
        with open("../../datasets/raw/drugbank_database.json", 'r') as f:
            raw_data = f.read()
        print("✓ Raw DrugBank data loaded")
    except FileNotFoundError:
        print("❌ DrugBank database file not found!")
        print("Please ensure the file is at: datasets/raw/drugbank_database.json")
        return
    
    # Parse the data
    print("Processing DrugBank data...")
    drugs = parse_drugbank_data(raw_data)
    print(f"✓ Parsed {len(drugs)} drugs")
    
    # Create medicine database
    print("Creating medicine database...")
    medicine_db = create_medicine_database(drugs)
    
    # Save processed database
    output_path = "../../datasets/processed/drugbank_processed.json"
    with open(output_path, 'w') as f:
        json.dump(medicine_db, f, indent=2)
    print(f"✓ Saved processed database to {output_path}")
    
    # Update NLP processor medicines list
    print("Updating NLP processor medicines list...")
    medicine_names = update_nlp_processor_medicines(drugs)
    
    # Save medicine names for NLP processor
    nlp_medicines_path = "../../datasets/processed/nlp_medicines.json"
    with open(nlp_medicines_path, 'w') as f:
        json.dump({
            "version": "2.0",
            "total_medicines": len(medicine_names),
            "medicines": medicine_names
        }, f, indent=2)
    print(f"✓ Saved NLP medicines list to {nlp_medicines_path}")
    
    # Create a summary
    print("\nProcessing Summary:")
    print(f"- Total drugs processed: {len(drugs)}")
    print(f"- Medicine names extracted: {len(medicine_names)}")
    print(f"- Output files created:")
    print(f"  - {output_path}")
    print(f"  - {nlp_medicines_path}")
    
    print("\n✓ DrugBank processing complete!")

if __name__ == "__main__":
    main()
