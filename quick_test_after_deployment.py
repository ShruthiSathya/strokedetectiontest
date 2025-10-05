#!/usr/bin/env python3
"""
Quick Test After Deployment
Test if the improved Lambda function is working
"""

import requests
import json
import base64

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def test_after_deployment():
    """Test if the improved function is deployed"""
    
    print("🧪 Testing After Deployment")
    print("=" * 40)
    
    # Create test image
    test_image_b64 = base64.b64encode(b'test_image_data').decode('utf-8')
    
    payload = {
        "image_base64": test_image_b64,
        "user_id": "deployment_test",
        "keypoints_detected": 10,  # Excellent calibration
        "image_size_bytes": len(base64.b64decode(test_image_b64)),
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            raw_response = response.json()
            if 'body' in raw_response:
                body_data = json.loads(raw_response['body'])
                result = body_data
            else:
                result = raw_response
            
            print("📊 RESULTS:")
            print(f"   Severity: {result.get('severity', 'unknown').upper()}")
            print(f"   NIHSS: {result.get('nihss_motor_score', 0)}/4")
            print(f"   Y-Diff: {result.get('y_difference', 0)*100:.2f}%")
            print(f"   Drift: {result.get('drift_detected', False)}")
            
            # Check if improved version is deployed
            severity = result.get('severity', '').lower()
            y_diff = result.get('y_difference', 0)
            
            if severity == 'normal' and y_diff < 0.10:
                print("\n✅ IMPROVED VERSION DEPLOYED!")
                print("✅ Your straight-arm test should now show NORMAL")
                return True
            else:
                print(f"\n⚠️ Still showing {severity.upper()} - old version still active")
                print("🔧 Need to deploy the improved version")
                return False
                
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Quick Test After Deployment")
    print("Check if improved Lambda function is active")
    print()
    
    success = test_after_deployment()
    
    if success:
        print("\n🎉 SUCCESS! Improved version is deployed!")
        print("Your app should now show NORMAL results for straight arms")
    else:
        print("\n⚠️ Improved version not deployed yet")
        print("Please deploy the improved Lambda function first")
