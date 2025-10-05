#!/usr/bin/env python3
"""
Debug Keypoint Analysis
Test the keypoint analysis logic to find why it's returning 0.0000 for all scenarios
"""

import requests
import json

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def debug_keypoint_calculation():
    """Debug the keypoint calculation logic"""
    
    print("🔍 Debug Keypoint Analysis")
    print("=" * 50)
    print("Testing keypoint calculations to find the bug")
    print()
    
    # Test scenarios with different drift amounts
    test_scenarios = [
        {
            "name": "No Drift (Same Y)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.7},  # Same Y = 0 drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_drift": 0.0,
            "expected_severity": "normal"
        },
        {
            "name": "Small Drift (2% down)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.72},  # 2% down
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_drift": 0.05,  # 2% of arm length = 5% drift
            "expected_severity": "mild"
        },
        {
            "name": "Medium Drift (6% down)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.76},  # 6% down
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_drift": 0.15,  # 6% of arm length = 15% drift
            "expected_severity": "moderate"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🧪 Test {i}: {scenario['name']}")
        
        # Calculate expected values manually
        left_wrist_y = scenario['keypoints']['left_wrist']['y']
        right_wrist_y = scenario['keypoints']['right_wrist']['y']
        left_shoulder_y = scenario['keypoints']['left_shoulder']['y']
        right_shoulder_y = scenario['keypoints']['right_shoulder']['y']
        
        # Manual calculation
        vertical_drift_pixels = abs(left_wrist_y - right_wrist_y)
        left_arm_length = abs(left_wrist_y - left_shoulder_y)
        right_arm_length = abs(right_wrist_y - right_shoulder_y)
        avg_arm_length = (left_arm_length + right_arm_length) / 2
        
        if avg_arm_length > 0:
            manual_asymmetry = vertical_drift_pixels / avg_arm_length
        else:
            manual_asymmetry = 0.0
        
        print(f"   📊 Manual Calculation:")
        print(f"      Left wrist Y: {left_wrist_y}")
        print(f"      Right wrist Y: {right_wrist_y}")
        print(f"      Vertical drift: {vertical_drift_pixels:.4f}")
        print(f"      Left arm length: {left_arm_length:.4f}")
        print(f"      Right arm length: {right_arm_length:.4f}")
        print(f"      Avg arm length: {avg_arm_length:.4f}")
        print(f"      Manual asymmetry: {manual_asymmetry:.4f} ({manual_asymmetry*100:.1f}%)")
        print()
        
        # Test with Lambda
        payload = {
            "keypoints": scenario["keypoints"],
            "user_id": f"debug_test_{i}",
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
                
                lambda_asymmetry = result.get('asymmetry_score', 0)
                lambda_severity = result.get('severity', 'unknown')
                
                print(f"   🤖 Lambda Result:")
                print(f"      Asymmetry: {lambda_asymmetry:.4f} ({lambda_asymmetry*100:.1f}%)")
                print(f"      Severity: {lambda_severity}")
                print(f"      NIHSS: {result.get('nihss_motor_score', 0)}/4")
                print()
                
                # Compare results
                if abs(lambda_asymmetry - manual_asymmetry) < 0.001:
                    print(f"   ✅ Lambda matches manual calculation!")
                else:
                    print(f"   ❌ MISMATCH: Lambda={lambda_asymmetry:.4f}, Manual={manual_asymmetry:.4f}")
                
                # Check severity
                if lambda_severity.lower() == scenario['expected_severity']:
                    print(f"   ✅ Correct severity: {lambda_severity}")
                else:
                    print(f"   ⚠️ Wrong severity: Expected {scenario['expected_severity']}, got {lambda_severity}")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    debug_keypoint_calculation()
