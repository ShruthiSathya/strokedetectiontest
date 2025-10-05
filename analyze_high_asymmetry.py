#!/usr/bin/env python3
"""
Analyze why there's still high asymmetry (33.4%) even when arms are not drifting.
This will help identify the root cause of the persistent asymmetry.
"""

import json
import math

def analyze_keypoint_positions():
    """Analyze the keypoint positions to understand why asymmetry is still high."""
    
    # Your actual keypoint data
    keypoints = {
        'left_wrist': {'x': 0.5560755729675293, 'y': 0.5311617851257324},
        'left_shoulder': {'x': 0.5504499673843384, 'y': 0.5109182596206665},
        'right_wrist': {'x': 0.3835928738117218, 'y': 0.5197547674179077},
        'right_shoulder': {'x': 0.42909833788871765, 'y': 0.506827712059021}
    }
    
    print("🔍 DETAILED KEYPOINT ANALYSIS")
    print("=" * 60)
    print("📊 Your actual keypoint positions:")
    print(f"   Left wrist:   ({keypoints['left_wrist']['x']:.3f}, {keypoints['left_wrist']['y']:.3f})")
    print(f"   Left shoulder: ({keypoints['left_shoulder']['x']:.3f}, {keypoints['left_shoulder']['y']:.3f})")
    print(f"   Right wrist:  ({keypoints['right_wrist']['x']:.3f}, {keypoints['right_wrist']['y']:.3f})")
    print(f"   Right shoulder: ({keypoints['right_shoulder']['x']:.3f}, {keypoints['right_shoulder']['y']:.3f})")
    print()
    
    # Calculate individual components
    left_arm_length = math.sqrt((keypoints['left_wrist']['x'] - keypoints['left_shoulder']['x'])**2 + 
                               (keypoints['left_wrist']['y'] - keypoints['left_shoulder']['y'])**2)
    right_arm_length = math.sqrt((keypoints['right_wrist']['x'] - keypoints['right_shoulder']['x'])**2 + 
                                (keypoints['right_wrist']['y'] - keypoints['right_shoulder']['y'])**2)
    
    vertical_drift = abs(keypoints['left_wrist']['y'] - keypoints['right_wrist']['y'])
    horizontal_drift = abs(keypoints['left_wrist']['x'] - keypoints['right_wrist']['x'])
    
    print("📏 MEASUREMENTS:")
    print(f"   Left arm length:  {left_arm_length:.3f}")
    print(f"   Right arm length: {right_arm_length:.3f}")
    print(f"   Vertical drift:   {vertical_drift:.3f}")
    print(f"   Horizontal drift: {horizontal_drift:.3f}")
    print()
    
    # Analyze the asymmetry components
    print("🔍 ASYMMETRY BREAKDOWN:")
    
    # 1. Arm length difference
    arm_length_diff = abs(left_arm_length - right_arm_length)
    arm_length_asymmetry = arm_length_diff / max(left_arm_length, right_arm_length)
    print(f"   1. Arm length difference: {arm_length_diff:.3f}")
    print(f"      Arm length asymmetry: {arm_length_asymmetry*100:.1f}%")
    
    # 2. Vertical drift
    print(f"   2. Vertical drift: {vertical_drift:.3f}")
    
    # 3. Horizontal positioning
    left_center = (keypoints['left_wrist']['x'] + keypoints['left_shoulder']['x']) / 2
    right_center = (keypoints['right_wrist']['x'] + keypoints['right_shoulder']['x']) / 2
    horizontal_center_diff = abs(left_center - right_center)
    print(f"   3. Horizontal center difference: {horizontal_center_diff:.3f}")
    
    # 4. Shoulder level difference
    shoulder_level_diff = abs(keypoints['left_shoulder']['y'] - keypoints['right_shoulder']['y'])
    print(f"   4. Shoulder level difference: {shoulder_level_diff:.3f}")
    print()
    
    # Current asymmetry calculation
    avg_arm_length = (left_arm_length + right_arm_length) / 2
    current_asymmetry = vertical_drift / avg_arm_length
    
    print("⚖️ CURRENT ASYMMETRY CALCULATION:")
    print(f"   Formula: vertical_drift / avg_arm_length")
    print(f"   Calculation: {vertical_drift:.3f} / {avg_arm_length:.3f} = {current_asymmetry:.3f} ({current_asymmetry*100:.1f}%)")
    print()
    
    # Identify potential issues
    print("🚨 POTENTIAL ISSUES IDENTIFIED:")
    
    issues = []
    
    # Issue 1: Arm length difference
    if arm_length_asymmetry > 0.3:  # >30% difference
        issues.append(f"Large arm length difference ({arm_length_asymmetry*100:.1f}%) - suggests detection accuracy issues")
    
    # Issue 2: Horizontal positioning
    if horizontal_center_diff > 0.1:  # >10% difference
        issues.append(f"Significant horizontal positioning difference ({horizontal_center_diff*100:.1f}%) - arms not centered")
    
    # Issue 3: Shoulder level
    if shoulder_level_diff > 0.02:  # >2% difference
        issues.append(f"Shoulder level difference ({shoulder_level_diff*100:.1f}%) - body not level")
    
    # Issue 4: Small arm lengths
    if avg_arm_length < 0.05:  # <5%
        issues.append(f"Very small arm lengths ({avg_arm_length*100:.1f}%) - suggests detection or positioning issues")
    
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("   No obvious issues detected in keypoint positioning")
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("   1. Check camera positioning - ensure it's centered and level")
    print("   2. Verify arm positioning - both arms should be at same height and distance")
    print("   3. Improve lighting - better lighting helps keypoint detection accuracy")
    print("   4. Check keypoint detection confidence - low confidence can cause positioning errors")
    print("   5. Consider using a different asymmetry metric that's less sensitive to detection errors")
    
    return {
        'arm_length_asymmetry': arm_length_asymmetry,
        'horizontal_center_diff': horizontal_center_diff,
        'shoulder_level_diff': shoulder_level_diff,
        'avg_arm_length': avg_arm_length,
        'current_asymmetry': current_asymmetry,
        'issues': issues
    }

def suggest_alternative_asymmetry_metrics():
    """Suggest alternative asymmetry metrics that might be more robust."""
    
    print("\n🔧 ALTERNATIVE ASYMMETRY METRICS:")
    print("=" * 60)
    
    print("Current metric: vertical_drift / avg_arm_length")
    print("Problems: Sensitive to detection errors, small arm lengths amplify asymmetry")
    print()
    
    print("Alternative 1: Absolute vertical drift")
    print("Formula: abs(left_wrist_y - right_wrist_y)")
    print("Pros: Simple, not affected by arm length detection errors")
    print("Cons: Doesn't normalize for person size or distance")
    print()
    
    print("Alternative 2: Relative vertical drift")
    print("Formula: abs(left_wrist_y - right_wrist_y) / body_height")
    print("Pros: Normalizes for person size")
    print("Cons: Requires body height estimation")
    print()
    
    print("Alternative 3: Combined drift metric")
    print("Formula: sqrt(vertical_drift² + horizontal_drift²) / avg_arm_length")
    print("Pros: Accounts for both vertical and horizontal drift")
    print("Cons: Still sensitive to arm length detection")
    print()
    
    print("Alternative 4: Confidence-weighted metric")
    print("Formula: drift / (arm_length * confidence)")
    print("Pros: Reduces impact of low-confidence detections")
    print("Cons: Requires confidence scores from keypoint detection")
    print()
    
    print("Alternative 5: Threshold-based metric")
    print("Formula: 1 if drift > threshold, else 0")
    print("Pros: Binary classification, less sensitive to small variations")
    print("Cons: Less granular information")

if __name__ == "__main__":
    result = analyze_keypoint_positions()
    suggest_alternative_asymmetry_metrics()
