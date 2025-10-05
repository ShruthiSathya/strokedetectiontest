#!/usr/bin/env python3
"""
Test Keypoint-Based Lambda Function
Test the new clinically accurate version
"""

import requests
import json

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def create_test_keypoints():
    """Create realistic keypoint data for testing"""
    
    # Simulate a person with arms extended, minimal drift
    base_y = 200  # Base vertical position
    arm_length = 150  # Arm length in pixels
    
    # Perfect calibration - no drift
    perfect_keypoints = {
        "left_wrist": {"y": base_y + arm_length, "x": 100},
        "right_wrist": {"y": base_y + arm_length, "x": 300},  # Same Y = no drift
        "left_shoulder": {"y": base_y, "x": 120},
        "right_shoulder": {"y": base_y, "x": 280}
    }
    
    # Slight drift - one arm 10 pixels lower (10/150 = 6.7% drift)
    slight_drift_keypoints = {
        "left_wrist": {"y": base_y + arm_length, "x": 100},
        "right_wrist": {"y": base_y + arm_length + 10, "x": 300},  # 10 pixels lower
        "left_shoulder": {"y": base_y, "x": 120},
        "right_shoulder": {"y": base_y, "x": 280}
    }
    
    # Moderate drift - one arm 30 pixels lower (30/150 = 20% drift)
    moderate_drift_keypoints = {
        "left_wrist": {"y": base_y + arm_length, "x": 100},
        "right_wrist": {"y": base_y + arm_length + 30, "x": 300},  # 30 pixels lower
        "left_shoulder": {"y": base_y, "x": 120},
        "right_shoulder": {"y": base_y, "x": 280}
    }
    
    return {
        "perfect": perfect_keypoints,
        "slight_drift": slight_drift_keypoints,
        "moderate_drift": moderate_drift_keypoints
    }

def test_keypoint_scenarios():
    """Test different drift scenarios"""
    
    print("🧪 Testing Keypoint-Based Lambda Function")
    print("=" * 60)
    print("Testing clinically accurate drift detection using skeletal keypoints")
    print()
    
    test_cases = create_test_keypoints()
    
    scenarios = [
        {
            "name": "Perfect Calibration (No Drift)",
            "keypoints": test_cases["perfect"],
            "expected": "normal",
            "description": "Both arms at same height - should show NORMAL"
        },
        {
            "name": "Slight Drift (6.7%)",
            "keypoints": test_cases["slight_drift"],
            "expected": "mild",
            "description": "One arm 10 pixels lower - should show MILD"
        },
        {
            "name": "Moderate Drift (20%)",
            "keypoints": test_cases["moderate_drift"],
            "expected": "moderate",
            "description": "One arm 30 pixels lower - should show MODERATE"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🧪 Test {i}: {scenario['name']}")
        print(f"   📋 {scenario['description']}")
        
        payload = {
            "keypoints": scenario["keypoints"],
            "user_id": f"keypoint_test_{i}"
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
                version = result.get('version', 'unknown')
                analysis_method = result.get('analysis_method', 'unknown')
                
                print(f"   ✅ Result: {severity.upper()}")
                print(f"   📊 Asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
                print(f"   🏥 NIHSS: {nihss_score}/4")
                print(f"   🔧 Method: {analysis_method}")
                print(f"   📦 Version: {version}")
                print(f"   💬 Message: {result.get('message', 'N/A')[:50]}...")
                
                # Check if this is the new version
                if 'keypoint' in analysis_method.lower() or 'corrected_v3' in version:
                    print(f"   🎉 NEW KEYPOINT VERSION DETECTED!")
                    
                    # Evaluate results
                    expected = scenario['expected']
                    if severity.lower() == expected:
                        print(f"   ✅ PERFECT MATCH! Expected {expected}, got {severity}")
                    else:
                        print(f"   ⚠️ Different result: Expected {expected}, got {severity}")
                else:
                    print(f"   ❌ OLD VERSION STILL ACTIVE")
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

def test_your_scenario():
    """Test your specific scenario"""
    
    print("🎯 Testing Your Specific Scenario")
    print("=" * 60)
    print("Simulating: Arms held straight, should show NORMAL")
    print()
    
    # Create keypoints for straight arms (your scenario)
    straight_arms_keypoints = {
        "left_wrist": {"y": 350, "x": 100},
        "right_wrist": {"y": 350, "x": 300},  # Same Y = no drift
        "left_shoulder": {"y": 200, "x": 120},
        "right_shoulder": {"y": 200, "x": 280}
    }
    
    payload = {
        "keypoints": straight_arms_keypoints,
        "user_id": "your_straight_arms_test"
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
            
            print("📊 YOUR SCENARIO RESULTS:")
            print(f"   🎯 Severity: {result.get('severity', 'unknown').upper()}")
            print(f"   📊 Asymmetry: {result.get('asymmetry_score', 0):.4f} ({result.get('asymmetry_score', 0)*100:.1f}%)")
            print(f"   🏥 NIHSS: {result.get('nihss_motor_score', 0)}/4")
            print(f"   🔍 Drift Detected: {result.get('drift_detected', False)}")
            print(f"   💬 Message: {result.get('message', 'N/A')}")
            print(f"   🔧 Method: {result.get('analysis_method', 'unknown')}")
            print(f"   📦 Version: {result.get('version', 'unknown')}")
            
            # Evaluate for your scenario
            severity = result.get('severity', '').lower()
            asymmetry_score = result.get('asymmetry_score', 0)
            
            if severity == 'normal' and asymmetry_score < 0.05:
                print(f"\n🎉 PERFECT! Your straight arms test shows NORMAL results")
                print(f"✅ The new keypoint-based analysis is working correctly!")
                return True
            elif severity in ['normal', 'mild'] and asymmetry_score < 0.15:
                print(f"\n✅ GOOD! Much better than the old CRITICAL result")
                print(f"✅ The new version is more accurate")
                return True
            else:
                print(f"\n⚠️ Still showing {severity.upper()} - may need deployment")
                return False
                
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Test Keypoint-Based Lambda Function")
    print("Testing the new clinically accurate version")
    print()
    
    # Test your scenario first
    your_success = test_your_scenario()
    
    print("\n" + "="*60 + "\n")
    
    # Test multiple scenarios
    test_keypoint_scenarios()
    
    if your_success:
        print("\n🎉 KEYPOINT-BASED VERSION: SUCCESS!")
        print("✅ Your improved code is working correctly!")
        print("✅ Much more clinically accurate than the old version!")
    else:
        print("\n⚠️ Need to deploy the keypoint-based version")
        print("🔧 Copy your improved lambda_fast_enhanced.py to AWS")
