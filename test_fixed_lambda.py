#!/usr/bin/env python3
"""
Test Fixed Lambda Function
Test the Lambda function after fixing the keypoint analysis bug
"""

import requests
import json

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def test_fixed_lambda():
    """Test the Lambda function after fixing the bug"""
    
    print("🔧 Testing Fixed Lambda Function")
    print("=" * 50)
    print("Testing after fixing the avg_arm_length < 1 bug")
    print()
    
    test_scenarios = [
        {
            "name": "No Drift",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.7},  # Same Y = no drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "normal"
        },
        {
            "name": "Small Drift (5%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.72},  # 2% down = 5% drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "mild"
        },
        {
            "name": "Medium Drift (15%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.76},  # 6% down = 15% drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "moderate"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🧪 Test {i}: {scenario['name']}")
        
        payload = {
            "keypoints": scenario["keypoints"],
            "user_id": f"fixed_test_{i}",
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
                
                severity = result.get('severity', 'unknown')
                asymmetry_score = result.get('asymmetry_score', 0)
                nihss_score = result.get('nihss_motor_score', 0)
                
                print(f"   🎯 Result: {severity.upper()}")
                print(f"   📊 Asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
                print(f"   🏥 NIHSS: {nihss_score}/4")
                print(f"   💬 Message: {result.get('message', 'N/A')[:50]}...")
                
                # Check if this matches expectation
                expected = scenario['expected_severity']
                if severity.lower() == expected:
                    print(f"   ✅ PERFECT! Expected {expected}, got {severity}")
                else:
                    print(f"   ⚠️ Different: Expected {expected}, got {severity}")
                
                # Check if asymmetry is no longer 0.0000
                if asymmetry_score > 0.001:
                    print(f"   ✅ FIXED! Asymmetry is no longer 0.0000")
                else:
                    print(f"   ❌ STILL BROKEN! Asymmetry is still 0.0000")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_fixed_lambda()
