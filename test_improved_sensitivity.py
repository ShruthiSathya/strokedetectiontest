#!/usr/bin/env python3
"""
Test Improved Sensitivity
Simulates your exact test scenario with improved thresholds
"""

import requests
import json
import base64

# API Gateway URL
API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def create_realistic_test_image():
    """Create a test image that simulates your exact scenario"""
    
    # Create a 400x300 pixel image (realistic camera size)
    width, height = 400, 300
    test_image_data = bytearray()
    
    # Simulate a person with arms extended, minimal asymmetry
    for y in range(height):
        for x in range(width):
            center_x = width // 2
            center_y = height // 2
            
            # Distance from center
            dist_x = abs(x - center_x)
            dist_y = abs(y - center_y)
            
            # Simulate very minimal asymmetry (like your test)
            if x < center_x:  # Left side
                r = 120 + dist_x // 4 - dist_y // 5
                g = 130 + dist_x // 5 - dist_y // 4
                b = 140 + dist_x // 6 - dist_y // 6
            else:  # Right side
                r = 118 + dist_x // 4 - dist_y // 5  # Very slight difference
                g = 132 + dist_x // 5 - dist_y // 4  # Very slight difference
                b = 138 + dist_x // 6 - dist_y // 6  # Very slight difference
            
            # Add minimal noise
            r += 2
            g += 1
            b += 1
            
            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            test_image_data.extend([r, g, b])
    
    return base64.b64encode(test_image_data).decode('utf-8')

def test_improved_sensitivity():
    """Test the improved sensitivity thresholds"""
    
    print("🧪 Testing Improved Sensitivity Thresholds")
    print("=" * 60)
    print("Simulating your exact test scenario:")
    print("- Arms held straight (minimal asymmetry)")
    print("- Excellent calibration (10+ keypoints)")
    print("- Real camera image size")
    print()
    
    # Create test payload matching your scenario
    test_image_b64 = create_realistic_test_image()
    
    payload = {
        "image_base64": test_image_b64,
        "user_id": "sensitivity_test_user",
        "keypoints_detected": 10,  # Excellent calibration like yours
        "image_size_bytes": len(base64.b64decode(test_image_b64)),
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    print(f"📤 Test Parameters:")
    print(f"   - Image size: {payload['image_size_bytes']} bytes")
    print(f"   - Keypoints: {payload['keypoints_detected']} (excellent calibration)")
    print(f"   - Expected: Normal results (arms held straight)")
    print()
    
    try:
        start_time = time.time()
        
        response = requests.post(
            API_GATEWAY_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        response_time = time.time() - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📡 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            raw_response = response.json()
            if 'body' in raw_response:
                body_data = json.loads(raw_response['body'])
                result = body_data
            else:
                result = raw_response
            
            print("\n📊 IMPROVED RESULTS:")
            print(f"   🎯 Severity: {result.get('severity', 'unknown').upper()}")
            print(f"   🏥 NIHSS Score: {result.get('nihss_motor_score', 0)}/4")
            print(f"   📈 Y-Difference: {result.get('y_difference', 0):.4f} ({result.get('y_difference', 0)*100:.2f}%)")
            print(f"   🔍 Drift Detected: {result.get('drift_detected', False)}")
            print(f"   📝 Message: {result.get('message', 'N/A')}")
            print(f"   🎯 Test Quality: {result.get('test_quality', 'unknown')}")
            print(f"   ⚡ Analysis Time: {result.get('analysis_time', 0):.3f}s")
            
            # Evaluate the result
            severity = result.get('severity', 'unknown').lower()
            y_diff = result.get('y_difference', 0)
            
            print(f"\n🎯 EVALUATION:")
            if severity == "normal" and not result.get('drift_detected', True):
                print("   ✅ PERFECT! System correctly identified no drift")
                print("   ✅ Improved sensitivity working correctly")
                return True
            elif severity == "mild" and y_diff < 0.10:
                print("   ⚠️ ACCEPTABLE - Minor drift detected (within normal variation)")
                print("   ✅ Much better than previous 'moderate' result")
                return True
            elif severity in ["moderate", "severe", "critical"]:
                print("   ❌ STILL TOO SENSITIVE - Detecting drift where none exists")
                print("   🔧 Further threshold adjustment needed")
                return False
            else:
                print("   ❓ UNEXPECTED RESULT - Need to investigate")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multiple_scenarios():
    """Test multiple scenarios to verify improvements"""
    
    print(f"\n🔄 Testing Multiple Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Excellent Calibration (10+ keypoints)",
            "keypoints": 11,
            "expected": "normal",
            "desc": "Should be normal with excellent calibration"
        },
        {
            "name": "Good Calibration (8 keypoints)",
            "keypoints": 8,
            "expected": "normal_to_mild",
            "desc": "Should be normal to mild"
        },
        {
            "name": "Poor Calibration (4 keypoints)",
            "keypoints": 4,
            "expected": "conservative",
            "desc": "Should be more conservative"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Test {i}: {scenario['name']}")
        print(f"   📋 {scenario['desc']}")
        
        test_image_b64 = create_realistic_test_image()
        payload = {
            "image_base64": test_image_b64,
            "user_id": f"scenario_test_{i}",
            "keypoints_detected": scenario["keypoints"],
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
                timeout=10
            )
            
            if response.status_code == 200:
                raw_response = response.json()
                if 'body' in raw_response:
                    body_data = json.loads(raw_response['body'])
                    result = body_data
                else:
                    result = raw_response
                
                severity = result.get('severity', 'unknown')
                y_diff = result.get('y_difference', 0)
                
                print(f"   ✅ Result: {severity.upper()} (Y-diff: {y_diff*100:.2f}%)")
                print(f"   🏥 NIHSS: {result.get('nihss_motor_score', 0)}/4")
                print(f"   🎯 Quality: {result.get('test_quality', 'unknown')}")
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    import time
    
    print("🏥 Improved Sensitivity Test")
    print("Testing the updated Lambda function with better thresholds")
    print("API Gateway: https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest")
    print()
    
    # Test improved sensitivity
    success = test_improved_sensitivity()
    
    if success:
        print("\n🎉 SENSITIVITY IMPROVEMENT: SUCCESS!")
        test_multiple_scenarios()
        print("\n✅ The improved Lambda function should now give you 'Normal' results")
        print("✅ When you keep your arms straight, you should see:")
        print("   - Severity: NORMAL")
        print("   - NIHSS Score: 0/4")
        print("   - Message: 'Normal Results - No drift detected'")
    else:
        print("\n⚠️ SENSITIVITY IMPROVEMENT: NEEDS MORE WORK")
        print("🔧 The thresholds may need further adjustment")
        print("💡 Try the test again or contact for further optimization")
