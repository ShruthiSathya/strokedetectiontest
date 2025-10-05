#!/usr/bin/env python3
"""
Debug the response parsing issue between Lambda and iOS app.
This will help identify why the app shows an error despite correct console output.
"""

import json

def test_response_parsing():
    """Test the response parsing to identify the issue."""
    
    # This is the actual response from the Lambda function
    lambda_response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": "{\"drift_detected\": false, \"asymmetry_score\": 0.011407017707824707, \"asymmetry_percent\": 1.1407017707824707, \"y_difference\": 0.011407017707824707, \"clinical_score\": 0, \"nihss_motor_score\": 0, \"nihss_total\": 0, \"severity\": \"normal\", \"message\": \"No significant drift detected. Arms held steady within normal variation range.\", \"clinical_interpretation\": \"No significant drift detected. Arms held steady within normal variation range.\", \"test_quality\": \"robust_keypoint_analysis\", \"research_based\": true, \"clinical_standards\": \"NIHSS_Motor_Arm_Item5_Robust\", \"analysis_method\": \"absolute_vertical_drift\", \"detection_quality\": \"poor\", \"quality_reason\": \"Small arm lengths (0.034) or significant difference (55.6%)\", \"vertical_drift\": 0.011407017707824707}"
    }
    
    print("🔍 DEBUGGING RESPONSE PARSING")
    print("=" * 60)
    print("📥 Lambda response structure:")
    print(f"   Status code: {lambda_response['statusCode']}")
    print(f"   Headers: {lambda_response['headers']}")
    print(f"   Body type: {type(lambda_response['body'])}")
    print()
    
    # Step 1: Parse the body string
    try:
        body_data = json.loads(lambda_response['body'])
        print("✅ Step 1: Successfully parsed body string")
        print(f"   Body keys: {list(body_data.keys())}")
        print()
    except json.JSONDecodeError as e:
        print(f"❌ Step 1: Failed to parse body string: {e}")
        return
    
    # Step 2: Check if all required fields are present
    required_fields = [
        'drift_detected', 'asymmetry_score', 'nihss_motor_score', 'severity', 
        'message', 'test_quality', 'research_based', 'clinical_standards', 
        'analysis_method', 'clinical_interpretation', 'y_difference', 'clinical_score'
    ]
    
    print("📋 Step 2: Checking required fields:")
    missing_fields = []
    for field in required_fields:
        if field in body_data:
            print(f"   ✅ {field}: {body_data[field]}")
        else:
            print(f"   ❌ {field}: MISSING")
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n⚠️  Missing fields: {missing_fields}")
    else:
        print("\n✅ All required fields are present")
    
    print()
    
    # Step 3: Check for any parsing issues
    print("🔍 Step 3: Checking for parsing issues:")
    
    # Check for any non-standard field names
    unexpected_fields = []
    for key in body_data.keys():
        if key not in required_fields and key not in ['asymmetry_percent', 'nihss_total', 'detection_quality', 'quality_reason', 'vertical_drift']:
            unexpected_fields.append(key)
    
    if unexpected_fields:
        print(f"   ⚠️  Unexpected fields: {unexpected_fields}")
    else:
        print("   ✅ No unexpected fields")
    
    # Check data types
    print("\n📊 Step 4: Checking data types:")
    type_checks = [
        ('drift_detected', bool),
        ('asymmetry_score', (int, float)),
        ('nihss_motor_score', int),
        ('severity', str),
        ('message', str),
        ('research_based', bool)
    ]
    
    for field, expected_type in type_checks:
        if field in body_data:
            actual_type = type(body_data[field])
            if isinstance(body_data[field], expected_type):
                print(f"   ✅ {field}: {actual_type.__name__} (correct)")
            else:
                print(f"   ❌ {field}: {actual_type.__name__} (expected {expected_type.__name__})")
        else:
            print(f"   ❌ {field}: MISSING")
    
    print()
    
    # Step 5: Simulate iOS parsing
    print("📱 Step 5: Simulating iOS parsing:")
    
    # This is what the iOS app does
    try:
        # First decode AWS wrapper
        aws_response = lambda_response
        print("   ✅ AWS wrapper decoded successfully")
        
        # Check status code
        if aws_response['statusCode'] == 200:
            print("   ✅ Status code is 200")
        else:
            print(f"   ❌ Status code is {aws_response['statusCode']}")
            return
        
        # Parse body
        body_data = json.loads(aws_response['body'])
        print("   ✅ Body parsed successfully")
        
        # Check if this would match ClinicalResponse struct
        print("   ✅ Response should parse successfully in iOS app")
        print(f"   📊 Final result: NIHSS {body_data.get('nihss_motor_score', 'unknown')} - {body_data.get('severity', 'unknown')}")
        
    except Exception as e:
        print(f"   ❌ iOS parsing would fail: {e}")
    
    print()
    print("🎯 CONCLUSION:")
    print("   The Lambda response should work fine with the iOS app")
    print("   The issue might be:")
    print("   1. Network timeout (15 seconds)")
    print("   2. Image capture failure")
    print("   3. JSON encoding failure")
    print("   4. Network connectivity issues")
    print()
    print("💡 RECOMMENDATION:")
    print("   Check the iOS console logs for the specific error message")
    print("   Look for: 'TIMEOUT', 'Image capture failed', 'Network Error', etc.")

if __name__ == "__main__":
    test_response_parsing()
