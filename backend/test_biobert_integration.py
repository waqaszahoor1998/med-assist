#!/usr/bin/env python3
"""
Test BioBERT integration with Django backend
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('/Users/m.w.zahoor/Desktop/med assist/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_assistant.settings')
django.setup()

from api.biobert_processor import BioBERTProcessor

def test_biobert_processor():
    """Test the BioBERT processor with sample prescriptions"""
    print("=" * 60)
    print("🧬 Testing BioBERT Processor Integration")
    print("=" * 60)
    
    try:
        # Initialize processor
        print("📥 Initializing BioBERT processor...")
        processor = BioBERTProcessor()
        print("✅ Processor initialized successfully!")
        
        # Show model info
        model_info = processor.get_model_info()
        print(f"\n📊 Model Information:")
        print(f"   Path: {model_info['model_path']}")
        print(f"   Vocabulary: {model_info['vocabulary_size']:,}")
        print(f"   Parameters: {model_info['model_parameters']:,}")
        print(f"   Size: {model_info['model_size_mb']} MB")
        
        # Test prescriptions - expanded with more edge cases
        test_prescriptions = [
            "Take Metformin 500mg twice daily with meals for diabetes",
            "Aspirin 81mg once daily for heart health",
            "Amoxicillin 250mg three times daily for 7 days for infection",
            "Ibuprofen 200mg as needed for pain relief",
            "Take Lisinopril 10mg once daily in the morning for blood pressure",
            # Additional test cases for Day 7 improvements
            "Prescribe: Omeprazole 20mg q.d. for acid reflux",
            "Patient needs: Warfarin 5mg b.i.d. for blood thinning",
            "Rx: Prednisone 10mg t.i.d. for inflammation",
            "Medication: Atorvastatin 40mg once daily at bedtime",
            "Give: Ciprofloxacin 500mg b.i.d. for UTI"
        ]
        
        print(f"\n💊 Testing {len(test_prescriptions)} sample prescriptions:")
        print("=" * 60)
        
        # Track test statistics
        total_tests = len(test_prescriptions)
        successful_extractions = 0
        total_medicines_found = 0
        confidence_scores = []
        
        for i, prescription in enumerate(test_prescriptions, 1):
            print(f"\n🔍 Test {i}: {prescription}")
            
            # Extract medicines
            medicines = processor.extract_medicines(prescription)
            
            if medicines:
                successful_extractions += 1
                total_medicines_found += len(medicines)
                print(f"   ✅ Found {len(medicines)} medicine(s):")
                for j, med in enumerate(medicines, 1):
                    print(f"      {j}. {med['name']}")
                    print(f"         Dosage: {med['dosage']}")
                    print(f"         Frequency: {med['frequency']}")
                    print(f"         Confidence: {med['confidence']}")
                    confidence_scores.append(med['confidence'])
            else:
                print("   ❌ No medicines found")
        
        # Calculate and display statistics
        success_rate = (successful_extractions / total_tests) * 100
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        print("\n" + "=" * 60)
        print("📊 TEST STATISTICS SUMMARY")
        print("=" * 60)
        print(f"✅ Success Rate: {success_rate:.1f}% ({successful_extractions}/{total_tests})")
        print(f"💊 Total Medicines Found: {total_medicines_found}")
        print(f"🎯 Average Confidence: {avg_confidence:.2f}")
        print(f"📈 High Confidence (>0.7): {sum(1 for c in confidence_scores if c > 0.7)}")
        print("=" * 60)
        print("🎉 BioBERT Processor Integration Test Complete!")
        print("Ready to replace rule-based system in Django views")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_biobert_processor()
    sys.exit(0 if success else 1)
