#!/usr/bin/env python3
"""
Integrate SDF Structure Data with Medicine Database
Combines chemical structures with existing medicine information
"""

import json
from typing import Dict, List, Any

def load_existing_database() -> Dict[str, Any]:
    """Load the existing medicine database"""
    try:
        with open("../../backend/medicines_database.json", 'r') as f:
            data = json.load(f)
            # Handle both list and dict formats
            if isinstance(data, list):
                return {
                    "version": "2.0",
                    "source": "Existing Database",
                    "last_updated": "2025-01-27",
                    "total_medicines": len(data),
                    "medicines": data
                }
            else:
                return data
    except FileNotFoundError:
        print("Existing medicine database not found, creating new one")
        return {
            "version": "2.0",
            "source": "Integrated DrugBank + SDF",
            "last_updated": "2025-01-27",
            "total_medicines": 0,
            "medicines": []
        }

def load_sdf_structures() -> Dict[str, Any]:
    """Load parsed SDF structures"""
    try:
        with open("../../datasets/processed/drugbank_structures.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("SDF structures not found, please run sdf_parser.py first")
        return {"structures": []}

def create_enhanced_medicine_entry(medicine: Dict[str, Any], structure: Dict[str, Any]) -> Dict[str, Any]:
    """Create an enhanced medicine entry with structure data"""
    
    # Basic medicine information
    enhanced_entry = {
        "id": medicine.get("id", structure.get("drugbank_id", "")),
        "name": medicine.get("name", structure.get("common_name", "")),
        "generic_name": medicine.get("generic_name", structure.get("common_name", "")),
        "brand_names": medicine.get("brand_names", []),
        "description": medicine.get("description", ""),
        "indication": medicine.get("indication", ""),
        "pharmacology": medicine.get("pharmacology", ""),
        "mechanism_of_action": medicine.get("mechanism_of_action", ""),
        "dosage": medicine.get("dosage", ""),
        "side_effects": medicine.get("side_effects", ""),
        "metabolism": medicine.get("metabolism", ""),
        "half_life": medicine.get("half_life", ""),
        "protein_binding": medicine.get("protein_binding", ""),
        "route_of_elimination": medicine.get("route_of_elimination", ""),
        "volume_of_distribution": medicine.get("volume_of_distribution", ""),
        "clearance": medicine.get("clearance", ""),
        "food_interactions": medicine.get("food_interactions", ""),
        "drug_interactions": medicine.get("drug_interactions", ""),
        "categories": medicine.get("categories", ""),
        "groups": medicine.get("groups", []),
        "manufacturers": medicine.get("manufacturers", ""),
        "prices": medicine.get("prices", ""),
        "fda_label": medicine.get("fda_label", ""),
        "external_links": medicine.get("external_links", ""),
        "targets": medicine.get("targets", ""),
        "enzymes": medicine.get("enzymes", ""),
        "carriers": medicine.get("carriers", ""),
        "transporters": medicine.get("transporters", ""),
        
        # Enhanced with structure data
        "chemical_structure": {
            "cas_number": structure.get("cas_number", ""),
            "unii": structure.get("unii", ""),
            "synonyms": structure.get("synonyms", []),
            "atom_count": structure.get("atom_count", 0),
            "bond_count": structure.get("bond_count", 0),
            "molecular_formula": calculate_molecular_formula(structure.get("atoms", [])),
            "molecular_weight": calculate_molecular_weight(structure.get("atoms", [])),
            "atoms": structure.get("atoms", []),
            "bonds": structure.get("bonds", [])
        },
        
        # Additional metadata
        "has_structure": True,
        "structure_quality": assess_structure_quality(structure),
        "last_updated": "2025-01-27"
    }
    
    return enhanced_entry

def calculate_molecular_formula(atoms: List[Dict[str, Any]]) -> str:
    """Calculate molecular formula from atoms"""
    element_count = {}
    
    for atom in atoms:
        element = atom.get("element", "")
        if element:
            element_count[element] = element_count.get(element, 0) + 1
    
    # Sort elements by standard order
    element_order = ["C", "H", "N", "O", "P", "S", "F", "Cl", "Br", "I"]
    formula_parts = []
    
    for element in element_order:
        if element in element_count:
            count = element_count[element]
            if count > 1:
                formula_parts.append(f"{element}{count}")
            else:
                formula_parts.append(element)
    
    # Add any remaining elements
    for element, count in element_count.items():
        if element not in element_order:
            if count > 1:
                formula_parts.append(f"{element}{count}")
            else:
                formula_parts.append(element)
    
    return "".join(formula_parts)

def calculate_molecular_weight(atoms: List[Dict[str, Any]]) -> float:
    """Calculate molecular weight from atoms"""
    # Atomic weights (simplified)
    atomic_weights = {
        "C": 12.01, "H": 1.008, "N": 14.01, "O": 16.00, "P": 30.97,
        "S": 32.07, "F": 19.00, "Cl": 35.45, "Br": 79.90, "I": 126.90
    }
    
    total_weight = 0.0
    
    for atom in atoms:
        element = atom.get("element", "")
        if element in atomic_weights:
            total_weight += atomic_weights[element]
    
    return round(total_weight, 2)

def assess_structure_quality(structure: Dict[str, Any]) -> str:
    """Assess the quality of the molecular structure"""
    atom_count = structure.get("atom_count", 0)
    bond_count = structure.get("bond_count", 0)
    
    if atom_count == 0:
        return "no_structure"
    elif atom_count < 10:
        return "simple"
    elif atom_count < 50:
        return "moderate"
    elif atom_count < 100:
        return "complex"
    else:
        return "very_complex"

def integrate_databases():
    """Main integration function"""
    print("Integrating SDF Structure Data with Medicine Database")
    print("=" * 60)
    
    # Load existing data
    print("Loading existing medicine database...")
    existing_db = load_existing_database()
    print(f"✓ Loaded {len(existing_db.get('medicines', []))} existing medicines")
    
    print("Loading SDF structure data...")
    sdf_data = load_sdf_structures()
    structures = sdf_data.get("structures", [])
    print(f"✓ Loaded {len(structures)} molecular structures")
    
    if not structures:
        print("No SDF structures found. Please run sdf_parser.py first.")
        return
    
    # Create structure lookup
    structure_lookup = {}
    for structure in structures:
        drugbank_id = structure.get("drugbank_id", "")
        common_name = structure.get("common_name", "").lower()
        
        if drugbank_id:
            structure_lookup[drugbank_id] = structure
        if common_name:
            structure_lookup[common_name] = structure
    
    # Integrate data
    print("Integrating structure data...")
    enhanced_medicines = []
    
    # Process existing medicines
    for medicine in existing_db.get("medicines", []):
        medicine_id = medicine.get("id", "")
        medicine_name = medicine.get("name", "").lower()
        
        # Find matching structure
        matching_structure = None
        if medicine_id in structure_lookup:
            matching_structure = structure_lookup[medicine_id]
        elif medicine_name in structure_lookup:
            matching_structure = structure_lookup[medicine_name]
        
        if matching_structure:
            enhanced_entry = create_enhanced_medicine_entry(medicine, matching_structure)
            enhanced_medicines.append(enhanced_entry)
            print(f"✓ Enhanced: {medicine.get('name', 'Unknown')}")
        else:
            # Keep original medicine without structure
            medicine["has_structure"] = False
            medicine["chemical_structure"] = None
            enhanced_medicines.append(medicine)
    
    # Add new medicines from SDF that aren't in existing database
    existing_names = {med.get("name", "").lower() for med in existing_db.get("medicines", [])}
    
    for structure in structures:
        common_name = structure.get("common_name", "")
        if common_name.lower() not in existing_names:
            # Create new medicine entry
            new_medicine = {
                "id": structure.get("drugbank_id", ""),
                "name": common_name,
                "generic_name": common_name,
                "brand_names": [],
                "description": "",
                "indication": "",
                "pharmacology": "",
                "mechanism_of_action": "",
                "dosage": "",
                "side_effects": "",
                "metabolism": "",
                "half_life": "",
                "protein_binding": "",
                "route_of_elimination": "",
                "volume_of_distribution": "",
                "clearance": "",
                "food_interactions": "",
                "drug_interactions": "",
                "categories": "",
                "groups": [],
                "manufacturers": "",
                "prices": "",
                "fda_label": "",
                "external_links": "",
                "targets": "",
                "enzymes": "",
                "carriers": "",
                "transporters": "",
                "has_structure": True,
                "last_updated": "2025-01-27"
            }
            
            enhanced_entry = create_enhanced_medicine_entry(new_medicine, structure)
            enhanced_medicines.append(enhanced_entry)
            print(f"✓ Added new: {common_name}")
    
    # Create enhanced database
    enhanced_db = {
        "version": "3.0",
        "source": "Integrated DrugBank + SDF Structures",
        "last_updated": "2025-01-27",
        "total_medicines": len(enhanced_medicines),
        "medicines_with_structures": len([m for m in enhanced_medicines if m.get("has_structure", False)]),
        "medicines": enhanced_medicines
    }
    
    # Save enhanced database
    output_path = "../../datasets/processed/enhanced_medicine_database.json"
    with open(output_path, 'w') as f:
        json.dump(enhanced_db, f, indent=2)
    
    print(f"\n✓ Integration complete!")
    print(f"✓ Total medicines: {len(enhanced_medicines)}")
    print(f"✓ With structures: {enhanced_db['medicines_with_structures']}")
    print(f"✓ Saved to: {output_path}")
    
    # Show sample enhanced medicines
    print(f"\nSample enhanced medicines:")
    for i, medicine in enumerate(enhanced_medicines[:5]):
        print(f"{i+1}. {medicine['name']}")
        if medicine.get("has_structure"):
            structure = medicine.get("chemical_structure", {})
            print(f"   Formula: {structure.get('molecular_formula', 'N/A')}")
            print(f"   Weight: {structure.get('molecular_weight', 'N/A')} g/mol")
            print(f"   Atoms: {structure.get('atom_count', 0)}")
        else:
            print(f"   No structure data available")
        print()

def main():
    """Main function"""
    integrate_databases()

if __name__ == "__main__":
    main()
