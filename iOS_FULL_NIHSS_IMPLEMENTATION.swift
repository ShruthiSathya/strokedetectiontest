// iOS App Changes for Full NIHSS Implementation
// These are the key changes needed in your existing Swift files

// ============================================================================
// 1. TestViewModel.swift Changes
// ============================================================================

// Add new properties for NIHSS implementation
class TestViewModel: ObservableObject {
    // ... existing properties ...
    
    // NIHSS-specific properties
    @Published var keypointHistory: [KeypointSnapshot] = []
    @Published var eyeClosed: Bool = false
    @Published var armAngleVerified: Bool = false
    @Published var testDuration: Double = 0.0
    @Published var realTimeDrift: Double = 0.0
    @Published var nihssInstructions: String = "Position arms at 90° and close your eyes"
    
    // NIHSS test state
    @Published var isNihssTestActive: Bool = false
    @Published var nihssCountdown: Int = 10
    @Published var showNihssInstructions: Bool = false
    
    // ... existing code ...
    
    // MARK: - NIHSS Implementation Methods
    
    func startNihssTest() {
        print("🏥 Starting NIHSS Motor Arm Test...")
        
        // Reset NIHSS-specific state
        keypointHistory.removeAll()
        eyeClosed = false
        armAngleVerified = false
        testDuration = 0.0
        realTimeDrift = 0.0
        
        // Show NIHSS instructions
        showNihssInstructions = true
        nihssInstructions = "Position your arms at 90° with palms down"
        
        // Start arm angle verification
        startArmAngleVerification()
    }
    
    func verifyArmAngles(keypoints: [CGPoint]) {
        guard keypoints.count >= 4 else {
            armAngleVerified = false
            nihssInstructions = "Ensure all keypoints are detected"
            return
        }
        
        // Calculate arm angles (simplified for normalized coordinates)
        let leftWrist = keypoints[0]  // Assuming first keypoint is left wrist
        let rightWrist = keypoints[1]
        let leftShoulder = keypoints[2]
        let rightShoulder = keypoints[3]
        
        let leftArmLength = abs(leftWrist.y - leftShoulder.y)
        let rightArmLength = abs(rightWrist.y - rightShoulder.y)
        
        // For 90° arms, the arm length should be approximately 0.3 in normalized coordinates
        // This is a simplified calculation - in production, you'd need camera calibration
        let leftAngle = calculateArmAngle(armLength: leftArmLength)
        let rightAngle = calculateArmAngle(armLength: rightArmLength)
        
        print("🔍 Arm Angle Verification:")
        print("   Left arm angle: \(leftAngle)°")
        print("   Right arm angle: \(rightAngle)°")
        
        // Check if arms are positioned at 90° (with tolerance)
        if (80 <= leftAngle && leftAngle <= 100) && (80 <= rightAngle && rightAngle <= 100) {
            armAngleVerified = true
            nihssInstructions = "Arms positioned correctly. Now close your eyes."
            
            // Start eye closure detection
            startEyeClosureDetection()
        } else {
            armAngleVerified = false
            nihssInstructions = "Position arms at 90° (horizontal). Current: L:\(Int(leftAngle))° R:\(Int(rightAngle))°"
        }
    }
    
    func verifyEyeClosure() {
        // This would integrate with face detection to verify eyes are closed
        // For now, we'll use a manual verification approach
        eyeClosed = true  // In production, this would be determined by face detection
        nihssInstructions = "Eyes closed. Hold position for 10 seconds..."
        
        // Start the 10-second NIHSS test
        startNihssCountdown()
    }
    
    func startNihssCountdown() {
        nihssCountdown = 10
        isNihssTestActive = true
        
        // Start countdown timer
        Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] timer in
            guard let self = self else {
                timer.invalidate()
                return
            }
            
            if self.nihssCountdown > 1 {
                self.nihssCountdown -= 1
                print("🔢 NIHSS countdown: \(self.nihssCountdown)")
            } else {
                // Countdown finished, start 10-second test
                timer.invalidate()
                self.startTenSecondTest()
            }
        }
    }
    
    func startTenSecondTest() {
        print("🚀 Starting 10-second NIHSS test...")
        nihssInstructions = "Hold position for 10 seconds..."
        
        // Start collecting keypoint history
        startKeypointHistoryCollection()
        
        // Start 10-second timer
        Timer.scheduledTimer(withTimeInterval: 10.0, repeats: false) { [weak self] _ in
            self?.completeNihssTest()
        }
    }
    
    func startKeypointHistoryCollection() {
        // Collect keypoint snapshots every 0.5 seconds for 10 seconds
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] timer in
            guard let self = self else {
                timer.invalidate()
                return
            }
            
            // Get current keypoints from camera manager
            let currentKeypoints = self.cameraManager.latestKeypoints
            
            // Convert to snapshot format
            let snapshot = KeypointSnapshot(
                timestamp: Date().timeIntervalSince1970,
                keypoints: currentKeypoints
            )
            
            self.keypointHistory.append(snapshot)
            
            // Calculate real-time drift
            self.calculateRealTimeDrift()
            
            // Stop after 10 seconds (20 snapshots at 0.5s intervals)
            if self.keypointHistory.count >= 20 {
                timer.invalidate()
            }
        }
    }
    
    func calculateRealTimeDrift() {
        guard keypointHistory.count >= 2 else { return }
        
        let currentSnapshot = keypointHistory.last!
        let keypoints = currentSnapshot.keypoints
        
        guard let leftWrist = keypoints["left_wrist"],
              let rightWrist = keypoints["right_wrist"],
              let leftShoulder = keypoints["left_shoulder"],
              let rightShoulder = keypoints["right_shoulder"] else {
            return
        }
        
        // Calculate current asymmetry
        let verticalDrift = abs(leftWrist.y - rightWrist.y)
        let leftArmLength = abs(leftWrist.y - leftShoulder.y)
        let rightArmLength = abs(rightWrist.y - rightShoulder.y)
        let avgArmLength = (leftArmLength + rightArmLength) / 2
        
        if avgArmLength > 0.01 {
            realTimeDrift = verticalDrift / avgArmLength
        }
        
        print("📊 Real-time drift: \(realTimeDrift * 100)%")
    }
    
    func completeNihssTest() {
        print("✅ NIHSS test completed. Sending data to Lambda...")
        
        // Calculate total test duration
        if let firstSnapshot = keypointHistory.first,
           let lastSnapshot = keypointHistory.last {
            testDuration = lastSnapshot.timestamp - firstSnapshot.timestamp
        }
        
        // Send NIHSS data to Lambda
        sendNihssDataToAWS()
    }
    
    func sendNihssDataToAWS() {
        // Create NIHSS payload
        let nihssPayload = NihssPayload(
            keypoints_history: keypointHistory,
            test_duration: testDuration,
            eye_closed: eyeClosed,
            user_id: userID
        )
        
        // Send to Lambda (similar to existing sendImageToAWS method)
        sendNihssToAWS(payload: nihssPayload)
    }
    
    private func calculateArmAngle(armLength: Double) -> Double {
        // Simplified arm angle calculation for normalized coordinates
        // In production, you'd need proper camera calibration
        let estimatedArmLength = 0.3  // Approximate arm length in normalized coordinates
        let angleRadians = asin(min(armLength / estimatedArmLength, 1.0))
        return angleRadians * 180 / .pi
    }
}

// ============================================================================
// 2. New Data Structures
// ============================================================================

struct KeypointSnapshot: Codable {
    let timestamp: TimeInterval
    let keypoints: [String: KeypointData]
}

struct NihssPayload: Codable {
    let keypoints_history: [KeypointSnapshot]
    let test_duration: Double
    let eye_closed: Bool
    let user_id: String
}

// ============================================================================
// 3. TestView.swift Changes
// ============================================================================

struct TestView: View {
    @StateObject private var viewModel = TestViewModel()
    
    var body: some View {
        ZStack {
            // ... existing camera view code ...
            
            // NIHSS Instructions Overlay
            if viewModel.showNihssInstructions {
                VStack {
                    Text("🏥 NIHSS Motor Arm Test")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Text(viewModel.nihssInstructions)
                        .font(.title2)
                        .foregroundColor(.yellow)
                        .multilineTextAlignment(.center)
                        .padding()
                    
                    // Arm angle verification indicator
                    if viewModel.armAngleVerified {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("Arms positioned at 90°")
                                .foregroundColor(.green)
                        }
                        .font(.headline)
                    }
                    
                    // Eye closure verification indicator
                    if viewModel.eyeClosed {
                        HStack {
                            Image(systemName: "eye.slash.fill")
                                .foregroundColor(.blue)
                            Text("Eyes closed")
                                .foregroundColor(.blue)
                        }
                        .font(.headline)
                    }
                    
                    // NIHSS countdown
                    if viewModel.isNihssTestActive {
                        VStack {
                            Text("Starting test in:")
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            Text("\(viewModel.nihssCountdown)")
                                .font(.system(size: 48, weight: .bold))
                                .foregroundColor(.red)
                        }
                        .padding()
                    }
                    
                    // Real-time drift monitoring
                    if viewModel.testDuration > 0 {
                        VStack {
                            Text("Real-time Drift:")
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            Text("\(viewModel.realTimeDrift * 100, specifier: "%.1f")%")
                                .font(.title)
                                .fontWeight(.bold)
                                .foregroundColor(viewModel.realTimeDrift > 0.15 ? .red : .green)
                        }
                        .padding()
                    }
                }
                .padding()
                .background(Color.black.opacity(0.8))
                .cornerRadius(15)
            }
            
            // ... existing UI code ...
        }
    }
}

// ============================================================================
// 4. CameraManager.swift Changes
// ============================================================================

extension CameraManager {
    // Add method to get current keypoints in the format needed for NIHSS
    func getCurrentKeypointsForNihss() -> [String: KeypointData] {
        var keypointData: [String: KeypointData] = [:]
        
        for (key, point) in latestKeypoints {
            keypointData[key] = KeypointData(x: point.x, y: point.y)
        }
        
        return keypointData
    }
    
    // Add face detection for eye closure (simplified)
    func detectEyeClosure() -> Bool {
        // This would integrate with Vision framework's face detection
        // For now, return a placeholder
        // In production, you'd use VNDetectFaceRectanglesRequest
        return false  // Placeholder
    }
}

// ============================================================================
// 5. Integration with Existing Code
// ============================================================================

// Update the existing startDriftTest method to use NIHSS
private func startDriftTest() {
    // Instead of the old test, start NIHSS test
    startNihssTest()
}

// Update the button text to reflect NIHSS
private func buttonText(for state: TestViewModel.AppState) -> String {
    switch state {
    case .setup:
        return "START NIHSS TEST"
    case .calibrating:
        if viewModel.isCalibrated {
            return "START NIHSS TEST"
        } else {
            return "CALIBRATING..."
        }
    // ... rest of the cases
    }
}
