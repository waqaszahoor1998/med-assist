#!/usr/bin/env python3
"""
Test Django BioBERT integration
"""

import os
import sys
import django
import requests
import json

# Add the backend directory to Python path
sys.path.append('/Users/m.w.zahoor/Desktop/med assist/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_assistant.settings')
django.setup()

def test_biobert_integration():
    """Test the Django API with BioBERT integration"""
    print("=" * 60)
    print("🧬 Testing Django BioBERT Integration")
    print("=" * 60)
    
    # Test data
    test_prescriptions = [
        "Take Metformin 500mg twice daily with meals for diabetes",
        "Aspirin 81mg once daily for heart health",
        "Amoxicillin 250mg three times daily for 7 days for infection"
    ]
    
    base_url = "http://localhost:8000/api"
    
    print("📡 Testing API endpoints...")
    
    # Test 1: Ping endpoint
    try:
        response = requests.get(f"{base_url}/ping/", timeout=10)
        if response.status_code == 200:
            print("✅ Ping endpoint working")
        else:
            print(f"❌ Ping endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure Django server is running: python manage.py runserver")
        return False
    
    print(f"\n💊 Testing prescription analysis with {len(test_prescriptions)} samples:")
    print("=" * 60)
    
    success_count = 0
    
    for i, prescription in enumerate(test_prescriptions, 1):
        print(f"\n🔍 Test {i}: {prescription}")
        
        try:
            # Test prescription analysis
            payload = {"text": prescription}
            response = requests.post(
                f"{base_url}/prescription/analyze/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Status: {data.get('status')}")
                print(f"   🧠 Processing Method: {data.get('processing_method', 'Unknown')}")
                print(f"   🎯 Confidence Score: {data.get('confidence_score', 'N/A')}")
                print(f"   📊 NLP Version: {data.get('nlp_version', 'Unknown')}")
                
                medicines = data.get('extracted_medicines', [])
                if medicines:
                    print(f"   💊 Found {len(medicines)} medicine(s):")
                    for j, med in enumerate(medicines, 1):
                        confidence = med.get('confidence', 'N/A')
                        source = med.get('source', 'Unknown')
                        print(f"      {j}. {med.get('name', 'Unknown')}")
                        print(f"         Dosage: {med.get('dosage', 'N/A')}")
                        print(f"         Frequency: {med.get('frequency', 'N/A')}")
                        print(f"         Confidence: {confidence}")
                        print(f"         Source: {source}")
                    success_count += 1
                else:
                    print("   ❌ No medicines found")
                
                # Show AI model info if available
                ai_info = data.get('ai_model_info')
                if ai_info:
                    print(f"   🤖 AI Model: {ai_info.get('model_parameters', 0):,} parameters")
                    print(f"   📏 Model Size: {ai_info.get('model_size_mb', 0)} MB")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"✅ Successful tests: {success_count}/{len(test_prescriptions)}")
    success_rate = (success_count / len(test_prescriptions)) * 100
    print(f"🎯 Success rate: {success_rate:.1f}%")
    
    if success_count == len(test_prescriptions):
        print("🎉 Django BioBERT integration is working perfectly!")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = test_biobert_integration()
    sys.exit(0 if success else 1)
