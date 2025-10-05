#!/usr/bin/env python3
"""
Test script for different Lambda function scenarios
Run this to test various drift detection cases
"""

import requests
import base64
import json

# AWS Lambda URL
LAMBDA_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

# Test image (minimal PNG)
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_scenario(scenario_name, force_drift=False, test_mode=True):
    """Test a specific scenario"""
    print(f"\n🧪 Testing: {scenario_name}")
    print("=" * 50)
    
    payload = {
        "image_base64": TEST_IMAGE_BASE64,
        "user_id": f"test_{scenario_name.lower().replace(' ', '_')}",
        "test_mode": test_mode,
        "force_drift": force_drift
    }
    
    print(f"📤 Sending payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            LAMBDA_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            body_data = json.loads(result.get('body', '{}'))
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Drift Detected: {body_data.get('drift_detected', 'Unknown')}")
            print(f"📏 Y Difference: {body_data.get('y_difference', 'Unknown'):.4f}")
            print(f"🎯 Severity: {body_data.get('severity', 'Unknown')}")
            print(f"💬 Message: {body_data.get('message', 'Unknown')}")
            print(f"🏥 NIHSS Motor Score: {body_data.get('nihss_motor_score', 'Unknown')}")
            print(f"📈 Clinical Score: {body_data.get('clinical_score', 'Unknown')}")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🔬 Lambda Function Drift Detection Test Suite")
    print("=" * 60)
    
    # Test scenarios
    test_scenario("Normal Position (No Drift)", force_drift=False)
    test_scenario("Simulated Drift (Test Mode)", force_drift=True)
    test_scenario("Real Image Analysis", force_drift=False, test_mode=False)
    
    print(f"\n📝 Test Summary:")
    print(f"- Normal Position: Should show no drift detected")
    print(f"- Simulated Drift: Should show drift detected with high severity")
    print(f"- Real Image: Depends on actual image characteristics")
    
    print(f"\n💡 To test with real camera images:")
    print(f"1. Run your iOS app")
    print(f"2. Position yourself with arms extended")
    print(f"3. Try different positions (symmetric vs asymmetric)")
    print(f"4. Check the console logs for debug information")

if __name__ == "__main__":
    main()
