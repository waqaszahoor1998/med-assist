#!/usr/bin/env python3
"""
Synthetic Prescription Generator for NLP Testing
Creates realistic prescription text samples for training and testing
"""

import json
import random
import csv
from pathlib import Path

def generate_prescriptions():
    """Generate synthetic prescription dataset"""
    
    medicines = [
        'Paracetamol', 'Ibuprofen', 'Amoxicillin', 'Metformin', 'Lisinopril',
        'Atorvastatin', 'Omeprazole', 'Aspirin', 'Azithromycin', 'Loratadine'
    ]
    
    dosages = {
        'Paracetamol': ['500mg', '650mg', '1000mg'],
        'Ibuprofen': ['200mg', '400mg', '600mg'],
        'Amoxicillin': ['250mg', '500mg', '875mg'],
        'Metformin': ['500mg', '850mg', '1000mg'],
        'Lisinopril': ['5mg', '10mg', '20mg'],
        'Atorvastatin': ['10mg', '20mg', '40mg'],
        'Omeprazole': ['20mg', '40mg'],
        'Aspirin': ['81mg', '325mg'],
        'Azithromycin': ['250mg', '500mg'],
        'Loratadine': ['10mg']
    }
    
    frequencies = [
        'once daily', 'twice daily', 'three times daily',
        'every 6 hours', 'every 8 hours', 'every 12 hours',
        'with meals', 'before meals', 'at bedtime'
    ]
    
    durations = [
        '3 days', '5 days', '7 days', '10 days', '14 days',
        'for 1 week', 'for 2 weeks', 'until finished'
    ]
    
    templates = [
        "Take {medicine} {dose} {frequency}",
        "Take {medicine} {dose} {frequency} for {duration}",
        "{medicine} {dose} {frequency} for {duration}",
        "Take {dose} of {medicine} {frequency}",
        "Use {medicine} {dose} {frequency} for {duration}"
    ]
    
    dataset = []
    
    for i in range(100):
        medicine = random.choice(medicines)
        dose = random.choice(dosages.get(medicine, ['500mg']))
        frequency = random.choice(frequencies)
        duration = random.choice(durations)
        template = random.choice(templates)
        
        prescription_text = template.format(
            medicine=medicine,
            dose=dose,
            frequency=frequency,
            duration=duration
        )
        
        dataset.append({
            'id': i + 1,
            'text': prescription_text,
            'medicine': medicine,
            'dosage': dose,
            'frequency': frequency,
            'duration': duration,
            'type': 'single'
        })
    
    return dataset

def main():
    print("Generating synthetic prescription dataset...")
    
    dataset = generate_prescriptions()
    
    # Save as JSON
    with open('synthetic_prescriptions.json', 'w') as f:
        json.dump(dataset, f, indent=2)
    
    # Save as CSV
    with open('synthetic_prescriptions.csv', 'w', newline='') as f:
        fieldnames = ['id', 'text', 'medicine', 'dosage', 'frequency', 'duration', 'type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)
    
    print(f"✓ Generated {len(dataset)} synthetic prescriptions")
    print("\nSample prescriptions:")
    for i in range(5):
        print(f"{i+1}. {dataset[i]['text']}")
    
    print(f"\n✓ Files saved:")
    print(f"  - synthetic_prescriptions.json")
    print(f"  - synthetic_prescriptions.csv")

if __name__ == "__main__":
    main()
