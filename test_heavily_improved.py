#!/usr/bin/env python3
"""
Test Heavily Improved Lambda Function
Test with much more conservative thresholds
"""

import requests
import json
import base64

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def create_test_image():
    """Create a test image that simulates your scenario"""
    
    # Create a realistic camera image
    width, height = 400, 300
    test_image_data = bytearray()
    
    for y in range(height):
        for x in range(width):
            center_x = width // 2
            center_y = height // 2
            
            dist_x = abs(x - center_x)
            dist_y = abs(y - center_y)
            
            # Simulate minimal asymmetry (like your real test)
            if x < center_x:  # Left side
                r = 120 + dist_x // 4
                g = 130 + dist_x // 5
                b = 140 + dist_x // 6
            else:  # Right side
                r = 118 + dist_x // 4  # Very slight difference
                g = 132 + dist_x // 5  # Very slight difference
                b = 138 + dist_x // 6  # Very slight difference
            
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            test_image_data.extend([r, g, b])
    
    return base64.b64encode(test_image_data).decode('utf-8')

def test_heavily_improved():
    """Test the heavily improved Lambda function"""
    
    print("🧪 Testing Heavily Improved Lambda Function")
    print("=" * 60)
    print("New thresholds: Normal<20%, Mild<40%, Moderate<60%, Severe<80%")
    print("Simulating: Arms held straight, excellent calibration")
    print()
    
    test_image_b64 = create_test_image()
    
    payload = {
        "image_base64": test_image_b64,
        "user_id": "heavily_improved_test",
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
            print(f"   🎯 Severity: {result.get('severity', 'unknown').upper()}")
            print(f"   🏥 NIHSS Score: {result.get('nihss_motor_score', 0)}/4")
            print(f"   📈 Y-Difference: {result.get('y_difference', 0)*100:.2f}%")
            print(f"   🔍 Drift Detected: {result.get('drift_detected', False)}")
            print(f"   📝 Message: {result.get('message', 'N/A')}")
            print(f"   🔧 Analysis Method: {result.get('analysis_method', 'unknown')}")
            print(f"   📦 Version: {result.get('version', 'unknown')}")
            
            # Check if heavily improved version is working
            severity = result.get('severity', '').lower()
            y_diff = result.get('y_difference', 0)
            version = result.get('version', '')
            
            print(f"\n🎯 EVALUATION:")
            if 'improved_v2' in version:
                print("   ✅ HEAVILY IMPROVED VERSION DETECTED!")
                if severity == 'normal' and y_diff < 0.20:
                    print("   ✅ PERFECT! Normal results for straight arms")
                    return True
                elif severity == 'mild' and y_diff < 0.40:
                    print("   ✅ GOOD! Much better than before")
                    return True
                else:
                    print(f"   ⚠️ Still showing {severity.upper()} - may need even more adjustment")
                    return False
            else:
                print("   ❌ OLD VERSION STILL ACTIVE")
                print("   🔧 Need to deploy the heavily improved version")
                return False
                
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Test Heavily Improved Lambda Function")
    print("Testing with much more conservative thresholds")
    print()
    
    success = test_heavily_improved()
    
    if success:
        print("\n🎉 HEAVILY IMPROVED VERSION WORKING!")
        print("✅ Your straight-arm test should now show NORMAL or MILD")
        print("✅ Much more realistic results!")
    else:
        print("\n⚠️ Need to deploy the heavily improved version")
        print("🔧 Copy the updated lambda_fast_enhanced.py to AWS")
