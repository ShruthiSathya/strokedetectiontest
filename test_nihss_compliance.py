#!/usr/bin/env python3
"""
Test script to compare current implementation with NIHSS-compliant version.
"""

def test_nihss_compliance():
    """Test how both implementations would classify the user's 22.6% asymmetry"""
    
    print("🧪 TESTING NIHSS COMPLIANCE")
    print("=" * 60)
    
    # User's reported asymmetry
    user_asymmetry = 0.22600902200865777  # 22.6%
    
    print(f"📊 User's detected asymmetry: {user_asymmetry:.4f} ({user_asymmetry*100:.1f}%)")
    
    # Current implementation thresholds
    current_thresholds = {
        "Normal": 0.15,    # 15%
        "Mild": 0.25,      # 25%
        "Moderate": 0.40,  # 40%
        "Severe": 0.60,    # 60%
        "Critical": 0.80   # 80%
    }
    
    # NIHSS-compliant thresholds
    nihss_thresholds = {
        "Normal": 0.05,    # 5%
        "Mild": 0.15,      # 15%
        "Moderate": 0.30,  # 30%
        "Severe": 0.50,    # 50%
        "Critical": 0.80   # 80%
    }
    
    print(f"\n📊 THRESHOLD COMPARISON:")
    print(f"=" * 40)
    
    print(f"Current Implementation:")
    for severity, threshold in current_thresholds.items():
        print(f"   {severity}: {threshold*100:.0f}%")
    
    print(f"\nNIHSS-Compliant Implementation:")
    for severity, threshold in nihss_thresholds.items():
        print(f"   {severity}: {threshold*100:.0f}%")
    
    # Classify with current implementation
    if user_asymmetry < current_thresholds["Normal"]:
        current_classification = "Normal"
        current_nihss = 0
    elif user_asymmetry < current_thresholds["Mild"]:
        current_classification = "Mild"
        current_nihss = 1
    elif user_asymmetry < current_thresholds["Moderate"]:
        current_classification = "Moderate"
        current_nihss = 2
    elif user_asymmetry < current_thresholds["Severe"]:
        current_classification = "Severe"
        current_nihss = 3
    else:
        current_classification = "Critical"
        current_nihss = 4
    
    # Classify with NIHSS-compliant implementation
    if user_asymmetry < nihss_thresholds["Normal"]:
        nihss_classification = "Normal"
        nihss_score = 0
    elif user_asymmetry < nihss_thresholds["Mild"]:
        nihss_classification = "Mild"
        nihss_score = 1
    elif user_asymmetry < nihss_thresholds["Moderate"]:
        nihss_classification = "Moderate"
        nihss_score = 2
    elif user_asymmetry < nihss_thresholds["Severe"]:
        nihss_classification = "Severe"
        nihss_score = 3
    else:
        nihss_classification = "Critical"
        nihss_score = 4
    
    print(f"\n🎯 CLASSIFICATION RESULTS:")
    print(f"=" * 35)
    
    print(f"Current Implementation:")
    print(f"   Classification: {current_classification}")
    print(f"   NIHSS Score: {current_nihss}/4")
    print(f"   Clinical Meaning: {get_clinical_meaning(current_nihss)}")
    
    print(f"\nNIHSS-Compliant Implementation:")
    print(f"   Classification: {nihss_classification}")
    print(f"   NIHSS Score: {nihss_score}/4")
    print(f"   Clinical Meaning: {get_clinical_meaning(nihss_score)}")
    
    print(f"\n📊 COMPARISON:")
    print(f"=" * 20)
    
    if current_classification != nihss_classification:
        print(f"✅ IMPROVEMENT: Changed from {current_classification} to {nihss_classification}")
        print(f"   NIHSS Score changed from {current_nihss} to {nihss_score}")
    else:
        print(f"⚠️  Same classification with both implementations")
    
    # Analyze the difference
    print(f"\n🔍 ANALYSIS:")
    print(f"=" * 15)
    
    print(f"Your 22.6% asymmetry is:")
    print(f"• {nihss_score} points above NIHSS-compliant 'Normal' threshold")
    print(f"• {nihss_score} points above NIHSS-compliant 'Mild' threshold")
    print(f"• {'At' if nihss_score == 2 else 'Below'} NIHSS-compliant 'Moderate' threshold")
    
    if nihss_score <= 1:
        print(f"✅ NIHSS-compliant classification suggests this is likely normal variation")
    elif nihss_score == 2:
        print(f"⚠️  NIHSS-compliant classification suggests mild weakness")
    else:
        print(f"🚨 NIHSS-compliant classification suggests significant weakness")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"=" * 25)
    
    print(f"1. **Deploy NIHSS-compliant version** for more accurate clinical assessment")
    print(f"2. **Your 22.6% asymmetry would be classified as '{nihss_classification}' with NIHSS standards**")
    print(f"3. **NIHSS-compliant thresholds are more clinically accurate**")
    print(f"4. **Consider implementing arm angle verification** (90° requirement)")
    print(f"5. **Add time-based drift analysis** for full NIHSS compliance")
    
    # Test different asymmetry values
    print(f"\n🧪 TESTING DIFFERENT ASYMMETRY VALUES:")
    print(f"=" * 45)
    
    test_values = [0.03, 0.10, 0.22, 0.35, 0.60]
    
    for test_asymmetry in test_values:
        # Current classification
        if test_asymmetry < current_thresholds["Normal"]:
            current_class = "Normal"
        elif test_asymmetry < current_thresholds["Mild"]:
            current_class = "Mild"
        elif test_asymmetry < current_thresholds["Moderate"]:
            current_class = "Moderate"
        elif test_asymmetry < current_thresholds["Severe"]:
            current_class = "Severe"
        else:
            current_class = "Critical"
        
        # NIHSS classification
        if test_asymmetry < nihss_thresholds["Normal"]:
            nihss_class = "Normal"
        elif test_asymmetry < nihss_thresholds["Mild"]:
            nihss_class = "Mild"
        elif test_asymmetry < nihss_thresholds["Moderate"]:
            nihss_class = "Moderate"
        elif test_asymmetry < nihss_thresholds["Severe"]:
            nihss_class = "Severe"
        else:
            nihss_class = "Critical"
        
        print(f"   {test_asymmetry*100:4.0f}% asymmetry: Current={current_class:8} | NIHSS={nihss_class:8}")

def get_clinical_meaning(nihss_score):
    """Get clinical interpretation of NIHSS score"""
    meanings = {
        0: "No drift - Normal motor function",
        1: "Mild drift - Slight weakness, monitor",
        2: "Moderate drift - Noticeable weakness, medical evaluation recommended",
        3: "Severe drift - Significant weakness, urgent medical evaluation",
        4: "No movement - Severe paralysis, emergency medical care needed"
    }
    return meanings.get(nihss_score, "Unknown score")

if __name__ == "__main__":
    test_nihss_compliance()
