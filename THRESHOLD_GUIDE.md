# 🎯 Perfect Threshold Guide for Stroke Detection

## 📊 **Current Threshold Analysis**

### **What We Found:**
- **Test Image**: 24.1% asymmetry → Always detects drift ✅
- **Your Real Camera**: 0.3% asymmetry → Should NOT detect drift ✅
- **Current Adaptive Threshold**: 
  - Large images (>500KB): 0.5% threshold
  - Small images: 1% threshold

## 🔧 **How to Find Your Perfect Threshold**

### **Step 1: Test Your Real Camera**
Run your iOS app and capture images with different arm positions:

```bash
# Test 1: Arms held steady
# Expected: No drift detected
# Look for: asymmetry_score around 0.003 (0.3%)

# Test 2: Slight arm lowering  
# Expected: Mild drift detected
# Look for: asymmetry_score around 0.008-0.015 (0.8-1.5%)

# Test 3: Obvious arm lowering
# Expected: Significant drift detected  
# Look for: asymmetry_score around 0.020+ (2%+)
```

### **Step 2: Analyze the Logs**
In your iOS app logs, look for:
```
DEBUG: Image analysis - brightness_asymmetry: 0.0023, texture_asymmetry: 0.0034, total_score: 0.0028
```

### **Step 3: Calculate Your Threshold**
```
Perfect Threshold = (Max No-Drift Score + Min Drift Score) / 2

Example:
- No drift max: 0.003 (0.3%)
- Mild drift min: 0.008 (0.8%)
- Perfect threshold: (0.003 + 0.008) / 2 = 0.0055 (0.55%)
```

## 🎛️ **Threshold Adjustment Options**

### **Option 1: Conservative (Fewer False Positives)**
```python
image_drift_threshold = 0.008  # 0.8% - Only detect obvious drift
```

### **Option 2: Balanced (Current Setting)**
```python
image_drift_threshold = 0.005  # 0.5% - Detect subtle drift
```

### **Option 3: Sensitive (More False Positives)**
```python
image_drift_threshold = 0.003  # 0.3% - Detect very subtle drift
```

## 🧪 **Testing Your Threshold**

### **Test Script:**
```bash
# Run the calibration tool
python3 threshold_calibration_tool.py

# Run threshold testing
python3 test_thresholds.py
```

### **Manual Testing:**
1. **Hold arms steady** → Should show "No drift detected"
2. **Lower one arm slightly** → Should show "Mild drift detected"  
3. **Lower one arm obviously** → Should show "Significant drift detected"

## 📈 **Expected Results by Scenario**

| Arm Position | Expected Asymmetry | Expected Result |
|-------------|-------------------|-----------------|
| Steady arms | 0.002-0.005 | No drift |
| Slight lowering | 0.006-0.015 | Mild drift |
| Obvious lowering | 0.016+ | Significant drift |

## 🔧 **How to Modify Threshold**

### **Edit lambda_with_rekognition.py:**
```python
# Line 356: For large real camera images
image_drift_threshold = 0.005  # Change this value

# Line 358: For smaller images  
image_drift_threshold = 0.01   # Change this value
```

### **Recommended Values:**
- **0.003** (0.3%) - Very sensitive, may have false positives
- **0.005** (0.5%) - **RECOMMENDED** - Balanced
- **0.008** (0.8%) - Conservative, fewer false positives
- **0.010** (1.0%) - Very conservative

## 🎯 **Perfect Threshold Formula**

```
Perfect Threshold = Your_Steady_Arms_Max + Safety_Margin

Where:
- Your_Steady_Arms_Max = Highest asymmetry when holding arms steady
- Safety_Margin = 0.002-0.003 (0.2-0.3%) buffer
```

## 🚨 **Red Flags to Watch For**

1. **Always detecting drift** → Threshold too low
2. **Never detecting drift** → Threshold too high  
3. **Inconsistent results** → Need more test data
4. **Severity doesn't match** → Check clinical scoring logic

## 📱 **Next Steps**

1. **Test with real camera** - Capture 10 images with steady arms
2. **Note asymmetry scores** - Find your baseline (should be ~0.003)
3. **Test with drift** - Lower arms and note new scores
4. **Adjust threshold** - Set to 0.5x your drift minimum
5. **Validate** - Test both steady and drifted positions

## 🎉 **Success Criteria**

✅ **Perfect threshold when:**
- Steady arms: 95%+ show "No drift"
- Drifted arms: 90%+ show "Drift detected"  
- Consistent results across multiple tests
- Severity matches visual assessment

Your current threshold (0.5% for large images) should work well for your real camera setup!
