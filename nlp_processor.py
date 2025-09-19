#!/usr/bin/env python3
"""
Basic NLP Processor for Prescription Analysis - Day 2
"""

import re
import json

def extract_medicine_info(text):
    """Extract medicine information from prescription text"""
    
    # Common medicines (from our database)
    medicines = [
        'paracetamol', 'acetaminophen', 'ibuprofen', 'amoxicillin', 'metformin',
        'lisinopril', 'atorvastatin', 'omeprazole', 'aspirin', 'azithromycin',
        'loratadine', 'amlodipine', 'simvastatin', 'levothyroxine'
    ]
    
    text_lower = text.lower()
    
    # Find medicines
    found_medicines = []
    for medicine in medicines:
        if medicine in text_lower:
            found_medicines.append(medicine.title())
    
    # Extract dosages (number + unit)
    dosage_pattern = r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|tablets?|capsules?)'
    dosages = re.findall(dosage_pattern, text_lower)
    
    # Extract frequency
    frequency = None
    if 'once daily' in text_lower or 'once a day' in text_lower:
        frequency = 'once daily'
    elif 'twice daily' in text_lower or 'twice a day' in text_lower:
        frequency = 'twice daily'
    elif 'three times daily' in text_lower or 'thrice daily' in text_lower:
        frequency = 'three times daily'
    elif 'every 6 hours' in text_lower:
        frequency = 'every 6 hours'
    elif 'every 8 hours' in text_lower:
        frequency = 'every 8 hours'
    
    # Extract duration
    duration = None
    duration_match = re.search(r'for\s+(\d+)\s+(days?|weeks?)', text_lower)
    if duration_match:
        duration = f"{duration_match.group(1)} {duration_match.group(2)}"
    
    return {
        'medicines': found_medicines,
        'dosages': [f"{d[0]}{d[1]}" for d in dosages],
        'frequency': frequency,
        'duration': duration
    }

def test_nlp_processor():
    """Test the NLP processor with sample prescriptions"""
    
    test_cases = [
        "Take Paracetamol 500mg twice daily for 7 days",
        "Ibuprofen 400mg every 6 hours as needed",
        "Take Amoxicillin 250mg three times daily for 10 days",
        "Metformin 500mg twice daily with meals",
        "Take one Lisinopril 10mg tablet once daily"
    ]
    
    print("Testing NLP Processor:")
    print("=" * 50)
    
    successful_extractions = 0
    
    for i, prescription in enumerate(test_cases, 1):
        result = extract_medicine_info(prescription)
        
        print(f"\n{i}. Input: {prescription}")
        print(f"   → Medicines: {result['medicines']}")
        print(f"   → Dosages: {result['dosages']}")
        print(f"   → Frequency: {result['frequency']}")
        print(f"   → Duration: {result['duration']}")
        
        # Check if we extracted at least medicine and dosage
        if result['medicines'] and result['dosages']:
            successful_extractions += 1
            print(f"   ✓ SUCCESS")
        else:
            print(f"   ✗ PARTIAL")
    
    accuracy = (successful_extractions / len(test_cases)) * 100
    print(f"\n" + "=" * 50)
    print(f"Extraction Accuracy: {accuracy:.1f}%")
    print(f"Successful extractions: {successful_extractions}/{len(test_cases)}")
    
    return accuracy

if __name__ == "__main__":
    accuracy = test_nlp_processor()
    
    # Test with synthetic data if available
    try:
        with open("synthetic_prescriptions.json", 'r') as f:
            synthetic_data = json.load(f)
        
        print(f"\n\nTesting with synthetic dataset...")
        
        successful = 0
        total_tested = min(20, len(synthetic_data))  # Test first 20
        
        for item in synthetic_data[:total_tested]:
            result = extract_medicine_info(item['text'])
            if result['medicines'] and result['dosages']:
                successful += 1
        
        synthetic_accuracy = (successful / total_tested) * 100
        print(f"Synthetic dataset accuracy: {synthetic_accuracy:.1f}% ({successful}/{total_tested})")
        
        if synthetic_accuracy >= 70:
            print("✓ NLP processor ready for integration!")
        else:
            print("⚠ NLP processor needs improvement")
            
    except FileNotFoundError:
        print("No synthetic dataset found")
    
    print(f"\n✓ Day 2 NLP preprocessing pipeline complete!")