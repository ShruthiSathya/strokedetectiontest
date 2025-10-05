#!/usr/bin/env python3
"""
Test Lambda Debug
Test the Lambda function with debug output to see what's happening inside
"""

import requests
import json

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def test_lambda_with_debug():
    """Test Lambda function with debug information"""
    
    print("🔍 Testing Lambda Function Internals")
    print("=" * 50)
    print("Checking what's happening inside the Lambda function")
    print()
    
    # Test with a scenario that should show drift
    test_payload = {
        "keypoints": {
            "left_wrist": {"x": 0.3, "y": 0.7},
            "right_wrist": {"x": 0.7, "y": 0.76},  # 6% down - should be moderate drift
            "left_shoulder": {"x": 0.35, "y": 0.3},
            "right_shoulder": {"x": 0.65, "y": 0.3}
        },
        "user_id": "debug_lambda_test",
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    print("📤 Sending payload to Lambda:")
    print(f"   Left wrist: ({test_payload['keypoints']['left_wrist']['x']}, {test_payload['keypoints']['left_wrist']['y']})")
    print(f"   Right wrist: ({test_payload['keypoints']['right_wrist']['x']}, {test_payload['keypoints']['right_wrist']['y']})")
    print(f"   Left shoulder: ({test_payload['keypoints']['left_shoulder']['x']}, {test_payload['keypoints']['left_shoulder']['y']})")
    print(f"   Right shoulder: ({test_payload['keypoints']['right_shoulder']['x']}, {test_payload['keypoints']['right_shoulder']['y']})")
    print()
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json=test_payload,
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
            
            print("📥 Lambda Response:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Raw Response Keys: {list(raw_response.keys())}")
            print()
            
            print("📊 Analysis Results:")
            print(f"   🎯 Severity: {result.get('severity', 'unknown')}")
            print(f"   📊 Asymmetry: {result.get('asymmetry_score', 0):.4f}")
            print(f"   🏥 NIHSS: {result.get('nihss_motor_score', 0)}/4")
            print(f"   🔍 Drift Detected: {result.get('drift_detected', False)}")
            print(f"   💬 Message: {result.get('message', 'N/A')}")
            print(f"   🔧 Method: {result.get('analysis_method', 'unknown')}")
            print(f"   📦 Version: {result.get('version', 'unknown')}")
            print(f"   ⏱️ Analysis Time: {result.get('analysis_time_seconds', 0):.4f}s")
            print(f"   ⏱️ Total Runtime: {result.get('total_runtime_seconds', 0):.4f}s")
            print()
            
            # Check if there's an error field
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            
            # Expected calculation
            left_wrist_y = test_payload['keypoints']['left_wrist']['y']
            right_wrist_y = test_payload['keypoints']['right_wrist']['y']
            left_shoulder_y = test_payload['keypoints']['left_shoulder']['y']
            right_shoulder_y = test_payload['keypoints']['right_shoulder']['y']
            
            vertical_drift = abs(left_wrist_y - right_wrist_y)
            left_arm_length = abs(left_wrist_y - left_shoulder_y)
            right_arm_length = abs(right_wrist_y - right_shoulder_y)
            avg_arm_length = (left_arm_length + right_arm_length) / 2
            
            if avg_arm_length > 0:
                expected_asymmetry = vertical_drift / avg_arm_length
            else:
                expected_asymmetry = 0.0
            
            print("🧮 Expected Calculation:")
            print(f"   Vertical drift: {vertical_drift:.4f}")
            print(f"   Left arm length: {left_arm_length:.4f}")
            print(f"   Right arm length: {right_arm_length:.4f}")
            print(f"   Avg arm length: {avg_arm_length:.4f}")
            print(f"   Expected asymmetry: {expected_asymmetry:.4f} ({expected_asymmetry*100:.1f}%)")
            print()
            
            # Compare
            lambda_asymmetry = result.get('asymmetry_score', 0)
            if abs(lambda_asymmetry - expected_asymmetry) < 0.001:
                print("✅ Lambda calculation matches expected!")
            else:
                print(f"❌ MISMATCH: Lambda={lambda_asymmetry:.4f}, Expected={expected_asymmetry:.4f}")
                print("🔍 The Lambda function has a bug in the keypoint analysis!")
                
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_lambda_with_debug()
