#!/usr/bin/env python3
"""
Test the AWS fix to ensure the iOS app can now parse the Lambda response correctly.
"""

import json
import requests

def test_aws_fix():
    """Test that the AWS integration now works correctly."""
    
    # Test payload with your actual data
    test_payload = {
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
    
    print("🔧 TESTING AWS FIX")
    print("=" * 60)
    print("📤 Testing with your actual keypoint data...")
    print()
    
    API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the AWS-wrapped response
            aws_response = response.json()
            body_json = json.loads(aws_response['body'])
            
            print("✅ AWS Lambda response received successfully!")
            print()
            print("🏥 CLINICAL RESULTS:")
            print(f"   Drift detected: {body_json.get('drift_detected')}")
            print(f"   Asymmetry: {body_json.get('asymmetry_percent'):.1f}%")
            print(f"   NIHSS score: {body_json.get('nihss_motor_score')}")
            print(f"   Severity: {body_json.get('severity')}")
            print(f"   Analysis method: {body_json.get('analysis_method')}")
            print(f"   Detection quality: {body_json.get('detection_quality')}")
            print()
            
            # Check if this matches what the iOS app expects
            required_fields = [
                'drift_detected', 'asymmetry_score', 'nihss_motor_score', 'severity', 
                'message', 'test_quality', 'research_based', 'clinical_standards', 
                'analysis_method', 'clinical_interpretation', 'y_difference', 'clinical_score',
                'asymmetry_percent', 'nihss_total', 'detection_quality', 'quality_reason', 'vertical_drift'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in body_json:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                print("   The iOS app will still fail to parse this response")
            else:
                print("✅ All required fields are present!")
                print("   The iOS app should now be able to parse this response correctly")
            
            # Verify the robust Lambda function is working
            if body_json.get('analysis_method') == 'absolute_vertical_drift':
                print("✅ Robust Lambda function is active and working correctly")
            else:
                print("⚠️  The robust Lambda function might not be deployed")
                print(f"   Expected analysis_method: 'absolute_vertical_drift'")
                print(f"   Actual analysis_method: '{body_json.get('analysis_method')}'")
            
        else:
            print(f"❌ AWS Lambda returned error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ AWS Lambda timed out")
        print("   This should trigger the fallback system in the iOS app")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_drift_scenario():
    """Test with a scenario that should show drift."""
    
    print("\n🧪 TESTING DRIFT SCENARIO")
    print("=" * 60)
    
    # Create a payload that should show drift
    drift_payload = {
        "keypoints": {
            "left_wrist": {"x": 0.5, "y": 0.3},    # Much higher
            "left_shoulder": {"x": 0.5, "y": 0.5},
            "right_wrist": {"x": 0.5, "y": 0.7},   # Much lower (significant drift)
            "right_shoulder": {"x": 0.5, "y": 0.5}
        },
        "user_id": "test_user",
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    print("📤 Testing with significant drift scenario...")
    print("   Left wrist: (0.5, 0.3) - much higher")
    print("   Right wrist: (0.5, 0.7) - much lower")
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
            aws_response = response.json()
            body_json = json.loads(aws_response['body'])
            
            print("✅ Drift scenario test successful!")
            print(f"   Drift detected: {body_json.get('drift_detected')}")
            print(f"   Asymmetry: {body_json.get('asymmetry_percent'):.1f}%")
            print(f"   NIHSS score: {body_json.get('nihss_motor_score')}")
            print(f"   Severity: {body_json.get('severity')}")
            
            if body_json.get('drift_detected'):
                print("   🎯 Correctly detected drift!")
            else:
                print("   ⚠️  Did not detect drift - might need threshold adjustment")
        else:
            print(f"❌ Drift scenario test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Drift scenario test error: {e}")

def provide_summary():
    """Provide a summary of the fixes applied."""
    
    print("\n📋 AWS FIX SUMMARY")
    print("=" * 60)
    print("✅ FIXES APPLIED:")
    print("   1. Added missing fields to ClinicalResponse struct:")
    print("      - asymmetry_percent")
    print("      - nihss_total")
    print("      - detection_quality")
    print("      - quality_reason")
    print("      - vertical_drift")
    print()
    print("   2. Increased timeout from 15 to 30 seconds")
    print("   3. Updated network request timeout to 25 seconds")
    print("   4. Fixed fallback response creation")
    print()
    print("🎯 EXPECTED RESULTS:")
    print("   - AWS calls should now work correctly")
    print("   - No more response parsing errors")
    print("   - Correct NIHSS 0 (Normal) for straight arms")
    print("   - Correct drift detection when arms actually drift")
    print("   - Fallback system as backup if AWS fails")
    print()
    print("🚀 NEXT STEPS:")
    print("   1. Test the app with straight arms → Should show NIHSS 0 (Normal)")
    print("   2. Test with actual drift → Should detect and show appropriate NIHSS score")
    print("   3. Test with poor network → Should use fallback system")

if __name__ == "__main__":
    test_aws_fix()
    test_drift_scenario()
    provide_summary()
