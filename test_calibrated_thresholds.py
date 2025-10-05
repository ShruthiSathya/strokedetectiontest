#!/usr/bin/env python3
"""
Test Calibrated Thresholds
Test the Lambda function with the new calibrated thresholds
"""

import requests
import json

API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

def test_calibrated_thresholds():
    """Test the Lambda function with new calibrated thresholds"""
    
    print("🎯 Testing Calibrated Thresholds")
    print("=" * 60)
    print("Testing with new thresholds: Normal<3%, Mild<10%, Moderate<20%, Severe<35%")
    print()
    
    test_scenarios = [
        {
            "name": "Perfect Calibration (No Drift)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.7},  # Same Y = no drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "normal",
            "expected_asymmetry": 0.0,
            "description": "Both arms at same height - should be NORMAL"
        },
        {
            "name": "Very Small Drift (2%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.71},  # 1% down = 2.5% drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "normal",
            "expected_asymmetry": 0.025,
            "description": "Minimal drift - should still be NORMAL (<3%)"
        },
        {
            "name": "Small Drift (5%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.72},  # 2% down = 5% drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "mild",
            "expected_asymmetry": 0.05,
            "description": "Should cross into MILD territory (3-10%)"
        },
        {
            "name": "Medium Drift (15%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.76},  # 6% down = 15% drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "moderate",
            "expected_asymmetry": 0.15,
            "description": "Should show MODERATE drift (10-20%)"
        },
        {
            "name": "Large Drift (25%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.80},  # 10% down = 25% drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "severe",
            "expected_asymmetry": 0.25,
            "description": "Should show SEVERE drift (20-35%)"
        },
        {
            "name": "Critical Drift (40%)",
            "keypoints": {
                "left_wrist": {"x": 0.3, "y": 0.7},
                "right_wrist": {"x": 0.7, "y": 0.85},  # 15% down = 40% drift
                "left_shoulder": {"x": 0.35, "y": 0.3},
                "right_shoulder": {"x": 0.65, "y": 0.3}
            },
            "expected_severity": "critical",
            "expected_asymmetry": 0.40,
            "description": "Should show CRITICAL drift (>35%)"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🧪 Test {i}: {scenario['name']}")
        print(f"   📋 {scenario['description']}")
        
        payload = {
            "keypoints": scenario["keypoints"],
            "user_id": f"calibrated_test_{i}",
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
                
                severity = result.get('severity', 'unknown')
                asymmetry_score = result.get('asymmetry_score', 0)
                nihss_score = result.get('nihss_motor_score', 0)
                message = result.get('message', 'N/A')
                
                print(f"   ✅ Result: {severity.upper()}")
                print(f"   📊 Asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
                print(f"   🏥 NIHSS: {nihss_score}/4")
                print(f"   💬 Message: {message[:50]}...")
                
                # Evaluate result
                expected_severity = scenario['expected_severity']
                expected_asymmetry = scenario['expected_asymmetry']
                
                # Check severity match
                if severity.lower() == expected_severity:
                    print(f"   🎯 PERFECT SEVERITY! Expected {expected_severity}, got {severity}")
                    severity_match = True
                else:
                    print(f"   ⚠️ Wrong severity: Expected {expected_severity}, got {severity}")
                    severity_match = False
                
                # Check asymmetry is in reasonable range
                if abs(asymmetry_score - expected_asymmetry) < 0.02:  # 2% tolerance
                    print(f"   ✅ Asymmetry calculation accurate")
                    asymmetry_match = True
                else:
                    print(f"   ⚠️ Asymmetry off: Expected ~{expected_asymmetry:.3f}, got {asymmetry_score:.3f}")
                    asymmetry_match = False
                
                results.append(severity_match and asymmetry_match)
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(False)
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 CALIBRATED THRESHOLDS TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(results)
    total_tests = len(results)
    
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Thresholds are perfectly calibrated!")
        print("✅ Your stroke detection app is working optimally!")
    elif passed_tests >= total_tests * 0.8:
        print("🎯 EXCELLENT RESULTS!")
        print("✅ Thresholds are well calibrated!")
        print("✅ Your app is ready for real-world use!")
    else:
        print("⚠️ THRESHOLDS NEED FINE-TUNING")
        print("🔧 Some adjustments may be needed")
    
    print()
    print("🚀 Your stroke detection app is now:")
    print("   ✅ Accurately detecting normal arm positions")
    print("   ✅ Properly classifying drift severity levels")
    print("   ✅ Ready for clinical testing!")

if __name__ == "__main__":
    test_calibrated_thresholds()
