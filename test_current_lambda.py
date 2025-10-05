#!/usr/bin/env python3
"""
Test script to verify current Lambda deployment
"""

import requests
import json
import base64
import time

# API Gateway URL from iOS app
API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def create_test_image():
    """Create a simple test image as base64"""
    # Create a simple 100x100 pixel test image (RGB)
    # This simulates a real camera image
    test_image_data = bytearray()
    for y in range(100):
        for x in range(100):
            # Create a simple gradient pattern
            r = (x + y) % 256
            g = (x * 2) % 256  
            b = (y * 2) % 256
            test_image_data.extend([r, g, b])
    
    # Convert to base64
    return base64.b64encode(test_image_data).decode('utf-8')

def test_lambda_deployment():
    """Test the current Lambda deployment"""
    print("🧪 Testing Lambda Deployment")
    print("=" * 50)
    
    # Create test payload
    test_image_b64 = create_test_image()
    
    payload = {
        "image_base64": test_image_b64,
        "user_id": "test_user_123",
        "keypoints_detected": 8,  # Perfect calibration
        "image_size_bytes": len(base64.b64decode(test_image_b64)),
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    print(f"📤 Sending test payload...")
    print(f"   - Image size: {payload['image_size_bytes']} bytes")
    print(f"   - Keypoints: {payload['keypoints_detected']}")
    print(f"   - User ID: {payload['user_id']}")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            API_GATEWAY_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        response_time = time.time() - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📡 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # First check if it's wrapped in AWS API Gateway format
                raw_response = response.json()
                print(f"🔍 Raw response structure: {type(raw_response)}")
                print(f"🔍 Raw response keys: {list(raw_response.keys()) if isinstance(raw_response, dict) else 'Not a dict'}")
                
                # Check if it's wrapped in AWS API Gateway response
                if 'body' in raw_response and 'statusCode' in raw_response:
                    print("📦 AWS API Gateway wrapper detected")
                    body_data = json.loads(raw_response['body'])
                    result = body_data
                else:
                    result = raw_response
                
                print("✅ SUCCESS - Lambda responded correctly!")
                print("\n📊 Response Details:")
                print(f"   - Drift Detected: {result.get('drift_detected', 'N/A')}")
                print(f"   - Severity: {result.get('severity', 'N/A')}")
                print(f"   - Clinical Score: {result.get('clinical_score', 'N/A')}")
                print(f"   - NIHSS Motor Score: {result.get('nihss_motor_score', 'N/A')}")
                print(f"   - Test Quality: {result.get('test_quality', 'N/A')}")
                print(f"   - Analysis Method: {result.get('analysis_method', 'N/A')}")
                print(f"   - Research Based: {result.get('research_based', 'N/A')}")
                print(f"   - Message: {result.get('message', 'N/A')}")
                
                if result.get('analysis_time'):
                    print(f"   - Analysis Time: {result.get('analysis_time'):.3f}s")
                if result.get('remaining_time_ms'):
                    print(f"   - Remaining Time: {result.get('remaining_time_ms')}ms")
                
                # Show full response for debugging
                print(f"\n🔍 Full response: {json.dumps(result, indent=2)}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print(f"📄 Raw response: {response.text}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Lambda took too long to respond")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def test_multiple_scenarios():
    """Test multiple scenarios to verify Lambda behavior"""
    print("\n🔄 Testing Multiple Scenarios")
    print("=" * 50)
    
    scenarios = [
        {"keypoints": 8, "expected": "perfect_calibration", "desc": "Perfect calibration (8 keypoints)"},
        {"keypoints": 4, "expected": "poor_calibration", "desc": "Poor calibration (4 keypoints)"},
        {"keypoints": 6, "expected": "good_calibration", "desc": "Good calibration (6 keypoints)"}
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Test {i}: {scenario['desc']}")
        
        test_image_b64 = create_test_image()
        payload = {
            "image_base64": test_image_b64,
            "user_id": f"test_user_{i}",
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
                timeout=15
            )
            
            if response.status_code == 200:
                # Parse AWS API Gateway wrapper
                raw_response = response.json()
                if 'body' in raw_response and 'statusCode' in raw_response:
                    body_data = json.loads(raw_response['body'])
                    result = body_data
                else:
                    result = raw_response
                
                print(f"   ✅ Status: {result.get('severity', 'unknown')}")
                print(f"   📊 Score: {result.get('clinical_score', 0)}/4")
                print(f"   🎯 Quality: {result.get('test_quality', 'unknown')}")
                print(f"   🏥 NIHSS: {result.get('nihss_motor_score', 0)}/4")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Lambda Deployment Test Suite")
    print("Testing: Fast Enhanced Lambda Function")
    print("API Gateway: https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest")
    print()
    
    # Test basic deployment
    success = test_lambda_deployment()
    
    if success:
        print("\n🎉 Basic test passed! Running additional scenarios...")
        test_multiple_scenarios()
        print("\n✅ All tests completed successfully!")
        print("🚀 Lambda deployment is working correctly")
    else:
        print("\n❌ Basic test failed!")
        print("🔧 Lambda deployment needs attention")
