#!/usr/bin/env python3
"""
Test the adjusted thresholds with the user's reported asymmetry value.
"""

def test_adjusted_thresholds():
    """Test how the new thresholds would classify the user's asymmetry"""
    
    print("🧪 TESTING ADJUSTED THRESHOLDS")
    print("=" * 50)
    
    # User's reported asymmetry from Lambda response
    user_asymmetry = 0.21708791278123382  # 21.7%
    
    # New adjusted thresholds
    NIHSS_0_NORMAL = 0.15           # <15% drift - Normal arm position (no stroke)
    NIHSS_1_MILD = 0.25             # 15-25% drift - Mild drift (NIHSS Score 1)
    NIHSS_2_MODERATE = 0.40         # 25-40% drift - Moderate drift (NIHSS Score 2)
    NIHSS_3_SEVERE = 0.60           # 40-60% drift - Severe drift (NIHSS Score 3)
    NIHSS_4_PARALYSIS = 0.80        # >60% drift - Critical/Paralysis (NIHSS Score 4)
    
    print(f"📊 User's detected asymmetry: {user_asymmetry:.4f} ({user_asymmetry*100:.1f}%)")
    print(f"🎯 New thresholds:")
    print(f"   Normal: <{NIHSS_0_NORMAL*100:.0f}%")
    print(f"   Mild: {NIHSS_1_MILD*100:.0f}%-{NIHSS_2_MODERATE*100:.0f}%")
    print(f"   Moderate: {NIHSS_2_MODERATE*100:.0f}%-{NIHSS_3_SEVERE*100:.0f}%")
    print(f"   Severe: {NIHSS_3_SEVERE*100:.0f}%-{NIHSS_4_PARALYSIS*100:.0f}%")
    print(f"   Critical: >{NIHSS_4_PARALYSIS*100:.0f}%")
    
    # Classify the user's asymmetry
    if user_asymmetry < NIHSS_0_NORMAL:
        classification = "Normal"
        nihss_score = 0
        severity = "normal"
    elif user_asymmetry < NIHSS_1_MILD:
        classification = "Mild"
        nihss_score = 1
        severity = "mild"
    elif user_asymmetry < NIHSS_2_MODERATE:
        classification = "Moderate"
        nihss_score = 2
        severity = "moderate"
    elif user_asymmetry < NIHSS_3_SEVERE:
        classification = "Severe"
        nihss_score = 3
        severity = "severe"
    else:
        classification = "Critical"
        nihss_score = 4
        severity = "critical"
    
    print(f"\n🎯 CLASSIFICATION WITH NEW THRESHOLDS:")
    print(f"   Severity: {severity.upper()}")
    print(f"   NIHSS Score: {nihss_score}/4")
    print(f"   Classification: {classification}")
    
    # Compare with old thresholds
    old_NIHSS_0_NORMAL = 0.03
    old_NIHSS_1_MILD = 0.10
    old_NIHSS_2_MODERATE = 0.20
    old_NIHSS_3_SEVERE = 0.35
    old_NIHSS_4_PARALYSIS = 0.50
    
    if user_asymmetry < old_NIHSS_0_NORMAL:
        old_classification = "Normal"
        old_nihss_score = 0
        old_severity = "normal"
    elif user_asymmetry < old_NIHSS_1_MILD:
        old_classification = "Mild"
        old_nihss_score = 1
        old_severity = "mild"
    elif user_asymmetry < old_NIHSS_2_MODERATE:
        old_classification = "Moderate"
        old_nihss_score = 2
        old_severity = "moderate"
    elif user_asymmetry < old_NIHSS_3_SEVERE:
        old_classification = "Severe"
        old_nihss_score = 3
        old_severity = "severe"
    else:
        old_classification = "Critical"
        old_nihss_score = 4
        old_severity = "critical"
    
    print(f"\n📊 COMPARISON:")
    print(f"   OLD thresholds: {old_severity.upper()} (NIHSS {old_nihss_score}/4)")
    print(f"   NEW thresholds: {severity.upper()} (NIHSS {nihss_score}/4)")
    
    if old_severity != severity:
        print(f"   ✅ IMPROVEMENT: Changed from {old_severity} to {severity}")
    else:
        print(f"   ⚠️  Same classification with both threshold sets")

if __name__ == "__main__":
    test_adjusted_thresholds()
