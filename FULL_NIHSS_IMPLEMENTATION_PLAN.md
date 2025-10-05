# Full NIHSS Motor Arm Test Implementation Plan

## 🎯 **NIHSS Motor Arm Test Requirements (Item 5)**

### **Official NIHSS Protocol:**
1. **Patient Positioning**: Sitting or supine
2. **Arm Position**: 90° (sitting) or 45° (supine) with palms down
3. **Eye Closure**: Patient closes eyes
4. **Duration**: Hold position for 10 seconds while counting
5. **Measurement**: Observe drift over time and effort against gravity

### **NIHSS Scoring Criteria:**
- **0** = No drift; limb holds 90° (or 45°) for full 10 seconds
- **1** = Drift; limb holds 90° (or 45°) but drifts down before full 10 seconds; does not hit bed or other support
- **2** = Some effort against gravity; limb falls to bed or other support but has some effort against gravity
- **3** = No effort against gravity; limb falls to bed or other support without any effort against gravity
- **4** = No movement; limb is completely paralyzed

## 🏗️ **Implementation Architecture**

### **Phase 1: iOS App Changes**
1. **Test Duration**: Extend from current test to 10 seconds
2. **Eye Closure Detection**: Add face detection to verify eyes are closed
3. **Arm Angle Verification**: Check if arms are positioned at 90°
4. **Real-time Drift Monitoring**: Track keypoint positions over time
5. **NIHSS Instructions**: Update UI with proper NIHSS instructions

### **Phase 2: Lambda Function Changes**
1. **Time-series Analysis**: Process keypoint data over 10 seconds
2. **Drift Over Time**: Calculate drift progression during test
3. **Arm Angle Validation**: Verify 90° positioning
4. **NIHSS Scoring**: Apply official NIHSS scoring criteria
5. **Clinical Interpretation**: Provide detailed clinical assessment

### **Phase 3: Data Structure Changes**
1. **Keypoint History**: Send multiple keypoint snapshots over time
2. **Metadata**: Include test duration, eye closure status, arm angles
3. **Quality Metrics**: Track keypoint stability and detection quality

## 📱 **iOS App Implementation**

### **1. TestViewModel.swift Changes**
- Extend test duration to 10 seconds
- Add keypoint history tracking
- Implement eye closure detection
- Add arm angle verification
- Send time-series data to Lambda

### **2. TestView.swift Changes**
- Update UI with NIHSS instructions
- Add eye closure prompt
- Show arm angle feedback
- Display real-time drift monitoring
- Add countdown timer for 10 seconds

### **3. CameraManager.swift Changes**
- Add face detection for eye closure
- Implement arm angle calculation
- Track keypoint stability over time
- Send periodic keypoint updates

## 🚀 **Lambda Function Implementation**

### **1. Time-series Analysis**
- Process keypoint data over 10-second period
- Calculate drift progression
- Detect when arms hit support surface
- Measure effort against gravity

### **2. NIHSS Scoring Algorithm**
- Apply official NIHSS criteria
- Consider drift timing and severity
- Account for arm angle compliance
- Provide clinical interpretation

### **3. Enhanced Response**
- Detailed drift analysis
- NIHSS score with justification
- Clinical recommendations
- Quality assessment

## 🔧 **Technical Implementation Details**

### **Keypoint History Data Structure**
```json
{
  "keypoints_history": [
    {
      "timestamp": 0.0,
      "keypoints": {
        "left_wrist": {"x": 0.5, "y": 0.6},
        "right_wrist": {"x": 0.5, "y": 0.6},
        "left_shoulder": {"x": 0.4, "y": 0.3},
        "right_shoulder": {"x": 0.6, "y": 0.3}
      }
    },
    {
      "timestamp": 1.0,
      "keypoints": { ... }
    }
  ],
  "test_duration": 10.0,
  "eye_closed": true,
  "arm_angle_verified": true,
  "user_id": "test_user"
}
```

### **NIHSS Analysis Algorithm**
```python
def analyze_nihss_motor_arm(keypoints_history, test_duration, eye_closed, arm_angle_verified):
    # 1. Verify test conditions
    if not eye_closed:
        return {"error": "Eyes must be closed for NIHSS test"}
    
    if not arm_angle_verified:
        return {"error": "Arms must be positioned at 90°"}
    
    if test_duration < 10:
        return {"error": "Test must be at least 10 seconds"}
    
    # 2. Analyze drift over time
    drift_analysis = analyze_drift_progression(keypoints_history)
    
    # 3. Apply NIHSS scoring
    nihss_score = calculate_nihss_score(drift_analysis)
    
    # 4. Return clinical assessment
    return {
        "nihss_score": nihss_score,
        "drift_analysis": drift_analysis,
        "clinical_interpretation": get_clinical_meaning(nihss_score)
    }
```

## 📊 **Expected Outcomes**

### **Improved Accuracy**
- **Time-based analysis** instead of single snapshot
- **NIHSS-compliant scoring** based on official criteria
- **Better clinical relevance** for stroke detection

### **Enhanced User Experience**
- **Clear NIHSS instructions** for proper test execution
- **Real-time feedback** on arm positioning
- **Professional medical assessment** based on established standards

### **Clinical Validation**
- **NIHSS compliance** with official stroke scale
- **Research-based thresholds** from clinical studies
- **Standardized assessment** comparable to clinical evaluations

## 🎯 **Implementation Priority**

### **Phase 1 (High Priority)**
1. Extend test duration to 10 seconds
2. Add arm angle verification
3. Implement keypoint history tracking
4. Update Lambda function for time-series analysis

### **Phase 2 (Medium Priority)**
1. Add eye closure detection
2. Implement real-time drift monitoring
3. Add NIHSS-compliant UI instructions
4. Enhance clinical interpretation

### **Phase 3 (Low Priority)**
1. Add support surface detection
2. Implement effort against gravity measurement
3. Add advanced quality metrics
4. Optimize performance for real-time analysis

## 🚀 **Next Steps**

1. **Start with Phase 1** - Extend test duration and add arm angle verification
2. **Update Lambda function** to handle keypoint history
3. **Test with current app** to ensure compatibility
4. **Gradually add Phase 2 features** for full NIHSS compliance
5. **Validate with clinical experts** for accuracy

This implementation will make your app truly NIHSS-compliant and provide accurate stroke detection based on established clinical standards.
