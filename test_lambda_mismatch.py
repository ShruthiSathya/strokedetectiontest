#!/usr/bin/env python3
"""
Test the Lambda function mismatch issue.
This will show why the app is giving an error even when console output is correct.
"""

import json
import requests

def test_current_lambda():
    """Test the current deployed Lambda function with the payload format the iOS app sends."""
    
    # This is the payload format your iOS app is sending
    ios_payload = {
        "keypoints": {
            "left_wrist": {"x": 0.5560755729675293, "y": 0.5311617851257324},
            "left_shoulder": {"x": 0.5504499673843384, "y": 0.5109182596206665},
            "right_wrist": {"x": 0.3835928738117218, "y": 0.5197547674179077},
            "right_shoulder": {"x": 0.42909833788871765, "y": 0.506827712059021}
        },
        "user_id": "test_user",
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    print("🔍 TESTING LAMBDA FUNCTION MISMATCH")
    print("=" * 60)
    print("📤 Sending iOS payload format to current Lambda function...")
    print(f"   Payload keys: {list(ios_payload.keys())}")
    print(f"   Keypoints: {list(ios_payload['keypoints'].keys())}")
    print()
    
    API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json=ios_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Response body: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Lambda function responded successfully")
                print(f"   Drift detected: {result.get('drift_detected', 'unknown')}")
                print(f"   NIHSS score: {result.get('nihss_motor_score', 'unknown')}")
                print(f"   Severity: {result.get('severity', 'unknown')}")
            except json.JSONDecodeError:
                print("❌ Lambda responded but with invalid JSON")
        else:
            print(f"❌ Lambda function returned error status: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ Lambda function timed out (this causes the 15-second timeout in iOS)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    
    print()
    print("🔍 ANALYSIS:")
    print("   The current Lambda function expects 'image_base64' field")
    print("   But your iOS app is sending 'keypoints' field")
    print("   This mismatch causes the Lambda to fail")
    print("   The iOS app then shows an error after 15-second timeout")
    print()
    print("💡 SOLUTION:")
    print("   Deploy the robust Lambda function (lambda_robust_asymmetry.py)")
    print("   which properly handles the keypoint payload format")

def test_robust_lambda_locally():
    """Test the robust Lambda function locally to show it works."""
    
    print("🧪 TESTING ROBUST LAMBDA FUNCTION LOCALLY")
    print("=" * 60)
    
    # Import the robust Lambda function
    import sys
    sys.path.append('.')
    
    try:
        from lambda_robust_asymmetry import lambda_handler
        
        # Test event (simulating API Gateway)
        test_event = {
            "body": json.dumps({
                "keypoints": {
                    "left_wrist": {"x": 0.5560755729675293, "y": 0.5311617851257324},
                    "left_shoulder": {"x": 0.5504499673843384, "y": 0.5109182596206665},
                    "right_wrist": {"x": 0.3835928738117218, "y": 0.5197547674179077},
                    "right_shoulder": {"x": 0.42909833788871765, "y": 0.506827712059021}
                },
                "user_id": "test_user",
                "test_mode": False,
                "force_drift": False,
                "user_intentionally_drifting": False
            })
        }
        
        # Mock context
        class MockContext:
            def get_remaining_time_in_millis(self):
                return 30000
        
        result = lambda_handler(test_event, MockContext())
        
        print("✅ Robust Lambda function works correctly!")
        print(f"   Status code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"   Drift detected: {body.get('drift_detected', 'unknown')}")
            print(f"   Asymmetry: {body.get('asymmetry_percent', 'unknown')}%")
            print(f"   NIHSS score: {body.get('nihss_motor_score', 'unknown')}")
            print(f"   Severity: {body.get('severity', 'unknown')}")
            print(f"   Method used: {body.get('analysis_method', 'unknown')}")
            print(f"   Detection quality: {body.get('detection_quality', 'unknown')}")
        
    except ImportError as e:
        print(f"❌ Could not import robust Lambda function: {e}")
    except Exception as e:
        print(f"❌ Error testing robust Lambda: {e}")

if __name__ == "__main__":
    test_current_lambda()
    print()
    test_robust_lambda_locally()
