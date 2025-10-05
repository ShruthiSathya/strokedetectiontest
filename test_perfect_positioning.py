#!/usr/bin/env python3
"""
Test script to simulate perfect positioning scenarios and see what asymmetry values would be expected.
"""

def test_perfect_positioning_scenarios():
    """Test various perfect positioning scenarios to understand expected asymmetry values"""
    
    print("🧪 TESTING PERFECT POSITIONING SCENARIOS")
    print("=" * 60)
    
    # Perfect positioning scenarios
    scenarios = [
        {
            "name": "Perfect Symmetry (Ideal)",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.6,
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.3,
            "expected": "0% asymmetry"
        },
        {
            "name": "Perfect Symmetry (Different Heights)",
            "left_wrist_y": 0.7,
            "right_wrist_y": 0.7,
            "left_shoulder_y": 0.4,
            "right_shoulder_y": 0.4,
            "expected": "0% asymmetry"
        },
        {
            "name": "Tiny Detection Error (±1%)",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.606,  # 1% difference
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.3,
            "expected": "~2% asymmetry"
        },
        {
            "name": "Small Detection Error (±2%)",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.612,  # 2% difference
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.3,
            "expected": "~6% asymmetry"
        },
        {
            "name": "Your Current Detection (22.6%)",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.72,   # 20% difference to achieve ~22% asymmetry
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.3,
            "expected": "~22% asymmetry"
        },
        {
            "name": "Significant Drift (Stroke-like)",
            "left_wrist_y": 0.6,
            "right_wrist_y": 0.8,    # 33% difference
            "left_shoulder_y": 0.3,
            "right_shoulder_y": 0.3,
            "expected": "~67% asymmetry"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print("-" * 50)
        
        # Extract coordinates
        left_wrist_y = scenario['left_wrist_y']
        right_wrist_y = scenario['right_wrist_y']
        left_shoulder_y = scenario['left_shoulder_y']
        right_shoulder_y = scenario['right_shoulder_y']
        
        # Calculate asymmetry using Lambda logic
        vertical_drift_pixels = abs(left_wrist_y - right_wrist_y)
        left_arm_length = abs(left_wrist_y - left_shoulder_y)
        right_arm_length = abs(right_wrist_y - right_shoulder_y)
        avg_arm_length = (left_arm_length + right_arm_length) / 2
        
        if avg_arm_length < 0.01:
            asymmetry_score = 0.0
        else:
            asymmetry_score = vertical_drift_pixels / avg_arm_length
        
        print(f"   Left wrist Y: {left_wrist_y}")
        print(f"   Right wrist Y: {right_wrist_y}")
        print(f"   Vertical drift: {vertical_drift_pixels:.4f}")
        print(f"   Left arm length: {left_arm_length:.4f}")
        print(f"   Right arm length: {right_arm_length:.4f}")
        print(f"   Avg arm length: {avg_arm_length:.4f}")
        print(f"   ✅ Calculated asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
        print(f"   📋 Expected: {scenario['expected']}")
        
        # Classify severity
        if asymmetry_score < 0.15:
            severity = "Normal"
        elif asymmetry_score < 0.25:
            severity = "Mild"
        elif asymmetry_score < 0.40:
            severity = "Moderate"
        elif asymmetry_score < 0.60:
            severity = "Severe"
        else:
            severity = "Critical"
        
        print(f"   🎯 Classification: {severity}")
    
    print(f"\n🔍 ANALYSIS OF YOUR 22.6% ASYMMETRY:")
    print("=" * 45)
    
    print(f"**To achieve 22.6% asymmetry, one wrist would need to be ~20% higher/lower than the other.**")
    print(f"")
    print(f"**This is equivalent to:**")
    print(f"• One arm being significantly higher than the other")
    print(f"• Shoulder height difference")
    print(f"• Body leaning to one side")
    print(f"• Camera angle creating perspective distortion")
    print(f"• Vision framework detection error")
    
    print(f"\n💡 **DIAGNOSTIC QUESTIONS:**")
    print(f"=" * 30)
    
    print(f"1. **Are you standing perfectly centered in the camera view?**")
    print(f"   • If not, this could cause apparent asymmetry")
    
    print(f"\n2. **Is the camera at eye level?**")
    print(f"   • Camera above/below eye level can create perspective distortion")
    
    print(f"\n3. **Are your shoulders at the same height?**")
    print(f"   • Natural shoulder height differences can cause wrist asymmetry")
    
    print(f"\n4. **Are you holding your arms at exactly the same height?**")
    print(f"   • Use a mirror to verify both arms are level")
    
    print(f"\n5. **Is the lighting even on both sides?**")
    print(f"   • Uneven lighting can affect keypoint detection accuracy")
    
    print(f"\n🎯 **RECOMMENDED TEST:**")
    print(f"=" * 25)
    
    print(f"1. **Perfect Setup Test:**")
    print(f"   • Stand in front of a mirror")
    print(f"   • Position camera at eye level")
    print(f"   • Ensure both arms are exactly level")
    print(f"   • Run the test 5 times")
    print(f"   • Expected result: <10% asymmetry")
    
    print(f"\n2. **If still getting >15% asymmetry:**")
    print(f"   • The issue is likely with keypoint detection accuracy")
    print(f"   • Consider adjusting thresholds further")
    print(f"   • May need to improve camera setup or lighting")

if __name__ == "__main__":
    test_perfect_positioning_scenarios()
