#!/usr/bin/env python3
"""
Test the motor test fix with the actual keypoint data from the user's debug output.
This will verify that the Euclidean distance calculation fixes the 68.8% asymmetry issue.
"""

import json
import math

def calculate_nihss_motor_score(y_difference, test_duration=20.0):
    """Calculate NIHSS Motor Arm Score based on clinical standards."""
    # Convert percentage to decimal if needed
    if y_difference > 1.0:
        y_difference = y_difference / 100.0
    
    # NIHSS Motor Arm Score (Item 5) - Clinical Standards
    if y_difference < 0.01:  # <1% - No drift
        return {'nihss_motor_score': 0, 'severity': 'normal'}
    elif y_difference < 0.03:  # 1-3% - Mild drift
        return {'nihss_motor_score': 1, 'severity': 'mild'}
    elif y_difference < 0.08:  # 3-8% - Moderate drift
        return {'nihss_motor_score': 2, 'severity': 'moderate'}
    elif y_difference < 0.15:  # 8-15% - Severe drift
        return {'nihss_motor_score': 3, 'severity': 'severe'}
    else:  # >15% - No movement
        return {'nihss_motor_score': 4, 'severity': 'critical'}

def analyze_keypoint_asymmetry_old_method(keypoints):
    """OLD METHOD: Using Y-only distance (causing the 68.8% asymmetry issue)"""
    left_wrist = keypoints['left_wrist']
    right_wrist = keypoints['right_wrist']
    left_shoulder = keypoints['left_shoulder']
    right_shoulder = keypoints['right_shoulder']
    
    # OLD CALCULATION: Y-only distance (WRONG for 90-degree arms)
    left_arm_length = abs(left_wrist['y'] - left_shoulder['y'])
    right_arm_length = abs(right_wrist['y'] - right_shoulder['y'])
    avg_arm_length = (left_arm_length + right_arm_length) / 2
    
    vertical_drift = abs(left_wrist['y'] - right_wrist['y'])
    
    if avg_arm_length > 0.01:
        asymmetry_score = vertical_drift / avg_arm_length
    else:
        asymmetry_score = 0.0
    
    return {
        'method': 'OLD (Y-only)',
        'left_arm_length': left_arm_length,
        'right_arm_length': right_arm_length,
        'avg_arm_length': avg_arm_length,
        'vertical_drift': vertical_drift,
        'asymmetry_score': asymmetry_score,
        'asymmetry_percent': asymmetry_score * 100
    }

def analyze_keypoint_asymmetry_new_method(keypoints):
    """NEW METHOD: Using Euclidean distance (correct for 90-degree arms)"""
    left_wrist = keypoints['left_wrist']
    right_wrist = keypoints['right_wrist']
    left_shoulder = keypoints['left_shoulder']
    right_shoulder = keypoints['right_shoulder']
    
    # NEW CALCULATION: Euclidean distance (CORRECT for 90-degree arms)
    left_arm_length = math.sqrt((left_wrist['x'] - left_shoulder['x'])**2 + (left_wrist['y'] - left_shoulder['y'])**2)
    right_arm_length = math.sqrt((right_wrist['x'] - right_shoulder['x'])**2 + (right_wrist['y'] - right_shoulder['y'])**2)
    avg_arm_length = (left_arm_length + right_arm_length) / 2
    
    vertical_drift = abs(left_wrist['y'] - right_wrist['y'])
    
    if avg_arm_length > 0.01:
        asymmetry_score = vertical_drift / avg_arm_length
    else:
        asymmetry_score = 0.0
    
    return {
        'method': 'NEW (Euclidean)',
        'left_arm_length': left_arm_length,
        'right_arm_length': right_arm_length,
        'avg_arm_length': avg_arm_length,
        'vertical_drift': vertical_drift,
        'asymmetry_score': asymmetry_score,
        'asymmetry_percent': asymmetry_score * 100
    }

def test_motor_test_fix():
    """Test the fix with the actual keypoint data from the user's debug output."""
    
    # Actual keypoint data from the user's debug output
    keypoints = {
        'left_elbow': {'x': 0.575599193572998, 'y': 0.5115957260131836},
        'left_shoulder': {'x': 0.5504499673843384, 'y': 0.5109182596206665},
        'left_wrist': {'x': 0.5560755729675293, 'y': 0.5311617851257324},
        'right_elbow': {'x': 0.3907064199447632, 'y': 0.5024568438529968},
        'right_shoulder': {'x': 0.42909833788871765, 'y': 0.506827712059021},
        'right_wrist': {'x': 0.3835928738117218, 'y': 0.5197547674179077}
    }
    
    print("🔍 MOTOR TEST FIX VERIFICATION")
    print("=" * 60)
    print("📊 Using actual keypoint data from user's debug output:")
    print(f"   Left wrist: ({keypoints['left_wrist']['x']:.3f}, {keypoints['left_wrist']['y']:.3f})")
    print(f"   Left shoulder: ({keypoints['left_shoulder']['x']:.3f}, {keypoints['left_shoulder']['y']:.3f})")
    print(f"   Right wrist: ({keypoints['right_wrist']['x']:.3f}, {keypoints['right_wrist']['y']:.3f})")
    print(f"   Right shoulder: ({keypoints['right_shoulder']['x']:.3f}, {keypoints['right_shoulder']['y']:.3f})")
    print()
    
    # Test OLD method (causing the issue)
    old_result = analyze_keypoint_asymmetry_old_method(keypoints)
    old_nihss = calculate_nihss_motor_score(old_result['asymmetry_score'])
    
    print("❌ OLD METHOD (Y-only distance - CAUSING THE ISSUE):")
    print(f"   🦾 Left arm length: {old_result['left_arm_length']:.3f}")
    print(f"   🦾 Right arm length: {old_result['right_arm_length']:.3f}")
    print(f"   📏 Vertical drift: {old_result['vertical_drift']:.3f}")
    print(f"   📐 Average arm length: {old_result['avg_arm_length']:.3f}")
    print(f"   ⚖️ Asymmetry: {old_result['asymmetry_percent']:.1f}%")
    print(f"   🏥 NIHSS Score: {old_nihss['nihss_motor_score']} - {old_nihss['severity'].upper()}")
    print()
    
    # Test NEW method (the fix)
    new_result = analyze_keypoint_asymmetry_new_method(keypoints)
    new_nihss = calculate_nihss_motor_score(new_result['asymmetry_score'])
    
    print("✅ NEW METHOD (Euclidean distance - THE FIX):")
    print(f"   🦾 Left arm length: {new_result['left_arm_length']:.3f}")
    print(f"   🦾 Right arm length: {new_result['right_arm_length']:.3f}")
    print(f"   📏 Vertical drift: {new_result['vertical_drift']:.3f}")
    print(f"   📐 Average arm length: {new_result['avg_arm_length']:.3f}")
    print(f"   ⚖️ Asymmetry: {new_result['asymmetry_percent']:.1f}%")
    print(f"   🏥 NIHSS Score: {new_nihss['nihss_motor_score']} - {new_nihss['severity'].upper()}")
    print()
    
    # Summary
    print("📋 SUMMARY:")
    print(f"   OLD asymmetry: {old_result['asymmetry_percent']:.1f}% → NIHSS {old_nihss['nihss_motor_score']} ({old_nihss['severity']})")
    print(f"   NEW asymmetry: {new_result['asymmetry_percent']:.1f}% → NIHSS {new_nihss['nihss_motor_score']} ({new_nihss['severity']})")
    print()
    
    if new_result['asymmetry_percent'] < 10.0:
        print("🎉 SUCCESS: The fix resolves the motor test error!")
        print("   The asymmetry is now within normal range for straight arms.")
    else:
        print("⚠️  The fix helps but asymmetry is still high.")
        print("   This might indicate actual positioning issues.")
    
    return {
        'old_result': old_result,
        'new_result': new_result,
        'old_nihss': old_nihss,
        'new_nihss': new_nihss
    }

if __name__ == "__main__":
    test_motor_test_fix()
