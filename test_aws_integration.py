#!/usr/bin/env python3
"""
Test the AWS integration to fix the connection issue.
This will help identify why the app shows error even when Lambda is deployed.
"""

import json
import requests
import time

def test_aws_integration():
    """Test the AWS integration with the exact payload format the iOS app sends."""
    
    # This is the exact payload format your iOS app sends
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
    
    print("🔍 TESTING AWS INTEGRATION")
    print("=" * 60)
    print("📤 Sending exact iOS payload format to AWS Lambda...")
    print(f"   Payload keys: {list(ios_payload.keys())}")
    print(f"   Keypoints: {list(ios_payload['keypoints'].keys())}")
    print()
    
    API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"
    
    print(f"🌐 Testing URL: {API_GATEWAY_URL}")
    print("⏱️  Testing with 30-second timeout...")
    print()
    
    try:
        start_time = time.time()
        response = requests.post(
            API_GATEWAY_URL,
            json=ios_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30  # 30-second timeout
        )
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"📡 Response received in {response_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Lambda function responded successfully!")
                print(f"   Drift detected: {result.get('drift_detected', 'unknown')}")
                print(f"   Asymmetry: {result.get('asymmetry_percent', 'unknown')}%")
                print(f"   NIHSS score: {result.get('nihss_motor_score', 'unknown')}")
                print(f"   Severity: {result.get('severity', 'unknown')}")
                print(f"   Analysis method: {result.get('analysis_method', 'unknown')}")
                print(f"   Detection quality: {result.get('detection_quality', 'unknown')}")
                print()
                
                # Check if this is the robust Lambda function
                if result.get('analysis_method') == 'absolute_vertical_drift':
                    print("🎉 SUCCESS: Robust Lambda function is deployed and working!")
                    print("   The app should now work correctly with AWS.")
                else:
                    print("⚠️  WARNING: This might not be the robust Lambda function")
                    print("   The analysis_method should be 'absolute_vertical_drift'")
                
            except json.JSONDecodeError as e:
                print(f"❌ Lambda responded but with invalid JSON: {e}")
                print(f"📄 Raw response: {response.text}")
        else:
            print(f"❌ Lambda function returned error status: {response.status_code}")
            print(f"📄 Response body: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Lambda function timed out after 30 seconds")
        print("   This explains why the iOS app shows timeout error")
        print("   The Lambda function is taking too long to respond")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("   This could be a network issue or AWS is down")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    
    print()
    print("🔍 DIAGNOSIS:")
    if response_time > 15:
        print("   ⚠️  Lambda is too slow (>15 seconds)")
        print("   💡 Solution: Optimize Lambda function or increase iOS timeout")
    elif response.status_code != 200:
        print("   ⚠️  Lambda is returning error status")
        print("   💡 Solution: Check Lambda function logs for errors")
    else:
        print("   ✅ Lambda is working correctly")
        print("   💡 The issue might be in the iOS app's response parsing")

def test_with_drift_scenario():
    """Test with a scenario that should show drift."""
    
    print("\n🧪 TESTING WITH DRIFT SCENARIO")
    print("=" * 60)
    
    # Create a payload that should show drift
    drift_payload = {
        "keypoints": {
            "left_wrist": {"x": 0.5, "y": 0.4},    # Higher position
            "left_shoulder": {"x": 0.5, "y": 0.5},
            "right_wrist": {"x": 0.5, "y": 0.6},   # Lower position (drift)
            "right_shoulder": {"x": 0.5, "y": 0.5}
        },
        "user_id": "test_user",
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    print("📤 Testing with intentional drift scenario...")
    print("   Left wrist: (0.5, 0.4) - higher")
    print("   Right wrist: (0.5, 0.6) - lower (should show drift)")
    print()
    
    API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json=drift_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Drift scenario test successful!")
            print(f"   Drift detected: {result.get('drift_detected', 'unknown')}")
            print(f"   Asymmetry: {result.get('asymmetry_percent', 'unknown')}%")
            print(f"   NIHSS score: {result.get('nihss_motor_score', 'unknown')}")
            print(f"   Severity: {result.get('severity', 'unknown')}")
            
            if result.get('drift_detected'):
                print("   🎯 Correctly detected drift!")
            else:
                print("   ⚠️  Did not detect drift - might need threshold adjustment")
        else:
            print(f"❌ Drift scenario test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Drift scenario test error: {e}")

def provide_solutions():
    """Provide solutions based on the test results."""
    
    print("\n💡 SOLUTIONS TO FIX AWS INTEGRATION")
    print("=" * 60)
    
    print("1. 🚀 DEPLOY ROBUST LAMBDA FUNCTION:")
    print("   - Make sure lambda_robust_asymmetry.py is deployed")
    print("   - Check that it's the active version")
    print("   - Verify the function name matches the API Gateway")
    print()
    
    print("2. ⏱️  INCREASE iOS TIMEOUT:")
    print("   - Current timeout: 15 seconds")
    print("   - Suggested timeout: 30 seconds")
    print("   - This gives Lambda more time to respond")
    print()
    
    print("3. 🔍 CHECK LAMBDA LOGS:")
    print("   - Go to AWS CloudWatch Logs")
    print("   - Look for your Lambda function logs")
    print("   - Check for any errors or performance issues")
    print()
    
    print("4. 🌐 VERIFY API GATEWAY:")
    print("   - Check API Gateway configuration")
    print("   - Ensure CORS is enabled")
    print("   - Verify the endpoint URL is correct")
    print()
    
    print("5. 📱 iOS APP DEBUGGING:")
    print("   - Check iOS console for specific error messages")
    print("   - Look for network errors, timeouts, or parsing errors")
    print("   - The fallback system will still work as backup")

if __name__ == "__main__":
    test_aws_integration()
    test_with_drift_scenario()
    provide_solutions()
