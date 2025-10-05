// MARK: - Bug Fix for iOS App Result State Logic
// Replace the switch statement in TestViewModel.swift around line 594

// BEFORE (INCORRECT):
switch response.severity {
case "critical":
    self.appState = .resultPositive
case "warning":  
    self.appState = .resultPositive
case "mild":
    self.appState = .resultNegative  // ❌ WRONG!
default: // "normal" and "moderate" both go here
    self.appState = .resultNegative  // ❌ WRONG for "moderate"!
}

// AFTER (CORRECT):
switch response.severity {
case "critical":
    self.appState = .resultPositive
    detailedMessage = """
    🚨 CLINICAL ALERT 🚨
    
    \(response.message ?? "Significant findings detected.")
    
    📊 Clinical Data:
    • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
    • Clinical Score: \(self.clinicalScore)/4
    • Test Quality: \(quality)
    
    ⚠️ Seek immediate medical evaluation.
    """
    
case "severe":
    self.appState = .resultPositive
    detailedMessage = """
    🚨 SEVERE DRIFT DETECTED 🚨
    
    \(response.message ?? "Severe drift detected.")
    
    📊 Clinical Data:
    • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
    • Clinical Score: \(self.clinicalScore)/4
    • Test Quality: \(quality)
    
    ⚠️ Urgent medical evaluation recommended.
    """
    
case "moderate":  // ✅ ADD THIS CASE!
    self.appState = .resultPositive  // ✅ CORRECT!
    detailedMessage = """
    🔶 MODERATE DRIFT DETECTED 🔶
    
    \(response.message ?? "Moderate drift detected.")
    
    📊 Clinical Data:
    • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
    • Clinical Score: \(self.clinicalScore)/4
    • Test Quality: \(quality)
    
    💡 Consider medical consultation.
    """
    
case "mild":
    self.appState = .resultPositive  // ✅ FIXED: mild should also be positive
    detailedMessage = """
    ⚠️ MILD DRIFT DETECTED ⚠️
    
    \(response.message ?? "Mild drift detected.")
    
    📊 Clinical Data:
    • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
    • Clinical Score: \(self.clinicalScore)/4
    • Test Quality: \(quality)
    
    👀 Monitor for other symptoms.
    """
    
default: // "normal" only
    self.appState = .resultNegative
    detailedMessage = """
    ✅ Normal Results
    
    \(response.message ?? "No abnormal findings detected.")
    
    📊 Clinical Data:
    • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
    • Clinical Score: \(self.clinicalScore)/4
    • Test Quality: \(quality)
    
    🎉 Test complete.
    """
}
self.alertMessage = detailedMessage
self.showFullAlert = true
