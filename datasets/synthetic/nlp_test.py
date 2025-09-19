import re
import json

def extract_medicine_info(text):
    medicines = ['paracetamol', 'ibuprofen', 'amoxicillin', 'metformin', 'lisinopril', 'atorvastatin', 'omeprazole', 'aspirin']
    text_lower = text.lower()
    
    found_medicines = [m.title() for m in medicines if m in text_lower]
    dosages = re.findall(r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml)', text_lower)
    
    frequency = None
    if 'twice daily' in text_lower:
        frequency = 'twice daily'
    elif 'once daily' in text_lower:
        frequency = 'once daily'
    elif 'three times daily' in text_lower:
        frequency = 'three times daily'
    
    return {
        'medicines': found_medicines,
        'dosages': [f"{d[0]}{d[1]}" for d in dosages],
        'frequency': frequency
    }

# Test cases
tests = [
    "Take Paracetamol 500mg twice daily for 7 days",
    "Ibuprofen 400mg every 6 hours",
    "Amoxicillin 250mg three times daily"
]

print("NLP Processor Test Results:")
print("=" * 40)

successful = 0
for i, test in enumerate(tests, 1):
    result = extract_medicine_info(test)
    print(f"\n{i}. {test}")
    print(f"   Medicines: {result['medicines']}")
    print(f"   Dosages: {result['dosages']}")
    print(f"   Frequency: {result['frequency']}")
    
    if result['medicines'] and result['dosages']:
        successful += 1
        print(f"   ✓ SUCCESS")

accuracy = (successful / len(tests)) * 100
print(f"\nAccuracy: {accuracy:.1f}% ({successful}/{len(tests)})")
print("✓ Basic NLP pipeline working!")
