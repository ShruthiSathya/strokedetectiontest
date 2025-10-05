#!/usr/bin/env python3
"""
Verify Fix - Test the improved Lambda function
"""

import requests
import json
import base64

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def test_your_scenario():
    """Test your exact scenario with improved function"""
    
    print("🧪 Testing Your Exact Scenario")
    print("=" * 50)
    print("Simulating: Arms held straight, excellent calibration")
    print()
    
    # Create test image with minimal asymmetry (like your real test)
    test_image_b64 = create_minimal_asymmetry_image()
    
    payload = {
        "image_base64": test_image_b64,
        "user_id": "your_test_scenario",
        "keypoints_detected": 10,  # Excellent calibration like yours
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
            print(f"   Message: {result.get('message', 'N/A')}")
            
            # Check if fix worked
            severity = result.get('severity', '').lower()
            if severity == 'normal' and not result.get('drift_detected', True):
                print("\n✅ FIX WORKING! Should show NORMAL for your test")
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

def create_minimal_asymmetry_image():
    """Create image with minimal asymmetry like your real test"""
    
    # Create realistic camera image
    width, height = 400, 300
    test_image_data = bytearray()
    
    for y in range(height):
        for x in range(width):
            center_x = width // 2
            center_y = height // 2
            
            dist_x = abs(x - center_x)
            dist_y = abs(y - center_y)
            
            # Minimal asymmetry (like your 3.16% result)
            if x < center_x:  # Left side
                r = 120 + dist_x // 4
                g = 130 + dist_x // 5
                b = 140 + dist_x // 6
            else:  # Right side
                r = 119 + dist_x // 4  # 1 pixel difference
                g = 131 + dist_x // 5  # 1 pixel difference
                b = 139 + dist_x // 6  # 1 pixel difference
            
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            test_image_data.extend([r, g, b])
    
    return base64.b64encode(test_image_data).decode('utf-8')

if __name__ == "__main__":
    print("🏥 Verify Fix - Test Improved Lambda Function")
    print("Testing if your scenario now shows NORMAL results")
    print()
    
    success = test_your_scenario()
    
    if success:
        print("\n🎉 SUCCESS! The fix is working!")
        print("Your straight-arm test should now show NORMAL results")
    else:
        print("\n⚠️ The improved function may not be deployed yet")
        print("Follow the deployment guide to update the Lambda function")
        print("Then run this test again to verify the fix")
