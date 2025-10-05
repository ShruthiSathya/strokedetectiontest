#!/usr/bin/env python3
"""
Create a more robust asymmetry calculation that's less sensitive to keypoint detection errors.
This will provide more accurate results even when keypoint detection is imperfect.
"""

import json
import math

def calculate_robust_asymmetry(keypoints):
    """
    Calculate asymmetry using multiple methods and choose the most reliable one.
    This approach is less sensitive to keypoint detection errors.
    """
    
    # Extract coordinates
    left_wrist = keypoints['left_wrist']
    right_wrist = keypoints['right_wrist']
    left_shoulder = keypoints['left_shoulder']
    right_shoulder = keypoints['right_shoulder']
    
    print("🔧 ROBUST ASYMMETRY CALCULATION")
    print("=" * 60)
    
    # Method 1: Current method (sensitive to detection errors)
    left_arm_length = math.sqrt((left_wrist['x'] - left_shoulder['x'])**2 + 
                               (left_wrist['y'] - left_shoulder['y'])**2)
    right_arm_length = math.sqrt((right_wrist['x'] - right_shoulder['x'])**2 + 
                                (right_wrist['y'] - right_shoulder['y'])**2)
    avg_arm_length = (left_arm_length + right_arm_length) / 2
    vertical_drift = abs(left_wrist['y'] - right_wrist['y'])
    
    current_asymmetry = vertical_drift / avg_arm_length if avg_arm_length > 0.01 else 0
    
    print("Method 1 (Current): vertical_drift / avg_arm_length")
    print(f"   Result: {current_asymmetry:.3f} ({current_asymmetry*100:.1f}%)")
    print(f"   Issues: Sensitive to arm length detection errors")
    print()
    
    # Method 2: Absolute vertical drift (not normalized)
    absolute_drift = abs(left_wrist['y'] - right_wrist['y'])
    print("Method 2 (Absolute): abs(left_wrist_y - right_wrist_y)")
    print(f"   Result: {absolute_drift:.3f} ({absolute_drift*100:.1f}%)")
    print(f"   Issues: Doesn't normalize for person size/distance")
    print()
    
    # Method 3: Body-relative drift (using shoulder distance as reference)
    shoulder_distance = abs(left_shoulder['x'] - right_shoulder['x'])
    if shoulder_distance > 0.01:
        body_relative_drift = vertical_drift / shoulder_distance
        print("Method 3 (Body-relative): vertical_drift / shoulder_distance")
        print(f"   Result: {body_relative_drift:.3f} ({body_relative_drift*100:.1f}%)")
        print(f"   Issues: Assumes shoulders are detected accurately")
    else:
        body_relative_drift = 0
        print("Method 3 (Body-relative): Cannot calculate - shoulder distance too small")
    print()
    
    # Method 4: Confidence-weighted (if we had confidence scores)
    # This would be: drift / (arm_length * confidence)
    # For now, we'll simulate with a quality score based on arm length consistency
    arm_length_consistency = 1.0 - abs(left_arm_length - right_arm_length) / max(left_arm_length, right_arm_length)
    confidence_weighted_drift = vertical_drift / (avg_arm_length * max(arm_length_consistency, 0.1))
    
    print("Method 4 (Confidence-weighted): drift / (arm_length * consistency)")
    print(f"   Arm length consistency: {arm_length_consistency:.3f}")
    print(f"   Result: {confidence_weighted_drift:.3f} ({confidence_weighted_drift*100:.1f}%)")
    print(f"   Issues: Still depends on arm length detection")
    print()
    
    # Method 5: Threshold-based (binary classification)
    # Use a fixed threshold for vertical drift
    drift_threshold = 0.05  # 5% of screen height
    threshold_based = 1 if vertical_drift > drift_threshold else 0
    
    print("Method 5 (Threshold-based): 1 if drift > 5%, else 0")
    print(f"   Threshold: {drift_threshold:.3f} ({drift_threshold*100:.1f}%)")
    print(f"   Result: {threshold_based} ({'Drift detected' if threshold_based else 'No drift'})")
    print(f"   Issues: Binary classification, less granular")
    print()
    
    # Method 6: Combined metric (vertical + horizontal drift)
    horizontal_drift = abs(left_wrist['x'] - right_wrist['x'])
    combined_drift = math.sqrt(vertical_drift**2 + horizontal_drift**2)
    combined_asymmetry = combined_drift / avg_arm_length if avg_arm_length > 0.01 else 0
    
    print("Method 6 (Combined): sqrt(vertical² + horizontal²) / avg_arm_length")
    print(f"   Vertical drift: {vertical_drift:.3f}")
    print(f"   Horizontal drift: {horizontal_drift:.3f}")
    print(f"   Combined drift: {combined_drift:.3f}")
    print(f"   Result: {combined_asymmetry:.3f} ({combined_asymmetry*100:.1f}%)")
    print(f"   Issues: Still sensitive to arm length detection")
    print()
    
    # Recommendation: Choose the most reliable method
    print("🎯 RECOMMENDATION:")
    
    # Check for detection quality issues
    arm_length_diff = abs(left_arm_length - right_arm_length) / max(left_arm_length, right_arm_length)
    small_arm_lengths = avg_arm_length < 0.05
    
    if arm_length_diff > 0.5 or small_arm_lengths:
        print("   ⚠️  Keypoint detection quality is poor")
        print("   📊 Recommended method: Absolute vertical drift (Method 2)")
        print(f"   🎯 Recommended asymmetry: {absolute_drift:.3f} ({absolute_drift*100:.1f}%)")
        recommended_method = "absolute"
        recommended_value = absolute_drift
    else:
        print("   ✅ Keypoint detection quality is good")
        print("   📊 Recommended method: Current method (Method 1)")
        print(f"   🎯 Recommended asymmetry: {current_asymmetry:.3f} ({current_asymmetry*100:.1f}%)")
        recommended_method = "current"
        recommended_value = current_asymmetry
    
    return {
        'current': current_asymmetry,
        'absolute': absolute_drift,
        'body_relative': body_relative_drift,
        'confidence_weighted': confidence_weighted_drift,
        'threshold_based': threshold_based,
        'combined': combined_asymmetry,
        'recommended_method': recommended_method,
        'recommended_value': recommended_value,
        'detection_quality': 'poor' if arm_length_diff > 0.5 or small_arm_lengths else 'good'
    }

def test_robust_calculation():
    """Test the robust calculation with the user's data."""
    
    # User's actual keypoint data
    keypoints = {
        'left_wrist': {'x': 0.5560755729675293, 'y': 0.5311617851257324},
        'left_shoulder': {'x': 0.5504499673843384, 'y': 0.5109182596206665},
        'right_wrist': {'x': 0.3835928738117218, 'y': 0.5197547674179077},
        'right_shoulder': {'x': 0.42909833788871765, 'y': 0.506827712059021}
    }
    
    result = calculate_robust_asymmetry(keypoints)
    
    print("\n📋 SUMMARY:")
    print("=" * 60)
    print(f"Current method result: {result['current']*100:.1f}%")
    print(f"Absolute drift result: {result['absolute']*100:.1f}%")
    print(f"Recommended method: {result['recommended_method']}")
    print(f"Recommended asymmetry: {result['recommended_value']*100:.1f}%")
    print(f"Detection quality: {result['detection_quality']}")
    
    # NIHSS classification with recommended value
    if result['recommended_value'] < 0.20:
        nihss_score = 0
        severity = "normal"
    elif result['recommended_value'] < 0.35:
        nihss_score = 1
        severity = "mild"
    elif result['recommended_value'] < 0.50:
        nihss_score = 2
        severity = "moderate"
    elif result['recommended_value'] < 0.70:
        nihss_score = 3
        severity = "severe"
    else:
        nihss_score = 4
        severity = "critical"
    
    print(f"\n🏥 NIHSS ASSESSMENT (with recommended method):")
    print(f"   Score: {nihss_score} - {severity.upper()}")
    
    if nihss_score <= 1:
        print("   ✅ Result: Normal or mild variation - no motor test error!")
    else:
        print("   ⚠️  Result: Still showing significant asymmetry")

if __name__ == "__main__":
    test_robust_calculation()
