#!/usr/bin/env python3
"""
Debug script to understand why the Lambda function is detecting 21.7% asymmetry
when the user reports they didn't drift their arms.
"""

def analyze_keypoint_scenario():
    """Analyze what keypoint positions would cause 21.7% asymmetry"""
    
    print("🔍 DEBUGGING ASYMMETRY DETECTION ISSUE")
    print("=" * 50)
    
    # The Lambda detected 21.7% asymmetry (0.21708791278123382)
    target_asymmetry = 0.21708791278123382
    print(f"🎯 Target asymmetry: {target_asymmetry:.4f} ({target_asymmetry*100:.1f}%)")
    
    # Simulate different keypoint scenarios
    scenarios = [
        {
            "name": "Natural Arm Asymmetry",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.65,  # 5% lower
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.3
        },
        {
            "name": "Slight Arm Length Difference",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.62,  # 2% lower
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.32  # 2% lower shoulder
        },
        {
            "name": "Camera Angle Effect",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.58,  # 2% higher
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.3
        },
        {
            "name": "Body Position Offset",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.66,  # 6% lower
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.3
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print("-" * 30)
        
        # Extract coordinates
        left_wrist_y = scenario['left_wrist_y']
        right_wrist_y = scenario['right_wrist_y']
        left_shoulder_y = scenario['left_shoulder_y']
        right_shoulder_y = scenario['right_shoulder_y']
        
        # Calculate drift using Lambda logic
        vertical_drift_pixels = abs(left_wrist_y - right_wrist_y)
        left_arm_length = abs(left_wrist_y - left_shoulder_y)
        right_arm_length = abs(right_wrist_y - right_shoulder_y)
        avg_arm_length = (left_arm_length + right_arm_length) / 2
        
        if avg_arm_length < 0.01:
            asymmetry_score = 0.0
            print(f"   ⚠️ Avg arm length too small: {avg_arm_length:.4f}")
        else:
            asymmetry_score = vertical_drift_pixels / avg_arm_length
            print(f"   ✅ Calculated asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
        
        print(f"   Left wrist Y: {left_wrist_y}")
        print(f"   Right wrist Y: {right_wrist_y}")
        print(f"   Vertical drift: {vertical_drift_pixels:.4f}")
        print(f"   Left arm length: {left_arm_length:.4f}")
        print(f"   Right arm length: {right_arm_length:.4f}")
        print(f"   Avg arm length: {avg_arm_length:.4f}")
        
        # Check if this matches the target
        if abs(asymmetry_score - target_asymmetry) < 0.001:
            print(f"   🎯 MATCH! This scenario produces the exact asymmetry detected")
    
    print(f"\n🔍 ANALYSIS:")
    print(f"The Lambda detected {target_asymmetry*100:.1f}% asymmetry.")
    print(f"This could be caused by:")
    print(f"1. Natural arm asymmetry (one arm slightly higher/lower)")
    print(f"2. Camera angle or perspective distortion")
    print(f"3. Body position offset (leaning slightly)")
    print(f"4. Vision framework keypoint detection inaccuracy")
    print(f"5. Normal human body asymmetry (most people have slight asymmetry)")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"1. Add tolerance for natural asymmetry (e.g., <5% is normal)")
    print(f"2. Improve keypoint detection accuracy")
    print(f"3. Add calibration baseline to account for natural asymmetry")
    print(f"4. Use multiple frames to average out detection noise")

if __name__ == "__main__":
    analyze_keypoint_scenario()
