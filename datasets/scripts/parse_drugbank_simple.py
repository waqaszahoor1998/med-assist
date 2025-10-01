#!/usr/bin/env python3
"""
Simple DrugBank Parser
Handles the single-line DrugBank data format
"""

import json
import re

def parse_drugbank_single_line(data: str) -> list:
    """
    Parse DrugBank data that's in a single line format
    """
    medicines = []
    
    # Split by drug entries - look for the pattern that starts a new drug
    # The data seems to be in format: "drugbank_id": "DB00001", "name": "Lepirudin", ...
    drug_entries = re.split(r'"drugbank_id":\s*"DB\d+"', data)
    
    # Remove empty entries
    drug_entries = [entry.strip() for entry in drug_entries if entry.strip()]
    
    print(f"Found {len(drug_entries)} potential drug entries")
    
    for i, entry in enumerate(drug_entries[:10]):  # Process first 10 for testing
        if not entry:
            continue
            
        # Extract basic fields
        medicine = {
            "id": f"DB{i:05d}",
            "name": "",
            "indication": "",
            "description": "",
            "dosage": "",
            "pharmacology": "",
            "mechanism_of_action": "",
            "toxicity": "",
            "metabolism": "",
            "absorption": "",
            "half_life": "",
            "protein_binding": "",
            "route_of_elimination": "",
            "volume_of_distribution": "",
            "clearance": "",
            "food_interactions": "",
            "drug_interactions": "",
            "brands": "",
            "mixtures": "",
            "packagers": "",
            "manufacturers": "",
            "prices": "",
            "categories": "",
            "affected_organisms": "",
            "ahfs_codes": "",
            "pdb_entries": "",
            "fda_label": "",
            "msds": "",
            "patents": "",
            "sequences": "",
            "experimental_properties": "",
            "external_identifiers": "",
            "external_links": "",
            "pathways": "",
            "reactions": "",
            "snp_effects": "",
            "snp_adverse_drug_reactions": "",
            "targets": "",
            "enzymes": "",
            "carriers": "",
            "transporters": ""
        }
        
        # Extract name
        name_match = re.search(r'"name":\s*"([^"]*)"', entry)
        if name_match:
            medicine["name"] = name_match.group(1)
        
        # Extract indication
        indication_match = re.search(r'"indication":\s*"([^"]*)"', entry)
        if indication_match:
            medicine["indication"] = indication_match.group(1)
        
        # Extract description
        description_match = re.search(r'"description":\s*"([^"]*)"', entry)
        if description_match:
            medicine["description"] = description_match.group(1)
        
        # Extract dosage
        dosage_match = re.search(r'"dosage":\s*"([^"]*)"', entry)
        if dosage_match:
            medicine["dosage"] = dosage_match.group(1)
        
        # Extract pharmacology
        pharmacology_match = re.search(r'"pharmacology":\s*"([^"]*)"', entry)
        if pharmacology_match:
            medicine["pharmacology"] = pharmacology_match.group(1)
        
        # Extract mechanism of action
        mechanism_match = re.search(r'"mechanism_of_action":\s*"([^"]*)"', entry)
        if mechanism_match:
            medicine["mechanism_of_action"] = mechanism_match.group(1)
        
        # Extract toxicity
        toxicity_match = re.search(r'"toxicity":\s*"([^"]*)"', entry)
        if toxicity_match:
            medicine["toxicity"] = toxicity_match.group(1)
        
        # Extract metabolism
        metabolism_match = re.search(r'"metabolism":\s*"([^"]*)"', entry)
        if metabolism_match:
            medicine["metabolism"] = metabolism_match.group(1)
        
        # Extract absorption
        absorption_match = re.search(r'"absorption":\s*"([^"]*)"', entry)
        if absorption_match:
            medicine["absorption"] = absorption_match.group(1)
        
        # Extract half life
        half_life_match = re.search(r'"half_life":\s*"([^"]*)"', entry)
        if half_life_match:
            medicine["half_life"] = half_life_match.group(1)
        
        # Extract protein binding
        protein_binding_match = re.search(r'"protein_binding":\s*"([^"]*)"', entry)
        if protein_binding_match:
            medicine["protein_binding"] = protein_binding_match.group(1)
        
        # Extract route of elimination
        route_elimination_match = re.search(r'"route_of_elimination":\s*"([^"]*)"', entry)
        if route_elimination_match:
            medicine["route_of_elimination"] = route_elimination_match.group(1)
        
        # Extract volume of distribution
        volume_distribution_match = re.search(r'"volume_of_distribution":\s*"([^"]*)"', entry)
        if volume_distribution_match:
            medicine["volume_of_distribution"] = volume_distribution_match.group(1)
        
        # Extract clearance
        clearance_match = re.search(r'"clearance":\s*"([^"]*)"', entry)
        if clearance_match:
            medicine["clearance"] = clearance_match.group(1)
        
        # Extract food interactions
        food_interactions_match = re.search(r'"food_interactions":\s*"([^"]*)"', entry)
        if food_interactions_match:
            medicine["food_interactions"] = food_interactions_match.group(1)
        
        # Extract drug interactions
        drug_interactions_match = re.search(r'"drug_interactions":\s*"([^"]*)"', entry)
        if drug_interactions_match:
            medicine["drug_interactions"] = drug_interactions_match.group(1)
        
        # Extract brands
        brands_match = re.search(r'"brands":\s*"([^"]*)"', entry)
        if brands_match:
            medicine["brands"] = brands_match.group(1)
        
        # Extract mixtures
        mixtures_match = re.search(r'"mixtures":\s*"([^"]*)"', entry)
        if mixtures_match:
            medicine["mixtures"] = mixtures_match.group(1)
        
        # Extract packagers
        packagers_match = re.search(r'"packagers":\s*"([^"]*)"', entry)
        if packagers_match:
            medicine["packagers"] = packagers_match.group(1)
        
        # Extract manufacturers
        manufacturers_match = re.search(r'"manufacturers":\s*"([^"]*)"', entry)
        if manufacturers_match:
            medicine["manufacturers"] = manufacturers_match.group(1)
        
        # Extract prices
        prices_match = re.search(r'"prices":\s*"([^"]*)"', entry)
        if prices_match:
            medicine["prices"] = prices_match.group(1)
        
        # Extract categories
        categories_match = re.search(r'"categories":\s*"([^"]*)"', entry)
        if categories_match:
            medicine["categories"] = categories_match.group(1)
        
        # Extract affected organisms
        affected_organisms_match = re.search(r'"affected_organisms":\s*"([^"]*)"', entry)
        if affected_organisms_match:
            medicine["affected_organisms"] = affected_organisms_match.group(1)
        
        # Extract AHFS codes
        ahfs_codes_match = re.search(r'"ahfs_codes":\s*"([^"]*)"', entry)
        if ahfs_codes_match:
            medicine["ahfs_codes"] = ahfs_codes_match.group(1)
        
        # Extract PDB entries
        pdb_entries_match = re.search(r'"pdb_entries":\s*"([^"]*)"', entry)
        if pdb_entries_match:
            medicine["pdb_entries"] = pdb_entries_match.group(1)
        
        # Extract FDA label
        fda_label_match = re.search(r'"fda_label":\s*"([^"]*)"', entry)
        if fda_label_match:
            medicine["fda_label"] = fda_label_match.group(1)
        
        # Extract MSDS
        msds_match = re.search(r'"msds":\s*"([^"]*)"', entry)
        if msds_match:
            medicine["msds"] = msds_match.group(1)
        
        # Extract patents
        patents_match = re.search(r'"patents":\s*"([^"]*)"', entry)
        if patents_match:
            medicine["patents"] = patents_match.group(1)
        
        # Extract sequences
        sequences_match = re.search(r'"sequences":\s*"([^"]*)"', entry)
        if sequences_match:
            medicine["sequences"] = sequences_match.group(1)
        
        # Extract experimental properties
        experimental_properties_match = re.search(r'"experimental_properties":\s*"([^"]*)"', entry)
        if experimental_properties_match:
            medicine["experimental_properties"] = experimental_properties_match.group(1)
        
        # Extract external identifiers
        external_identifiers_match = re.search(r'"external_identifiers":\s*"([^"]*)"', entry)
        if external_identifiers_match:
            medicine["external_identifiers"] = external_identifiers_match.group(1)
        
        # Extract external links
        external_links_match = re.search(r'"external_links":\s*"([^"]*)"', entry)
        if external_links_match:
            medicine["external_links"] = external_links_match.group(1)
        
        # Extract pathways
        pathways_match = re.search(r'"pathways":\s*"([^"]*)"', entry)
        if pathways_match:
            medicine["pathways"] = pathways_match.group(1)
        
        # Extract reactions
        reactions_match = re.search(r'"reactions":\s*"([^"]*)"', entry)
        if reactions_match:
            medicine["reactions"] = reactions_match.group(1)
        
        # Extract SNP effects
        snp_effects_match = re.search(r'"snp_effects":\s*"([^"]*)"', entry)
        if snp_effects_match:
            medicine["snp_effects"] = snp_effects_match.group(1)
        
        # Extract SNP adverse drug reactions
        snp_adverse_drug_reactions_match = re.search(r'"snp_adverse_drug_reactions":\s*"([^"]*)"', entry)
        if snp_adverse_drug_reactions_match:
            medicine["snp_adverse_drug_reactions"] = snp_adverse_drug_reactions_match.group(1)
        
        # Extract targets
        targets_match = re.search(r'"targets":\s*"([^"]*)"', entry)
        if targets_match:
            medicine["targets"] = targets_match.group(1)
        
        # Extract enzymes
        enzymes_match = re.search(r'"enzymes":\s*"([^"]*)"', entry)
        if enzymes_match:
            medicine["enzymes"] = enzymes_match.group(1)
        
        # Extract carriers
        carriers_match = re.search(r'"carriers":\s*"([^"]*)"', entry)
        if carriers_match:
            medicine["carriers"] = carriers_match.group(1)
        
        # Extract transporters
        transporters_match = re.search(r'"transporters":\s*"([^"]*)"', entry)
        if transporters_match:
            medicine["transporters"] = transporters_match.group(1)
        
        medicines.append(medicine)
    
    return medicines

def main():
    print("DrugBank Single-Line Parser")
    print("=" * 40)
    
    # Read the raw data
    try:
        with open("../../datasets/raw/drugbank_database.json", 'r') as f:
            raw_data = f.read()
        print("✓ DrugBank data loaded")
    except FileNotFoundError:
        print("❌ DrugBank database file not found!")
        return
    
    # Parse the data
    print("Parsing DrugBank data...")
    medicines = parse_drugbank_single_line(raw_data)
    print(f"✓ Parsed {len(medicines)} medicines")
    
    # Save the parsed data
    output_path = "../../datasets/processed/drugbank_parsed.json"
    with open(output_path, 'w') as f:
        json.dump({
            "version": "1.0",
            "source": "DrugBank 5.1.11",
            "total_medicines": len(medicines),
            "medicines": medicines
        }, f, indent=2)
    
    print(f"✓ Saved parsed data to {output_path}")
    
    # Show sample medicines
    print("\nSample medicines parsed:")
    for i, med in enumerate(medicines[:5]):
        print(f"{i+1}. {med['name']}")
        if med['indication']:
            print(f"   Indication: {med['indication'][:100]}...")
        if med['description']:
            print(f"   Description: {med['description'][:100]}...")
        print()

if __name__ == "__main__":
    main()
