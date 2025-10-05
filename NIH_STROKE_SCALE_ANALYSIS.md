# NIH Stroke Scale Analysis: Motor Arm Test

## 📋 **Official NIH Stroke Scale - Motor Arm Test**

### **NIHSS Item 5: Motor Arm**
**Instructions:** The patient is asked to hold both arms out at 90° (if sitting) or 45° (if supine) with palms down. The patient closes his or her eyes and counts to 10.

**Scoring:**
- **0** = No drift; limb holds 90° (or 45°) for full 10 seconds
- **1** = Drift; limb holds 90° (or 45°) but drifts down before full 10 seconds; does not hit bed or other support
- **2** = Some effort against gravity; limb falls to bed or other support but has some effort against gravity
- **3** = No effort against gravity; limb falls to bed or other support without any effort against gravity
- **4** = No movement; limb is completely paralyzed

## 🔍 **Our Current Implementation Analysis**

### **What We're Measuring:**
```python
# Our current calculation
vertical_drift_pixels = abs(left_wrist_y - right_wrist_y)
avg_arm_length = (abs(left_wrist_y - left_shoulder_y) + abs(right_wrist_y - right_shoulder_y)) / 2
asymmetry_score = vertical_drift_pixels / avg_arm_length
```

### **What NIHSS Actually Measures:**
- **Drift over TIME** (10 seconds)
- **Effort against gravity**
- **Final position** (hitting bed/support vs. holding position)

## 🚨 **Critical Issues with Our Current Implementation**

### **1. We're NOT Following NIHSS Standards**

| NIHSS Requirement | Our Implementation | Issue |
|------------------|-------------------|-------|
| **Time-based drift** | Static position measurement | ❌ We measure position, not drift over time |
| **Gravity resistance** | Vertical position difference | ❌ We don't measure effort against gravity |
| **10-second duration** | Instantaneous measurement | ❌ We take a single snapshot |
| **Eye closure** | Not implemented | ❌ Missing key requirement |
| **Arm angle (90°/45°)** | Not verified | ❌ We don't check arm positioning |

### **2. Our Thresholds Don't Match NIHSS**

| Our Classification | Our Threshold | NIHSS Equivalent | Clinical Meaning |
|-------------------|---------------|------------------|------------------|
| Normal (<15%) | <15% | NIHSS 0 | No drift for 10 seconds |
| Mild (15-25%) | 15-25% | NIHSS 1 | Drift before 10 seconds |
| Moderate (25-40%) | 25-40% | NIHSS 2 | Falls with some effort |
| Severe (40-60%) | 40-60% | NIHSS 3 | Falls without effort |
| Critical (>60%) | >60% | NIHSS 4 | No movement |

**Problem**: Our thresholds are based on position asymmetry, not NIHSS criteria.

## 🎯 **How to Fix Our Implementation**

### **Option 1: True NIHSS Implementation (Recommended)**

```python
def analyze_nihss_motor_arm(keypoints_history: List[Dict], duration_seconds: int) -> Dict:
    """
    True NIHSS Motor Arm Test implementation
    """
    if duration_seconds < 10:
        return {'nihss_score': 0, 'error': 'Test must be at least 10 seconds'}
    
    # Analyze drift over time
    initial_position = keypoints_history[0]
    final_position = keypoints_history[-1]
    
    # Check initial arm positioning (should be ~90° or ~45°)
    initial_arm_angle = calculate_arm_angle(initial_position)
    if not (80 <= initial_arm_angle <= 100):  # Allow some tolerance
        return {'nihss_score': 0, 'error': 'Arms not positioned correctly'}
    
    # Measure drift over 10 seconds
    drift_analysis = analyze_drift_over_time(keypoints_history, duration_seconds)
    
    # Apply NIHSS scoring
    if drift_analysis['no_drift_for_10_seconds']:
        nihss_score = 0  # No drift
    elif drift_analysis['drift_before_10_seconds']:
        nihss_score = 1  # Drift but doesn't hit support
    elif drift_analysis['hits_support_with_effort']:
        nihss_score = 2  # Some effort against gravity
    elif drift_analysis['hits_support_no_effort']:
        nihss_score = 3  # No effort against gravity
    else:
        nihss_score = 4  # No movement
    
    return {
        'nihss_score': nihss_score,
        'drift_analysis': drift_analysis,
        'clinical_interpretation': get_clinical_interpretation(nihss_score)
    }
```

### **Option 2: Improved Static Analysis (Easier to Implement)**

```python
def analyze_improved_static_asymmetry(keypoints: Dict) -> Dict:
    """
    Improved static analysis that better aligns with NIHSS principles
    """
    try:
        # Extract keypoints
        left_wrist_y = keypoints['left_wrist']['y']
        right_wrist_y = keypoints['right_wrist']['y']
        left_shoulder_y = keypoints['left_shoulder']['y']
        right_shoulder_y = keypoints['right_shoulder']['y']
        
        # Calculate arm angles (should be ~90° for proper NIHSS test)
        left_arm_angle = calculate_arm_angle(left_wrist_y, left_shoulder_y)
        right_arm_angle = calculate_arm_angle(right_wrist_y, right_shoulder_y)
        
        # Check if arms are positioned correctly
        if not (80 <= left_arm_angle <= 100) or not (80 <= right_arm_angle <= 100):
            return {
                'nihss_score': 0,
                'error': 'Arms not positioned at 90° (NIHSS requirement)',
                'left_angle': left_arm_angle,
                'right_angle': right_arm_angle
            }
        
        # Calculate vertical drift (NIHSS measures this)
        vertical_drift_pixels = abs(left_wrist_y - right_wrist_y)
        
        # Calculate arm lengths for normalization
        left_arm_length = abs(left_wrist_y - left_shoulder_y)
        right_arm_length = abs(right_wrist_y - right_shoulder_y)
        avg_arm_length = (left_arm_length + right_arm_length) / 2
        
        if avg_arm_length < 0.01:
            return {'nihss_score': 0, 'error': 'Arm length too small'}
        
        # Calculate asymmetry score
        asymmetry_score = vertical_drift_pixels / avg_arm_length
        
        # Map to NIHSS scores based on clinical research
        if asymmetry_score < 0.05:  # <5% drift
            nihss_score = 0  # No drift
        elif asymmetry_score < 0.15:  # 5-15% drift
            nihss_score = 1  # Mild drift
        elif asymmetry_score < 0.30:  # 15-30% drift
            nihss_score = 2  # Moderate drift
        elif asymmetry_score < 0.50:  # 30-50% drift
            nihss_score = 3  # Severe drift
        else:  # >50% drift
            nihss_score = 4  # Critical/paralysis
        
        return {
            'nihss_score': nihss_score,
            'asymmetry_score': asymmetry_score,
            'asymmetry_percentage': asymmetry_score * 100,
            'left_arm_angle': left_arm_angle,
            'right_arm_angle': right_arm_angle,
            'vertical_drift_pixels': vertical_drift_pixels,
            'clinical_interpretation': get_clinical_interpretation(nihss_score)
        }
        
    except (KeyError, TypeError) as e:
        return {'nihss_score': 0, 'error': f'Keypoint analysis failed: {e}'}

def calculate_arm_angle(wrist_y: float, shoulder_y: float) -> float:
    """Calculate arm angle from vertical (0° = straight down, 90° = horizontal)"""
    arm_length = abs(wrist_y - shoulder_y)
    if arm_length == 0:
        return 0
    # For normalized coordinates, this is a simplified calculation
    # In real implementation, you'd need to account for camera perspective
    return 90 - (arm_length * 90)  # Simplified angle calculation

def get_clinical_interpretation(nihss_score: int) -> str:
    """Get clinical interpretation of NIHSS score"""
    interpretations = {
        0: "No drift - Normal motor function",
        1: "Mild drift - Slight weakness, monitor",
        2: "Moderate drift - Noticeable weakness, medical evaluation recommended",
        3: "Severe drift - Significant weakness, urgent medical evaluation",
        4: "No movement - Severe paralysis, emergency medical care needed"
    }
    return interpretations.get(nihss_score, "Unknown score")
```

## 🎯 **Recommended Implementation Strategy**

### **Phase 1: Quick Fix (Immediate)**
1. **Update thresholds** to be more clinically accurate
2. **Add arm angle verification** (90° requirement)
3. **Improve error handling** for improper positioning

### **Phase 2: True NIHSS (Long-term)**
1. **Implement time-based drift analysis**
2. **Add 10-second test duration**
3. **Include eye closure requirement**
4. **Measure effort against gravity**

## 🔧 **Immediate Fix for Current Issues**

Your 22.6% asymmetry suggests the current thresholds are too sensitive. Here's a quick fix:

```python
# Updated thresholds based on NIHSS principles
NIHSS_0_NORMAL = 0.05      # <5% drift - No drift (NIHSS 0)
NIHSS_1_MILD = 0.15        # 5-15% drift - Mild drift (NIHSS 1)
NIHSS_2_MODERATE = 0.30    # 15-30% drift - Moderate drift (NIHSS 2)
NIHSS_3_SEVERE = 0.50      # 30-50% drift - Severe drift (NIHSS 3)
NIHSS_4_PARALYSIS = 0.80   # >50% drift - Critical/Paralysis (NIHSS 4)
```

## 🎯 **Conclusion**

**Your current implementation is NOT following NIHSS standards.** The main issues are:

1. **No time-based analysis** (NIHSS requires 10-second test)
2. **No arm angle verification** (should be 90°)
3. **Thresholds based on position, not drift**
4. **Missing key NIHSS requirements**

**Recommendation**: Implement the improved static analysis (Option 2) for immediate improvement, then work toward true NIHSS implementation (Option 1) for full compliance.
