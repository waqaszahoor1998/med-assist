#!/usr/bin/env python3
"""
Test complete system integration - Django + BioBERT + Frontend API
"""

import os
import sys
import django
import requests
import json
import time

# Add the backend directory to Python path
sys.path.append('/Users/m.w.zahoor/Desktop/med assist/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_assistant.settings')
django.setup()

def test_complete_system_integration():
    """Test the complete system integration"""
    print("=" * 70)
    print("COMPLETE SYSTEM INTEGRATION TEST")
    print("=" * 70)
    
    base_url = "http://localhost:8000/api"
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Simple Prescription",
            "prescription": "Take Metformin 500mg twice daily with meals for diabetes",
            "expected_medicines": ["Metformin"],
            "expected_dosage": "500mg",
            "expected_frequency": "twice daily"
        },
        {
            "name": "Complex Prescription with Medical Abbreviations",
            "prescription": "Prescribe: Omeprazole 20mg q.d. for acid reflux",
            "expected_medicines": ["Omeprazole"],
            "expected_dosage": "20mg",
            "expected_frequency": "once daily"
        },
        {
            "name": "Multiple Medicines",
            "prescription": "Take Aspirin 81mg once daily for heart health and Ibuprofen 200mg as needed for pain",
            "expected_medicines": ["Aspirin", "Ibuprofen"],
            "expected_dosage": ["81mg", "200mg"],
            "expected_frequency": ["once daily", "as needed"]
        },
        {
            "name": "Antibiotic with Duration",
            "prescription": "Amoxicillin 250mg three times daily for 7 days for infection",
            "expected_medicines": ["Amoxicillin"],
            "expected_dosage": "250mg",
            "expected_frequency": "three times daily"
        }
    ]
    
    print("Testing API connectivity...")
    try:
        response = requests.get(f"{base_url}/ping/", timeout=10)
        if response.status_code == 200:
            print("SUCCESS: API is accessible")
        else:
            print(f"FAILED: API ping returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"FAILED: Cannot connect to API - {e}")
        print("Make sure Django server is running on port 8000")
        return False
    
    print(f"\nTesting {len(test_scenarios)} prescription scenarios:")
    print("=" * 70)
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\nTest {i}: {scenario['name']}")
        print(f"Prescription: {scenario['prescription']}")
        
        try:
            payload = {"text": scenario['prescription']}
            response = requests.post(
                f"{base_url}/prescription/analyze/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                print(f"Status: {data.get('status')}")
                print(f"Processing Method: {data.get('processing_method', 'Unknown')}")
                print(f"Confidence Score: {data.get('confidence_score', 'N/A')}")
                print(f"NLP Version: {data.get('nlp_version', 'Unknown')}")
                
                # Check AI model info
                ai_info = data.get('ai_model_info')
                if ai_info:
                    print(f"AI Model: {ai_info.get('model_parameters', 0):,} parameters")
                    print(f"Model Size: {ai_info.get('model_size_mb', 0)} MB")
                    print(f"Model Status: {ai_info.get('status', 'Unknown')}")
                
                medicines = data.get('extracted_medicines', [])
                print(f"Extracted Medicines: {len(medicines)}")
                
                # Validate results
                test_result = {
                    "scenario": scenario['name'],
                    "success": True,
                    "medicines_found": len(medicines),
                    "processing_method": data.get('processing_method'),
                    "confidence": data.get('confidence_score'),
                    "ai_powered": 'BioBERT' in data.get('processing_method', '')
                }
                
                for j, med in enumerate(medicines):
                    print(f"  {j+1}. {med.get('name', 'Unknown')}")
                    print(f"     Dosage: {med.get('dosage', 'N/A')}")
                    print(f"     Frequency: {med.get('frequency', 'N/A')}")
                    print(f"     Confidence: {med.get('confidence', 'N/A')}")
                    print(f"     Source: {med.get('source', 'Unknown')}")
                
                # Check if expected medicines were found
                found_medicines = [med.get('name', '').lower() for med in medicines]
                expected_medicines = [name.lower() for name in scenario['expected_medicines']]
                
                medicine_accuracy = 0
                for expected in expected_medicines:
                    if any(expected in found for found in found_medicines):
                        medicine_accuracy += 1
                
                medicine_accuracy = medicine_accuracy / len(expected_medicines) * 100
                test_result["medicine_accuracy"] = medicine_accuracy
                print(f"Medicine Accuracy: {medicine_accuracy:.1f}%")
                
                results.append(test_result)
                print("RESULT: PASSED")
                
            else:
                print(f"FAILED: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Error: {response.text}")
                
                results.append({
                    "scenario": scenario['name'],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                print("RESULT: FAILED")
                
        except requests.exceptions.RequestException as e:
            print(f"FAILED: Request error - {e}")
            results.append({
                "scenario": scenario['name'],
                "success": False,
                "error": str(e)
            })
            print("RESULT: FAILED")
        except Exception as e:
            print(f"FAILED: Unexpected error - {e}")
            results.append({
                "scenario": scenario['name'],
                "success": False,
                "error": str(e)
            })
            print("RESULT: FAILED")
    
    # Calculate overall results
    print("\n" + "=" * 70)
    print("SYSTEM INTEGRATION TEST RESULTS")
    print("=" * 70)
    
    successful_tests = [r for r in results if r.get('success', False)]
    total_tests = len(results)
    success_rate = len(successful_tests) / total_tests * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {total_tests - len(successful_tests)}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if successful_tests:
        ai_powered_tests = [r for r in successful_tests if r.get('ai_powered', False)]
        avg_confidence = sum(r.get('confidence', 0) for r in successful_tests) / len(successful_tests)
        avg_medicine_accuracy = sum(r.get('medicine_accuracy', 0) for r in successful_tests) / len(successful_tests)
        
        print(f"AI-Powered Tests: {len(ai_powered_tests)}/{len(successful_tests)}")
        print(f"Average Confidence: {avg_confidence:.2f}")
        print(f"Average Medicine Accuracy: {avg_medicine_accuracy:.1f}%")
    
    print("\nDetailed Results:")
    for result in results:
        status = "PASS" if result.get('success', False) else "FAIL"
        scenario = result.get('scenario', 'Unknown')
        print(f"  {status}: {scenario}")
        if not result.get('success', False):
            print(f"    Error: {result.get('error', 'Unknown')}")
    
    if success_rate >= 75:
        print(f"\nSYSTEM INTEGRATION: SUCCESSFUL ({success_rate:.1f}% success rate)")
        return True
    else:
        print(f"\nSYSTEM INTEGRATION: NEEDS ATTENTION ({success_rate:.1f}% success rate)")
        return False

if __name__ == "__main__":
    success = test_complete_system_integration()
    sys.exit(0 if success else 1)
