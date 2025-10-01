#!/usr/bin/env python3
"""
Test script for enhanced reminder system
"""
import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:8000/api"

def test_smart_reminder_creation():
    """Test creating a smart reminder with scheduling"""
    print("🧪 Testing Smart Reminder Creation")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Once Daily Metformin",
            "data": {
                "medicine_name": "Metformin",
                "dosage": "500mg",
                "frequency": "once daily",
                "time": "08:00",
                "duration": "30 days"
            }
        },
        {
            "name": "Twice Daily Ibuprofen", 
            "data": {
                "medicine_name": "Ibuprofen",
                "dosage": "400mg",
                "frequency": "twice daily",
                "time": "09:00",
                "duration": "7 days"
            }
        },
        {
            "name": "Three Times Daily Amoxicillin",
            "data": {
                "medicine_name": "Amoxicillin", 
                "dosage": "250mg",
                "frequency": "three times daily",
                "time": "08:00",
                "duration": "10 days"
            }
        }
    ]
    
    reminder_ids = []
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        
        try:
            response = requests.post(f"{BASE_URL}/reminders/set/", json=test_case['data'])
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data['message']}")
                
                reminder = data['reminder']
                schedule_info = data['schedule_info']
                
                print(f"   📅 Schedule: {schedule_info['total_reminders']} reminders generated")
                print(f"   ⏰ Next: {schedule_info['next_reminder']['datetime'] if schedule_info['next_reminder'] else 'N/A'}")
                print(f"   📊 Frequency: {schedule_info['frequency_parsed']['times_per_day']} times/day")
                
                reminder_ids.append(reminder['id'])
                
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return reminder_ids

def test_reminder_management():
    """Test getting and managing reminders"""
    print("\n\n🧪 Testing Reminder Management")
    print("=" * 50)
    
    try:
        # Get all reminders
        response = requests.get(f"{BASE_URL}/reminders/?user_id=default_user")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {data['total']} reminders")
            print(f"📊 Active reminders: {data['summary']['active_reminders']}")
            print(f"📈 Average adherence: {data['summary']['average_adherence']}%")
            
            reminders = data['reminders']
            if reminders:
                reminder_id = reminders[0]['id']
                
                # Test medication tracking
                print(f"\n📝 Testing medication tracking for reminder: {reminder_id}")
                
                # Track taken medication
                track_response = requests.post(
                    f"{BASE_URL}/reminders/{reminder_id}/track/",
                    json={"action": "taken"}
                )
                
                if track_response.status_code == 200:
                    track_data = track_response.json()
                    print(f"✅ {track_data['message']}")
                    summary = track_data['adherence_summary']
                    print(f"   📊 Adherence: {summary['adherence_rate']}% ({summary['status']})")
                    print(f"   💊 Taken: {summary['taken_doses']}/{summary['total_doses']}")
                
                # Track missed medication
                track_response = requests.post(
                    f"{BASE_URL}/reminders/{reminder_id}/track/",
                    json={"action": "missed"}
                )
                
                if track_response.status_code == 200:
                    track_data = track_response.json()
                    print(f"✅ {track_data['message']}")
                    summary = track_data['adherence_summary']
                    print(f"   📊 Updated adherence: {summary['adherence_rate']}% ({summary['status']})")
                
        else:
            print(f"❌ Failed to get reminders: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_smart_scheduling():
    """Test smart scheduling functionality"""
    print("\n\n🧪 Testing Smart Scheduling")
    print("=" * 50)
    
    frequency_tests = [
        ("once daily", 1),
        ("twice daily", 2), 
        ("three times daily", 3),
        ("every 6 hours", 4),
        ("every 8 hours", 3),
        ("daily", 1)
    ]
    
    for freq_text, expected_times in frequency_tests:
        print(f"\n📅 Testing: '{freq_text}'")
        
        try:
            response = requests.post(f"{BASE_URL}/reminders/set/", json={
                "medicine_name": "Test Medicine",
                "dosage": "100mg", 
                "frequency": freq_text,
                "time": "08:00"
            })
            
            if response.status_code == 200:
                data = response.json()
                actual_times = data['schedule_info']['frequency_parsed']['times_per_day']
                
                if actual_times == expected_times:
                    print(f"✅ Correct: {actual_times} times/day")
                else:
                    print(f"⚠️  Expected: {expected_times}, Got: {actual_times}")
                
                # Clean up test reminder
                reminder_id = data['reminder']['id']
                requests.delete(f"{BASE_URL}/reminders/{reminder_id}/")
                
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Enhanced Reminder System Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/ping/")
        if response.status_code != 200:
            print("❌ Server not responding. Please start the Django server.")
            return
    except:
        print("❌ Cannot connect to server. Please start the Django server.")
        return
    
    print("✅ Server is running")
    
    # Run tests
    reminder_ids = test_smart_reminder_creation()
    test_reminder_management() 
    test_smart_scheduling()
    
    print("\n\n🎉 Test Suite Complete!")
    print("=" * 60)
    
    if reminder_ids:
        print(f"📝 Created {len(reminder_ids)} test reminders")
        print("💡 You can view them in the web app or delete them manually")

if __name__ == "__main__":
    main()
