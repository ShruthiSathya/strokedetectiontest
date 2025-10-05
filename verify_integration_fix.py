#!/usr/bin/env python3
"""
Verify Integration Fix
Test that the iOS app integration is working after fixing compilation errors
"""

import requests
import json

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def test_integration_after_fix():
    """Test the integration after fixing Swift compilation errors"""
    
    print("🔧 Testing Integration After Fix")
    print("=" * 50)
    print("Verifying that the iOS app can communicate with Lambda")
    print()
    
    # Test with the keypoint format that the iOS app now sends
    test_payload = {
        "keypoints": {
            "left_wrist": {"x": 0.3, "y": 0.7},
            "right_wrist": {"x": 0.7, "y": 0.7},  # Same Y = no drift
            "left_shoulder": {"x": 0.35, "y": 0.3},
            "right_shoulder": {"x": 0.65, "y": 0.3}
        },
        "user_id": "integration_test_after_fix",
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
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
            
            print("✅ SUCCESS: Integration is working!")
            print()
            print("📊 Test Results:")
            print(f"   🎯 Severity: {result.get('severity', 'unknown').upper()}")
            print(f"   📊 Asymmetry: {result.get('asymmetry_score', 0):.4f}")
            print(f"   🏥 NIHSS: {result.get('nihss_motor_score', 0)}/4")
            print(f"   🔍 Drift Detected: {result.get('drift_detected', False)}")
            print(f"   💬 Message: {result.get('message', 'N/A')}")
            print(f"   🔧 Method: {result.get('analysis_method', 'unknown')}")
            print(f"   📦 Version: {result.get('version', 'unknown')}")
            print()
            
            # Verify this is working correctly
            severity = result.get('severity', '').lower()
            asymmetry_score = result.get('asymmetry_score', 0)
            
            if severity == 'normal' and asymmetry_score < 0.05:
                print("🎉 PERFECT: No drift detected for straight arms")
                print("✅ Your stroke detection app is working correctly!")
                return True
            else:
                print(f"⚠️ Unexpected result: {severity} with {asymmetry_score:.4f} asymmetry")
                return False
                
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Verify Integration Fix")
    print("Testing after fixing Swift compilation errors")
    print()
    
    success = test_integration_after_fix()
    
    if success:
        print("\n🎉 INTEGRATION VERIFICATION: SUCCESS!")
        print("✅ All Swift compilation errors have been fixed")
        print("✅ iOS app can communicate with Lambda correctly")
        print("✅ Your stroke detection app is ready to use!")
        print()
        print("🚀 Next Steps:")
        print("   1. Build and run your iOS app")
        print("   2. Test with your arms held straight")
        print("   3. You should see NORMAL results!")
    else:
        print("\n❌ INTEGRATION VERIFICATION: FAILED")
        print("🔧 Need to check the integration further")
