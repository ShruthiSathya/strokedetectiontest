#!/usr/bin/env python3
"""
Simple threshold testing script
Test different threshold values to find the optimal one
"""

import requests
import json

# AWS Lambda URL
LAMBDA_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

# Test image (minimal PNG)
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_threshold_value(threshold_description, keypoints=8, image_size=500000):
    """
    Test a specific threshold configuration
    """
    print(f"🧪 Testing: {threshold_description}")
    print("-" * 40)
    
    payload = {
        "image_base64": TEST_IMAGE_BASE64,
        "user_id": f"threshold_test",
        "keypoints_detected": keypoints,
        "image_size_bytes": image_size,
        "test_mode": False,
        "force_drift": False,
        "user_intentionally_drifting": False
    }
    
    try:
        response = requests.post(
            LAMBDA_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            body_data = json.loads(result.get('body', '{}'))
            
            print(f"📊 Drift Detected: {body_data.get('drift_detected', False)}")
            print(f"📏 Y-Difference: {body_data.get('y_difference', 0):.4f}")
            print(f"🎯 Severity: {body_data.get('severity', 'unknown')}")
            print(f"📈 Test Quality: {body_data.get('test_quality', 'unknown')}")
            
            return {
                'drift_detected': body_data.get('drift_detected', False),
                'y_difference': body_data.get('y_difference', 0),
                'severity': body_data.get('severity', 'unknown')
            }
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """
    Test different scenarios to understand threshold behavior
    """
    print("🎯 THRESHOLD TESTING TOOL")
    print("=" * 50)
    print("This tool tests how the current threshold behaves")
    print()
    
    # Test scenarios
    scenarios = [
        ("Real Camera Image (526KB)", 8, 526713),
        ("Large Image (1MB)", 8, 1000000),
        ("Small Image (50KB)", 8, 50000),
        ("Perfect Calibration (10 keypoints)", 10, 500000),
        ("Good Calibration (6 keypoints)", 6, 500000),
        ("Poor Calibration (3 keypoints)", 3, 500000),
    ]
    
    results = []
    
    for description, keypoints, image_size in scenarios:
        result = test_threshold_value(description, keypoints, image_size)
        if result:
            results.append((description, result))
        print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 20)
    
    for description, result in results:
        status = "✅ Drift" if result['drift_detected'] else "❌ No Drift"
        print(f"{description}: {status} (Y-diff: {result['y_difference']:.4f})")
    
    print()
    print("💡 THRESHOLD INSIGHTS:")
    print("- Current threshold: 0.01 (1%)")
    print("- Test image asymmetry: ~0.241 (24.1%)")
    print("- Your real camera asymmetry: ~0.003 (0.3%)")
    print()
    print("🔧 RECOMMENDED ADJUSTMENTS:")
    print("1. For your real camera (0.003 asymmetry):")
    print("   - Try threshold: 0.005 (0.5%)")
    print("   - This should detect drift when asymmetry > 0.5%")
    print()
    print("2. For test images (0.241 asymmetry):")
    print("   - Current threshold works fine")
    print("   - Will detect drift since 24.1% > 1%")
    print()
    print("3. To modify threshold:")
    print("   - Edit lambda_with_rekognition.py line 331")
    print("   - Change: image_drift_threshold = 0.005")
    print("   - Test with your real camera images")

if __name__ == "__main__":
    main()
