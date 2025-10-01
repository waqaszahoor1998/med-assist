#!/usr/bin/env python3
"""
Extract and process medical knowledge from the wiki medical terms dataset.
"""

import json
import re
from collections import defaultdict

def extract_medical_knowledge():
    """Extract medical knowledge from wiki dataset and organize it"""
    
    print("EXTRACTING MEDICAL KNOWLEDGE FROM WIKI DATASET")
    print("=" * 60)
    
    # Load the wiki medical terms dataset
    wiki_file = "../datasets/wiki_medical_terms_llam2.jsonl"
    
    medical_terms = []
    medicine_related = []
    condition_related = []
    
    print("Processing wiki medical terms dataset...")
    
    with open(wiki_file, 'r') as f:
        for i, line in enumerate(f):
            if i % 1000 == 0:
                print(f"Processed {i:,} entries...")
            
            try:
                entry = json.loads(line.strip())
                text = entry.get('text', '')
                
                # Extract medical term and explanation
                if '[INST]' in text and '[/INST]' in text:
                    # Extract instruction
                    inst_start = text.find('[INST]') + 6
                    inst_end = text.find('[/INST]')
                    instruction = text[inst_start:inst_end].strip()
                    
                    # Extract medical term
                    if 'What is' in instruction:
                        term_start = instruction.find('What is') + 7
                        term_end = instruction.find(' and explain') if ' and explain' in instruction else len(instruction)
                        medical_term = instruction[term_start:term_end].strip().replace('?', '').strip()
                    else:
                        medical_term = 'Unknown'
                    
                    # Extract explanation
                    response_start = text.find('[/INST]') + 7
                    response_end = text.find('</s>')
                    explanation = text[response_start:response_end].strip()
                    
                    # Clean and process the medical term
                    medical_term = medical_term.lower().strip()
                    
                    # Skip if term is too generic or short
                    if len(medical_term) < 3 or medical_term in ['what', 'unknown', 'is']:
                        continue
                    
                    # Create structured entry
                    entry_data = {
                        'term': medical_term,
                        'explanation': explanation,
                        'term_length': len(explanation),
                        'is_medicine': is_medicine_related(medical_term, explanation),
                        'is_condition': is_condition_related(medical_term, explanation),
                        'keywords': extract_keywords(medical_term, explanation)
                    }
                    
                    medical_terms.append(entry_data)
                    
                    # Categorize
                    if entry_data['is_medicine']:
                        medicine_related.append(entry_data)
                    
                    if entry_data['is_condition']:
                        condition_related.append(entry_data)
                        
            except Exception as e:
                continue
    
    print(f"\nExtraction complete!")
    print(f"Total medical terms: {len(medical_terms):,}")
    print(f"Medicine-related: {len(medicine_related):,}")
    print(f"Condition-related: {len(condition_related):,}")
    
    # Save extracted data
    output_data = {
        'version': '1.0',
        'source': 'Wiki Medical Terms Dataset (LLaMA2)',
        'extraction_date': '2025-01-27',
        'total_terms': len(medical_terms),
        'medicine_related': len(medicine_related),
        'condition_related': len(condition_related),
        'all_terms': medical_terms,
        'medicine_terms': medicine_related,
        'condition_terms': condition_related
    }
    
    # Save comprehensive medical knowledge database
    output_file = "../datasets/processed/comprehensive_medical_knowledge.json"
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nSaved comprehensive medical knowledge to: {output_file}")
    
    # Create medicine-specific knowledge database
    medicine_knowledge = create_medicine_knowledge_db(medicine_related)
    medicine_file = "../datasets/processed/medicine_knowledge_database.json"
    with open(medicine_file, 'w') as f:
        json.dump(medicine_knowledge, f, indent=2)
    
    print(f"Saved medicine knowledge to: {medicine_file}")
    
    # Show sample terms
    print(f"\nSample Medicine-Related Terms:")
    for i, term in enumerate(medicine_related[:5]):
        print(f"  {i+1}. {term['term']} ({term['term_length']:,} chars)")
    
    print(f"\nSample Condition-Related Terms:")
    for i, term in enumerate(condition_related[:5]):
        print(f"  {i+1}. {term['term']} ({term['term_length']:,} chars)")
    
    return output_file, medicine_file

def is_medicine_related(term, explanation):
    """Check if term is medicine-related"""
    medicine_indicators = [
        'poisoning', 'overdose', 'drug', 'medication', 'medicine', 'pill', 'tablet',
        'capsule', 'injection', 'syrup', 'cream', 'ointment', 'dosage', 'dose',
        'pharmacology', 'pharmaceutical', 'therapeutic', 'treatment', 'side effect',
        'adverse effect', 'contraindication', 'interaction', 'metabolism', 'absorption',
        'elimination', 'pharmacokinetics', 'pharmacodynamics', 'antidote', 'toxicity'
    ]
    
    term_lower = term.lower()
    explanation_lower = explanation.lower()
    
    # Check term name
    for indicator in medicine_indicators:
        if indicator in term_lower:
            return True
    
    # Check explanation content
    medicine_count = sum(1 for indicator in medicine_indicators if indicator in explanation_lower)
    
    # If multiple medicine indicators in explanation, likely medicine-related
    return medicine_count >= 3

def is_condition_related(term, explanation):
    """Check if term is medical condition-related"""
    condition_indicators = [
        'syndrome', 'disease', 'disorder', 'condition', 'illness', 'symptom',
        'diagnosis', 'prognosis', 'pathophysiology', 'etiology', 'epidemiology',
        'treatment', 'therapy', 'cure', 'remission', 'progression', 'complication',
        'signs', 'clinical', 'medical', 'health', 'patient', 'hospital'
    ]
    
    term_lower = term.lower()
    explanation_lower = explanation.lower()
    
    # Check term name
    for indicator in condition_indicators:
        if indicator in term_lower:
            return True
    
    # Check explanation content
    condition_count = sum(1 for indicator in condition_indicators if indicator in explanation_lower)
    
    # If multiple condition indicators in explanation, likely condition-related
    return condition_count >= 3

def extract_keywords(term, explanation):
    """Extract relevant keywords from term and explanation"""
    keywords = set()
    
    # Add the term itself
    keywords.add(term)
    
    # Extract words from explanation (simple keyword extraction)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', explanation.lower())
    
    # Add common medical terms
    medical_keywords = [
        'treatment', 'symptoms', 'diagnosis', 'causes', 'effects', 'medicine',
        'drug', 'therapy', 'patient', 'medical', 'clinical', 'disease',
        'condition', 'syndrome', 'disorder', 'health', 'pharmacy'
    ]
    
    for word in words:
        if word in medical_keywords or len(word) > 6:
            keywords.add(word)
    
    return list(keywords)[:20]  # Limit to 20 keywords

def create_medicine_knowledge_db(medicine_terms):
    """Create a structured medicine knowledge database"""
    
    medicine_db = {
        'version': '1.0',
        'source': 'Wiki Medical Terms - Medicine Extracts',
        'created': '2025-01-27',
        'total_medicines': len(medicine_terms),
        'medicines': {}
    }
    
    # Group by medicine names and create structured entries
    for term_data in medicine_terms:
        term = term_data['term']
        explanation = term_data['explanation']
        
        # Create medicine entry
        medicine_entry = {
            'name': term,
            'detailed_explanation': explanation,
            'explanation_length': len(explanation),
            'keywords': term_data['keywords'],
            'source': 'Wiki Medical Knowledge',
            'last_updated': '2025-01-27'
        }
        
        # Add to database
        medicine_db['medicines'][term] = medicine_entry
    
    return medicine_db

if __name__ == "__main__":
    extract_medical_knowledge()
