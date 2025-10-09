#!/usr/bin/env python3
"""
Synthetic Prescription Generator for NLP Testing
Creates realistic prescription text samples for training and testing
"""

import json
import random
from pathlib import Path

class PrescriptionGenerator:
    def __init__(self):
        self.medicines = [
            'Paracetamol', 'Ibuprofen', 'Amoxicillin', 'Metformin', 'Lisinopril',
            'Atorvastatin', 'Omeprazole', 'Aspirin', 'Azithromycin', 'Loratadine',
            'Amlodipine', 'Simvastatin', 'Levothyroxine', 'Clopidogrel', 'Warfarin'
        ]
        
        self.dosages = {
            'Paracetamol': ['500mg', '650mg', '1000mg'],
            'Ibuprofen': ['200mg', '400mg', '600mg', '800mg'],
            'Amoxicillin': ['250mg', '500mg', '875mg'],
            'Metformin': ['500mg', '850mg', '1000mg'],
            'Lisinopril': ['5mg', '10mg', '20mg', '40mg'],
            'Atorvastatin': ['10mg', '20mg', '40mg', '80mg'],
            'Omeprazole': ['20mg', '40mg'],
            'Aspirin': ['81mg', '325mg', '500mg'],
            'Azithromycin': ['250mg', '500mg'],
            'Loratadine': ['10mg'],
            'Amlodipine': ['2.5mg', '5mg', '10mg'],
            'Simvastatin': ['10mg', '20mg', '40mg', '80mg'],
            'Levothyroxine': ['25mcg', '50mcg', '75mcg', '100mcg'],
            'Clopidogrel': ['75mg'],
            'Warfarin': ['1mg', '2mg', '5mg', '10mg']
        }
        
        self.frequencies = [
            'once daily', 'twice daily', 'three times daily', 'four times daily',
            'every 4 hours', 'every 6 hours', 'every 8 hours', 'every 12 hours',
            'once a day', 'twice a day', 'three times a day',
            'morning and evening', 'with meals', 'before meals', 'after meals',
            'at bedtime', 'as needed', 'when required'
        ]
        
        self.durations = [
            '3 days', '5 days', '7 days', '10 days', '14 days', '21 days', '30 days',
            'for 1 week', 'for 2 weeks', 'for 1 month', 'until finished',
            'for 3 days', 'for 5 days', 'for 7 days', 'continue as directed'
        ]
        
        self.templates = [
            "Take {medicine} {dose} {frequency}",
            "Take {medicine} {dose} {frequency} for {duration}",
            "{medicine} {dose} {frequency}",
            "{medicine} {dose} - {frequency} for {duration}",
            "Take {dose} of {medicine} {frequency}",
            "Use {medicine} {dose} {frequency} for {duration}",
            "Take one {medicine} {dose} tablet {frequency}",
            "{medicine} tablets {dose} {frequency} for {duration}",
            "Take {medicine} {dose} {frequency} with food",
            "Take {medicine} {dose} {frequency} on empty stomach"
        ]

    def generate_single_prescription(self):
        """Generate a single prescription text"""
        medicine = random.choice(self.medicines)
        dose = random.choice(self.dosages.get(medicine, ['500mg']))
        frequency = random.choice(self.frequencies)
        duration = random.choice(self.durations)
        template = random.choice(self.templates)
        
        prescription = template.format(
            medicine=medicine,
            dose=dose,
            frequency=frequency,
            duration=duration
        )
        
        return {
            'text': prescription,
            'medicine': medicine,
            'dosage': dose,
            'frequency': frequency,
            'duration': duration if '{duration}' in template else None
        }

    def generate_multi_medicine_prescription(self):
        """Generate prescription with multiple medicines"""
        num_medicines = random.randint(2, 3)
        prescriptions = []
        medicines_used = []
        
        selected_medicines = random.sample(self.medicines, num_medicines)
        
        for medicine in selected_medicines:
            dose = random.choice(self.dosages.get(medicine, ['500mg']))
            frequency = random.choice(self.frequencies)
            duration = random.choice(self.durations)
            
            prescriptions.append(f"Take {medicine} {dose} {frequency} for {duration}")
            medicines_used.append({
                'medicine': medicine,
                'dosage': dose,
                'frequency': frequency,
                'duration': duration
            })
        
        combined_text = ". ".join(prescriptions) + "."
        
        return {
            'text': combined_text,
            'medicines': medicines_used,
            'type': 'multi_medicine'
        }

    def generate_dataset(self, num_prescriptions=100):
        """Generate a complete dataset of synthetic prescriptions"""
        dataset = []
        
        # Generate different types of prescriptions
        for i in range(num_prescriptions):
            if i % 5 == 0:  # 20% multi-medicine prescriptions
                prescription = self.generate_multi_medicine_prescription()
            else:  # 80% single medicine prescriptions
                prescription = self.generate_single_prescription()
            
            prescription['id'] = i + 1
            dataset.append(prescription)
        
        return dataset

    def save_dataset(self, dataset, filename="synthetic_prescriptions"):
        """Save dataset to files"""
        # Save as JSON
        json_file = Path(f"{filename}.json")
        with open(json_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        # Save as CSV for easy viewing
        csv_file = Path(f"{filename}.csv")
        import csv
        with open(csv_file, 'w', newline='') as f:
            if dataset:
                fieldnames = ['id', 'text', 'type']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in dataset:
                    row = {
                        'id': item.get('id', ''),
                        'text': item.get('text', ''),
                        'type': item.get('type', 'single')
                    }
                    writer.writerow(row)
        
        print(f"✓ Dataset saved to: {json_file}")
        print(f"✓ CSV saved to: {csv_file}")

def main():
    generator = PrescriptionGenerator()
    
    print("Generating synthetic prescription dataset...")
    dataset = generator.generate_dataset(100)
    
    print(f"Generated {len(dataset)} prescriptions")
    
    # Show some examples
    print("\nSample prescriptions:")
    for i, prescription in enumerate(dataset[:5]):
        print(f"{i+1}. {prescription['text']}")
    
    # Save dataset
    generator.save_dataset(dataset)
    
    print(f"\n✓ Synthetic prescription dataset created successfully!")

if __name__ == "__main__":
    main()
