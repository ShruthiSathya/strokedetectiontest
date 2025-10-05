#!/usr/bin/env python3
"""
Debug the exact Lambda response format to fix the parsing issue.
"""

import json
import requests

def debug_lambda_response():
    """Debug the exact Lambda response format."""
    
    # Test payload
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
    
    print("🔍 DEBUGGING LAMBDA RESPONSE FORMAT")
    print("=" * 60)
    
    API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"
    
    try:
        response = requests.post(
            API_GATEWAY_URL,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status code: {response.status_code}")
        print(f"📄 Raw response text:")
        print(response.text)
        print()
        
        # Try to parse the response
        try:
            response_json = response.json()
            print("✅ Response is valid JSON")
            print(f"📋 Response keys: {list(response_json.keys())}")
            print()
            
            # Check if it's wrapped in AWS format
            if 'body' in response_json:
                print("🔍 Response is wrapped in AWS API Gateway format")
                print(f"   Status code: {response_json.get('statusCode')}")
                print(f"   Headers: {response_json.get('headers')}")
                print(f"   Body type: {type(response_json.get('body'))}")
                print()
                
                # Parse the body
                body_text = response_json['body']
                print(f"📄 Body content: {body_text}")
                print()
                
                try:
                    body_json = json.loads(body_text)
                    print("✅ Body is valid JSON")
                    print(f"📋 Body keys: {list(body_json.keys())}")
                    print()
                    
                    # Check the actual clinical data
                    print("🏥 CLINICAL DATA:")
                    print(f"   Drift detected: {body_json.get('drift_detected')}")
                    print(f"   Asymmetry: {body_json.get('asymmetry_percent')}%")
                    print(f"   NIHSS score: {body_json.get('nihss_motor_score')}")
                    print(f"   Severity: {body_json.get('severity')}")
                    print(f"   Analysis method: {body_json.get('analysis_method')}")
                    print(f"   Detection quality: {body_json.get('detection_quality')}")
                    print()
                    
                    # Check if this is the robust Lambda function
                    if body_json.get('analysis_method') == 'absolute_vertical_drift':
                        print("🎉 SUCCESS: Robust Lambda function is working!")
                        print("   The issue is in the iOS response parsing")
                    else:
                        print("⚠️  WARNING: This might not be the robust Lambda function")
                        print(f"   Expected analysis_method: 'absolute_vertical_drift'")
                        print(f"   Actual analysis_method: '{body_json.get('analysis_method')}'")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Body is not valid JSON: {e}")
            else:
                print("🔍 Response is direct JSON (not wrapped)")
                print("🏥 CLINICAL DATA:")
                print(f"   Drift detected: {response_json.get('drift_detected')}")
                print(f"   Asymmetry: {response_json.get('asymmetry_percent')}%")
                print(f"   NIHSS score: {response_json.get('nihss_motor_score')}")
                print(f"   Severity: {response_json.get('severity')}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Response is not valid JSON: {e}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    debug_lambda_response()
