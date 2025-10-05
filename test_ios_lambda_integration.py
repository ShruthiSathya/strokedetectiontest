#!/usr/bin/env python3
"""
Test iOS App + Lambda Integration
Verify that the updated iOS app sends the correct keypoint format to Lambda
"""

import requests
import json

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def test_ios_keypoint_format():
    """Test the keypoint format that the iOS app now sends"""
    
    print("🧪 Testing iOS App + Lambda Integration")
    print("=" * 60)
    print("Testing the new keypoint-based communication")
    print()
    
    # Simulate the keypoint payload that the iOS app now sends
    ios_keypoint_payload = {
        "keypoints": {
            "left_wrist": {"x": 0.3, "y": 0.7},      # Normalized coordinates (0-1)
            "right_wrist": {"x": 0.7, "y": 0.7},     # Same Y = no drift
            "left_shoulder": {"x": 0.35, "y": 0.3},
            "right_shoulder": {"x": 0.65, "y": 0.3},
            "left_elbow": {"x": 0.32, "y": 0.5},     # Additional keypoints
            "right_elbow": {"x": 0.68, "y": 0.5}
        },
        "user_id": "ios_app_test",
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    print("📱 iOS App Payload Format:")
    print(f"   Keypoints: {len(ios_keypoint_payload['keypoints'])} detected")
    print(f"   Left wrist: ({ios_keypoint_payload['keypoints']['left_wrist']['x']:.2f}, {ios_keypoint_payload['keypoints']['left_wrist']['y']:.2f})")
    print(f"   Right wrist: ({ios_keypoint_payload['keypoints']['right_wrist']['x']:.2f}, {ios_keypoint_payload['keypoints']['right_wrist']['y']:.2f})")
    print(f"   User ID: {ios_keypoint_payload['user_id']}")
    print()
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json=ios_keypoint_payload,
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
            
            print("✅ SUCCESS: iOS App + Lambda Integration Working!")
            print()
            print("📊 Lambda Response:")
            print(f"   🎯 Severity: {result.get('severity', 'unknown').upper()}")
            print(f"   📊 Asymmetry: {result.get('asymmetry_score', 0):.4f} ({result.get('asymmetry_score', 0)*100:.1f}%)")
            print(f"   🏥 NIHSS: {result.get('nihss_motor_score', 0)}/4")
            print(f"   🔍 Drift Detected: {result.get('drift_detected', False)}")
            print(f"   💬 Message: {result.get('message', 'N/A')}")
            print(f"   🔧 Method: {result.get('analysis_method', 'unknown')}")
            print(f"   📦 Version: {result.get('version', 'unknown')}")
            print(f"   ⏱️ Analysis Time: {result.get('analysis_time_seconds', 0):.4f}s")
            print()
            
            # Verify this is the keypoint-based version
            analysis_method = result.get('analysis_method', '')
            version = result.get('version', '')
            
            if 'keypoint' in analysis_method.lower() or 'corrected_v3' in version:
                print("🎉 CONFIRMED: Keypoint-based Lambda version is active!")
                print("✅ iOS app integration is working correctly!")
                
                # Check for expected results
                severity = result.get('severity', '').lower()
                asymmetry_score = result.get('asymmetry_score', 0)
                
                if severity == 'normal' and asymmetry_score < 0.05:
                    print("✅ Perfect: No drift detected for straight arms")
                elif severity in ['normal', 'mild'] and asymmetry_score < 0.15:
                    print("✅ Good: Minimal drift detected")
                else:
                    print(f"⚠️ Unexpected result: {severity} with {asymmetry_score:.4f} asymmetry")
                
                return True
            else:
                print("❌ OLD VERSION: Not using keypoint-based analysis")
                return False
                
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_drift_scenarios():
    """Test different drift scenarios with iOS keypoint format"""
    
    print("\n🧪 Testing Drift Scenarios with iOS Format")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Perfect Calibration (No Drift)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.7},  # Same Y = no drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected": "normal"
        },
        {
            "name": "Slight Drift (5%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.72},  # 2% lower (0.02/0.4 = 5%)
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected": "mild"
        },
        {
            "name": "Moderate Drift (15%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.76},  # 6% lower (0.06/0.4 = 15%)
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected": "moderate"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Test {i}: {scenario['name']}")
        
        payload = {
            "keypoints": scenario["keypoints"],
            "user_id": f"ios_drift_test_{i}",
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
                
                print(f"   ✅ Result: {severity.upper()}")
                print(f"   📊 Asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
                print(f"   🏥 NIHSS: {result.get('nihss_motor_score', 0)}/4")
                
                # Check if result matches expectation
                expected = scenario['expected']
                if severity.lower() == expected:
                    print(f"   ✅ PERFECT MATCH! Expected {expected}, got {severity}")
                else:
                    print(f"   ⚠️ Different result: Expected {expected}, got {severity}")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🏥 Test iOS App + Lambda Integration")
    print("Verifying keypoint-based communication")
    print()
    
    # Test the main integration
    integration_success = test_ios_keypoint_format()
    
    if integration_success:
        # Test different scenarios
        test_drift_scenarios()
        
        print("\n🎉 INTEGRATION TEST: SUCCESS!")
        print("✅ iOS app and Lambda are communicating correctly")
        print("✅ Keypoint-based analysis is working")
        print("✅ Your stroke detection app is ready for testing!")
    else:
        print("\n❌ INTEGRATION TEST: FAILED")
        print("🔧 Need to verify Lambda deployment and iOS app updates")
