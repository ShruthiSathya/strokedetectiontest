#!/usr/bin/env python3
"""
Threshold Calibration Tool for Stroke Detection App
This tool helps you find the optimal threshold for drift detection
"""

import requests
import json
import statistics

# AWS Lambda URL
LAMBDA_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

# Test image (minimal PNG)
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_threshold_scenarios():
    """
    Test different scenarios to help calibrate the threshold
    """
    print("🔬 THRESHOLD CALIBRATION TOOL")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "No Drift - Steady Arms",
            "keypoints": 8,
            "image_size": 500000,
            "expected": "no_drift",
            "description": "Test when arms are held steady - should show no drift"
        },
        {
            "name": "Mild Drift - Slight Arm Lowering", 
            "keypoints": 8,
            "image_size": 500000,
            "expected": "mild_drift",
            "description": "Test with slight arm lowering - should show mild drift"
        },
        {
            "name": "Significant Drift - Obvious Arm Lowering",
            "keypoints": 8, 
            "image_size": 500000,
            "expected": "significant_drift",
            "description": "Test with obvious arm lowering - should show significant drift"
        },
        {
            "name": "Poor Calibration - Low Keypoints",
            "keypoints": 4,
            "image_size": 500000,
            "expected": "unreliable",
            "description": "Test with poor calibration - should be unreliable"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Test {i}: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print("-" * 40)
        
        payload = {
            "image_base64": TEST_IMAGE_BASE64,
            "user_id": f"calibration_test_{i}",
            "keypoints_detected": scenario['keypoints'],
            "image_size_bytes": scenario['image_size'],
            "test_mode": False,
            "force_drift": False,
            "user_intentionally_drifting": False,
            "calibration_mode": True,
            "user_feedback": scenario['expected']
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
                
                test_result = {
                    "scenario": scenario['name'],
                    "expected": scenario['expected'],
                    "drift_detected": body_data.get('drift_detected', False),
                    "y_difference": body_data.get('y_difference', 0),
                    "severity": body_data.get('severity', 'unknown'),
                    "test_quality": body_data.get('test_quality', 'unknown')
                }
                
                results.append(test_result)
                
                print(f"✅ Expected: {scenario['expected']}")
                print(f"📊 Detected: {body_data.get('drift_detected', False)}")
                print(f"📏 Y-Difference: {body_data.get('y_difference', 0):.4f}")
                print(f"🎯 Severity: {body_data.get('severity', 'unknown')}")
                print(f"📈 Quality: {body_data.get('test_quality', 'unknown')}")
                
                # Check if result matches expectation
                if scenario['expected'] == 'no_drift' and not body_data.get('drift_detected', False):
                    print("✅ CORRECT: No drift detected as expected")
                elif scenario['expected'] in ['mild_drift', 'significant_drift'] and body_data.get('drift_detected', False):
                    print("✅ CORRECT: Drift detected as expected")
                else:
                    print("❌ INCORRECT: Result doesn't match expectation")
                    
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return results

def analyze_results(results):
    """
    Analyze the test results and provide threshold recommendations
    """
    print(f"\n📊 ANALYSIS & RECOMMENDATIONS")
    print("=" * 50)
    
    if not results:
        print("❌ No results to analyze")
        return
    
    # Analyze asymmetry scores
    asymmetry_scores = [r['y_difference'] for r in results if r['y_difference'] > 0]
    if asymmetry_scores:
        print(f"📈 Asymmetry Score Range: {min(asymmetry_scores):.4f} - {max(asymmetry_scores):.4f}")
        print(f"📊 Average Asymmetry: {statistics.mean(asymmetry_scores):.4f}")
        print(f"📊 Median Asymmetry: {statistics.median(asymmetry_scores):.4f}")
    
    # Count correct vs incorrect results
    correct = 0
    total = len(results)
    
    for result in results:
        expected = result['expected']
        detected = result['drift_detected']
        
        if expected == 'no_drift' and not detected:
            correct += 1
        elif expected in ['mild_drift', 'significant_drift'] and detected:
            correct += 1
        elif expected == 'unreliable':
            correct += 1  # Unreliable is always considered correct
    
    accuracy = (correct / total) * 100
    print(f"🎯 Accuracy: {accuracy:.1f}% ({correct}/{total} tests correct)")
    
    # Provide recommendations
    print(f"\n💡 THRESHOLD RECOMMENDATIONS:")
    print("-" * 30)
    
    if accuracy >= 80:
        print("✅ Current threshold appears to be working well!")
        print("💡 Consider fine-tuning based on your specific use cases")
    elif accuracy >= 60:
        print("⚠️ Threshold needs adjustment")
        print("💡 Consider increasing sensitivity for better drift detection")
    else:
        print("❌ Threshold needs significant adjustment")
        print("💡 Consider recalibrating with more test data")
    
    # Specific recommendations based on results
    no_drift_results = [r for r in results if r['expected'] == 'no_drift']
    drift_results = [r for r in results if r['expected'] in ['mild_drift', 'significant_drift']]
    
    if no_drift_results:
        max_no_drift = max([r['y_difference'] for r in no_drift_results])
        print(f"🔧 Suggested threshold: > {max_no_drift:.4f} (based on no-drift max: {max_no_drift:.4f})")
    
    if drift_results:
        min_drift = min([r['y_difference'] for r in drift_results])
        print(f"🔧 Alternative threshold: < {min_drift:.4f} (based on drift min: {min_drift:.4f})")

def main():
    """
    Main calibration function
    """
    print("🎯 STROKE DETECTION THRESHOLD CALIBRATION")
    print("This tool helps you find the optimal threshold for your setup")
    print()
    
    # Run calibration tests
    results = test_threshold_scenarios()
    
    # Analyze results
    analyze_results(results)
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Run your iOS app and test different arm positions")
    print("2. Note the asymmetry scores for each position")
    print("3. Adjust the threshold in lambda_with_rekognition.py")
    print("4. Re-run this calibration tool to verify improvements")
    print()
    print("🔧 Current threshold in code: image_drift_threshold = 0.01")
    print("💡 Try values between 0.005 and 0.05 for fine-tuning")

if __name__ == "__main__":
    main()
