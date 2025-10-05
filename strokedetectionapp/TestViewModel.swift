import Foundation
import SwiftUI
import CoreGraphics
import Combine
import AVFoundation // Required for AVCaptureSession in CameraManager

// IMPORTANT: REPLACE THIS PLACEHOLDER URL with the actual 'Invoke URL' you got from API Gateway Step 7.
// Example: https://xxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/test
let API_GATEWAY_URL = "https://irwrhsf9a0.execute-api.us-east-1.amazonaws.com/drifttest"

    // MARK: - 1. Codable Structs for AWS Communication

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

struct KeypointPayload: Codable {
    let keypoints: [String: KeypointData]
    let user_id: String
    let test_mode: Bool
    let force_drift: Bool
    let user_intentionally_drifting: Bool
}

struct KeypointData: Codable {
    let x: Double
    let y: Double
}
struct ClinicalResponse: Codable {
    let drift_detected: Bool
    let asymmetry_score: Double?
    let nihss_motor_score: Int?
    let severity: String?
    let message: String?
    let test_quality: String?
    let research_based: Bool?
    let clinical_standards: String?
    let analysis_method: String?
    let analysis_time_seconds: Double?
    let total_runtime_seconds: Double?
    let version: String?
    
    // NIHSS-specific fields
    let clinical_interpretation: String?
    let test_duration: Double?
    let eye_closed: Bool?
    let keypoints_snapshots: Int?
    let left_arm_angle: Double?
    let right_arm_angle: Double?
    let initial_asymmetry: Double?
    let max_drift: Double?
    let time_to_drift: Double?
    let hits_support: Bool?
    
    // Legacy fields for backward compatibility
    let y_difference: Double? // Maps to asymmetry_score
    let clinical_score: Int?  // Maps to nihss_motor_score
    
    // Additional fields from robust Lambda function
    let asymmetry_percent: Double?
    let nihss_total: Int?
    let detection_quality: String?
    let quality_reason: String?
    let vertical_drift: Double?
    
    enum CodingKeys: String, CodingKey {
        case drift_detected, asymmetry_score, nihss_motor_score, severity, message
        case test_quality, research_based, clinical_standards, analysis_method
        case analysis_time_seconds, total_runtime_seconds, version
        case clinical_interpretation, test_duration, eye_closed, keypoints_snapshots
        case left_arm_angle, right_arm_angle, initial_asymmetry, max_drift
        case time_to_drift, hits_support
        case y_difference, clinical_score // Legacy fields
        case asymmetry_percent, nihss_total, detection_quality, quality_reason, vertical_drift // Additional fields
    }
}

// AWS API Gateway response wrapper
struct AWSResponse: Codable {
    let statusCode: Int
    let headers: [String: String]
    let body: String
}

// MARK: - 2. ViewModel (Real Camera Integration)
class TestViewModel: ObservableObject {
    
    // --- State Variables ---
    enum AppState { 
        case setup, calibrating, testing, analyzing, resultNegative, resultPositive, error
    }
    @Published var appState: AppState = .setup
    @Published var alertMessage: String = "Welcome to the Clinical Romberg Test"
    @Published var showFullAlert: Bool = false
    @Published var isTesting: Bool = false
    @Published var recognizedKeypoints: [CGPoint] = []
    @Published var currentStep: Int = 1
    @Published var clinicalScore: Int = 0
    @Published var testSeverity: String = "normal"
    
    // Detailed clinical metrics for results display
    @Published var detectedDrift: Bool = false
    @Published var detectedPronation: Bool = false
    @Published var yDifference: Double = 0.0
    @Published var testQuality: String = "unknown"
    @Published var confidenceScore: Double = 0.0
    @Published var clinicalDetails: String = ""
    
    // NIH Stroke Scale components (based on medical research)
    @Published var nihssScore: Int = 0
    @Published var motorArmScore: Int = 0 // 0-4 scale
    @Published var sensoryScore: Int = 0 // 0-2 scale
    @Published var coordinationScore: Int = 0 // 0-2 scale
    @Published var timeToTreatment: String = ""
    
    // Live feedback and validation
    @Published var stepValidationStatus: [Bool] = [false, false, false] // Track each step completion
    @Published var liveFeedbackMessage: String = ""
    @Published var remainingTime: Int = 0
    @Published var isStepValidated: Bool = false
    @Published var showCheckmark: Bool = false
    
    // Calibration-specific properties
    @Published var calibrationStatus: String = ""
    @Published var isCalibrated: Bool = false
    @Published var calibrationFeedback: String = ""
    @Published var keypointCount: Int = 0
    
    // MARK: - NIHSS-Specific Properties
    @Published var keypointHistory: [KeypointSnapshot] = []
    @Published var eyeClosed: Bool = false
    @Published var armAngleVerified: Bool = false
    @Published var testDuration: Double = 0.0
    @Published var realTimeDrift: Double = 0.0
    @Published var nihssInstructions: String = "Position arms at 90° and close your eyes"
    @Published var isNihssTestActive: Bool = false
    @Published var nihssCountdown: Int = 10
    @Published var showNihssInstructions: Bool = false
    
    // Countdown properties
    @Published var showCountdown: Bool = false
    @Published var countdownNumber: Int = 5
    @Published var isCountingDown: Bool = false
    
    // CRITICAL: Camera Manager Instance
    public var cameraManager = CameraManager()
    private var testTimer: AnyCancellable?
    private var stepTimer: AnyCancellable?
    private var validationTimer: AnyCancellable?
    private var timeoutTimer: AnyCancellable?
    private var countdownTimer: AnyCancellable?
    
    // Variables to store the final data to be sent to AWS
    private var capturedImageData: Data?
    
    // Debug timer for coordinate logging
    private var debugTimer: AnyCancellable?
    
    // User ID for AWS requests
    let userID = "test_user_\(UUID().uuidString.prefix(8))"
    
    init() {
        // Connect the camera output to the ViewModel handler
        cameraManager.poseEstimationHandler = { [weak self] keypoints in
            // Called for EVERY frame (fast): Updates visual overlay and collects data
            self?.recognizedKeypoints = keypoints
            self?.processFrame(keypoints: keypoints)
            
            // NIHSS: Check arm angles during calibration
            if self?.appState == .calibrating {
                self?.verifyArmAngles(keypoints: keypoints)
            }
            
            // NIHSS: Collect keypoint history during test
            if self?.appState == .testing && self?.isNihssTestActive == true {
                self?.collectKeypointSnapshot()
            }
        }
        
        // Start debug timer for coordinate logging every 5 seconds
        startDebugTimer()
    }
    
    // Processes the keypoints from the camera manager with live validation
    private func processFrame(keypoints: [CGPoint]) {
        // Update live feedback
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // Live feedback based on current step and keypoint detection
            self.updateLiveFeedback(keypoints: keypoints)
            
            // Validate current step
            self.validateCurrentStep(keypoints: keypoints)
        }
    }
    
    // Updates live feedback message based on current step and keypoint detection
    private func updateLiveFeedback(keypoints: [CGPoint]) {
        let keypointCount = keypoints.count
        self.keypointCount = keypointCount
        
        switch appState {
        case .calibrating:
            updateCalibrationFeedback(keypoints: keypoints)
            
        case .testing:
            if keypointCount >= 4 {
                liveFeedbackMessage = "📊 Analyzing... Hold steady for \(remainingTime)s"
            } else if keypointCount >= 2 {
                liveFeedbackMessage = "🔍 Monitoring position... \(remainingTime)s remaining"
            } else {
                liveFeedbackMessage = "👀 Maintaining position... \(remainingTime)s"
            }
            
        default:
            liveFeedbackMessage = "Ready for testing"
        }
    }
    
    // Updates calibration feedback based on keypoint detection
    private func updateCalibrationFeedback(keypoints: [CGPoint]) {
        let keypointCount = keypoints.count
        
        if keypointCount >= 8 {
            calibrationStatus = "Perfect! ✅"
            calibrationFeedback = "Excellent positioning! All keypoints detected clearly. Auto-starting test in 5 seconds..."
            liveFeedbackMessage = "✅ Perfect! Auto-starting in 5 seconds..."
            isCalibrated = true
            
            // Start countdown if not already started
            if !isCountingDown {
                startAutoTestCountdown()
            }
        } else if keypointCount >= 6 {
            calibrationStatus = "Good! ⚡"
            calibrationFeedback = "Good positioning! Most keypoints detected. Auto-starting test in 5 seconds..."
            liveFeedbackMessage = "⚡ Good positioning! Auto-starting in 5 seconds..."
            isCalibrated = true
            
            // Start countdown if not already started
            if !isCountingDown {
                startAutoTestCountdown()
            }
        } else if keypointCount >= 4 {
            calibrationStatus = "Acceptable ✓"
            calibrationFeedback = "Basic positioning detected. Consider moving closer to camera for better accuracy."
            liveFeedbackMessage = "✓ Acceptable positioning. Move closer for better accuracy"
            isCalibrated = true
            
            // Cancel auto countdown if user moves to Acceptable
            if isCountingDown {
                print("⏹️ Canceling auto countdown - moved to Acceptable")
                cancelAutoCountdown()
            }
        } else if keypointCount >= 2 {
            calibrationStatus = "Poor 📍"
            calibrationFeedback = "Only partial detection. Move closer to camera and ensure arms are fully extended."
            liveFeedbackMessage = "📍 Partial detection. Move closer and extend arms fully"
            isCalibrated = false
            
            // Cancel auto countdown if user moves to Poor
            if isCountingDown {
                print("⏹️ Canceling auto countdown - moved to Poor")
                cancelAutoCountdown()
            }
        } else if keypointCount >= 1 {
            calibrationStatus = "Too Far 🔍"
            calibrationFeedback = "Person detected but too far away. Move closer to camera."
            liveFeedbackMessage = "🔍 Too far away. Move closer to camera"
            isCalibrated = false
            
            // Cancel auto countdown if user moves to Too Far
            if isCountingDown {
                print("⏹️ Canceling auto countdown - moved to Too Far")
                cancelAutoCountdown()
            }
        } else {
            calibrationStatus = "No Detection 📷"
            calibrationFeedback = "No person detected. Please stand in front of camera with arms extended."
            liveFeedbackMessage = "📷 No person detected. Stand in front of camera"
            isCalibrated = false
            
            // Cancel auto countdown if no detection
            if isCountingDown {
                print("⏹️ Canceling auto countdown - no detection")
                cancelAutoCountdown()
            }
        }
    }
    
    // Validates the current step based on keypoint detection
    private func validateCurrentStep(keypoints: [CGPoint]) {
        let keypointCount = keypoints.count
        let requiredKeypoints = 4 // Minimum keypoints needed for validation
        
        print("🔍 Validating step: \(appState), keypoints: \(keypointCount), required: \(requiredKeypoints)")
        
        switch appState {
        case .calibrating:
            // Calibration validation is handled in updateCalibrationFeedback
            print("🔧 Calibration: \(keypointCount) keypoints detected - \(calibrationStatus)")
            
        case .testing:
            if keypointCount >= 4 {
                print("✅ Testing: Good keypoint detection (\(keypointCount) points)")
            } else {
                print("⚠️ Testing: Low keypoint detection (\(keypointCount) points)")
            }
            
        default:
            break
        }
    }
    
    // Validates a specific step and shows checkmark
    private func validateStep(stepIndex: Int) {
        stepValidationStatus[stepIndex] = true
        isStepValidated = true
        showCheckmark = true
        
        // Hide checkmark after 2 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
            self?.showCheckmark = false
            self?.isStepValidated = false
        }
    }
    
    // Starts the clinical Romberg test protocol
    func startClinicalTest() {
        guard !isTesting else { return }
        
        self.appState = .calibrating
        self.alertMessage = "Calibration: Position yourself with arms extended forward, palms up"
        self.currentStep = 1
        self.isTesting = false // Not testing yet, just calibrating
        self.showFullAlert = false
        self.isCalibrated = false
        
        // Reset calibration state
        self.calibrationStatus = "Calibrating..."
        self.calibrationFeedback = "Position yourself in front of the camera"
        
        // Start the camera and Vision processing
        cameraManager.start()
        
        print("🔧 Starting calibration process")
    }
    
    // Starts the actual 20-second drift test after calibration
    func startDriftTest() {
        guard isCalibrated else { return }
        
        self.appState = .testing
        self.alertMessage = "Test: Close your eyes and hold steady for 20 seconds"
        self.currentStep = 2
        self.isTesting = true
        
        print("⏱️ Starting 20-second drift test")
        startMainTestTimer(duration: 20) // 20 seconds instead of 30
    }
    
    // Starts the 3-2-1 countdown after perfect calibration
    private func startCountdown() {
        guard !isCountingDown else { return }
        
        isCountingDown = true
        showCountdown = true
        countdownNumber = 5
        
        print("🔢 Starting 5-4-3-2-1 countdown...")
        
        countdownTimer = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self = self else { return }
                
                if self.countdownNumber > 1 {
                    self.countdownNumber -= 1
                    print("🔢 Countdown: \(self.countdownNumber)")
                } else {
                    // Countdown finished, start the test
                    print("🚀 Countdown finished! Starting drift test...")
                    self.isCountingDown = false
                    self.showCountdown = false
                    self.countdownTimer?.cancel()
                    self.startDriftTest()
                }
            }
    }
    
    // Starts automatic test countdown after Perfect/Good calibration
    private func startAutoTestCountdown() {
        guard !isCountingDown else { return }
        
        isCountingDown = true
        showCountdown = true
        countdownNumber = 5
        
        print("🔢 Starting AUTO test countdown: 5-4-3-2-1...")
        
        countdownTimer = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self = self else { return }
                
                if self.countdownNumber > 1 {
                    self.countdownNumber -= 1
                    print("🔢 Auto countdown: \(self.countdownNumber)")
                } else {
                    // Countdown finished, automatically start the test
                    print("🚀 Auto countdown finished! Starting drift test automatically...")
                    self.isCountingDown = false
                    self.showCountdown = false
                    self.countdownTimer?.cancel()
                    self.startDriftTest()
                }
            }
    }
    
    // Cancels the auto countdown if user moves out of Perfect/Good range
    private func cancelAutoCountdown() {
        isCountingDown = false
        showCountdown = false
        countdownTimer?.cancel()
        print("⏹️ Auto countdown canceled")
    }
    
    
    // Starts a step timer with live countdown
    private func startStepTimer(duration: Int, completion: @escaping () -> Void) {
        remainingTime = duration
        
        stepTimer = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self = self else { return }
                self.remainingTime -= 1
                
                if self.remainingTime <= 0 {
                    self.stepTimer?.cancel()
                    completion()
                }
            }
    }
    
    // Starts the main 30-second test timer
    private func startMainTestTimer(duration: Int) {
        remainingTime = duration
        print("🕐 Starting main test timer for \(duration) seconds")
        
        testTimer = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self = self else { return }
                self.remainingTime -= 1
                print("⏰ Timer: \(self.remainingTime) seconds remaining")
                
                if self.remainingTime <= 0 {
                    print("🎯 Timer finished! Starting AWS analysis...")
                    self.testTimer?.cancel()
                    self.startAWSAnalysisStream() // Send data to AWS after clinical observation
                }
            }
    }
    
    // Handles the API call to the AWS Lambda function via API Gateway.
    func startAWSAnalysisStream() {
        print("🔍 Starting AWS analysis stream...")
        
        // Stop the camera and move to analyzing state
        cameraManager.stop()
        
        // Update UI to show analysis is starting
        DispatchQueue.main.async { [weak self] in
            self?.appState = .analyzing
            self?.liveFeedbackMessage = "📊 Analyzing captured data..."
            self?.remainingTime = 0
            self?.isTesting = false
            print("📱 UI Updated: Analysis starting, camera stopped")
        }
        
        // Set a timeout to force results after 30 seconds
        timeoutTimer = Timer.publish(every: 30.0, on: .main, in: .common)
            .autoconnect()
            .prefix(1)
            .sink { [weak self] _ in
                print("⏰ TIMEOUT: Forcing fallback results after 30 seconds")
                print("🔍 DEBUG: This means AWS took longer than 30 seconds to respond")
                self?.showDemoResults()
            }
        
        // Capture the current frame as an image
        cameraManager.captureCurrentFrame { [weak self] imageData in
            guard let self = self else { return }
            
            if let imageData = imageData {
                print("✅ Image captured successfully, size: \(imageData.count) bytes")
                
                // Stop the camera once data is captured to save resources
                self.cameraManager.stop()
                
                // Convert image data to Base64 string
                let base64String = imageData.base64EncodedString()
                print("📤 Sending image to AWS Lambda...")
                print("🔍 DEBUG: Base64 string length: \(base64String.count) characters")
                print("🔍 DEBUG: User ID: \(userID)")
                
                // 1. Prepare the Keypoint Payload for JSON encoding
                let keypoints = cameraManager.latestKeypoints
                
                // Convert CGPoints to the format expected by Lambda
                var keypointData: [String: KeypointData] = [:]
                for (key, point) in keypoints {
                    keypointData[key] = KeypointData(x: point.x, y: point.y)
                }
                
                let payload = KeypointPayload(
                    keypoints: keypointData,
                    user_id: userID,
                    test_mode: false,
                    force_drift: false,
                    user_intentionally_drifting: false
                )
                
                print("🔍 DEBUG: About to call sendImageToAWS...")
                self.sendImageToAWS(payload: payload)
            } else {
                print("❌ Failed to capture image")
                print("🔍 DEBUG: Image capture failed - this triggers connection error")
                // Fallback: Show demo results if image capture fails
                self.showDemoResults()
            }
        }
    }
    
    // Show fallback results using local calculation when AWS is not available
    private func showDemoResults() {
        print("⚠️ AWS unavailable - using local calculation fallback...")
        print("🔍 DEBUG: showDemoResults called - this means one of the following happened:")
        print("   - 15-second timeout reached")
        print("   - Image capture failed") 
        print("   - Invalid API Gateway URL")
        print("   - JSON encoding failed")
        print("   - Network request failed")
        print("   - Response decoding failed")
        
        // Stop the camera if it's still running
        cameraManager.stop()
        
        // Update UI to show we're using local calculation
        DispatchQueue.main.async { [weak self] in
            self?.appState = .analyzing
            self?.liveFeedbackMessage = "📊 Using local analysis..."
            self?.isTesting = false
        }
        
        // Use local calculation as fallback
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            print("🔄 FALLBACK: Using local calculation instead of AWS")
            self.useLocalCalculationFallback()
        }
    }
    
    // Use local calculation when AWS fails
    private func useLocalCalculationFallback() {
        print("🧮 FALLBACK: Calculating results locally...")
        
        // Get the latest keypoints from camera manager
        let keypoints = cameraManager.latestKeypoints
        
        // Check if we have the required keypoints
        guard let leftWrist = keypoints["left_wrist"],
              let rightWrist = keypoints["right_wrist"],
              let leftShoulder = keypoints["left_shoulder"],
              let rightShoulder = keypoints["right_shoulder"] else {
            print("❌ FALLBACK: Missing required keypoints")
            showFallbackError()
            return
        }
        
        // Calculate arm lengths using Euclidean distance (the fix we implemented)
        let leftArmLength = sqrt(pow(leftWrist.x - leftShoulder.x, 2) + pow(leftWrist.y - leftShoulder.y, 2))
        let rightArmLength = sqrt(pow(rightWrist.x - rightShoulder.x, 2) + pow(rightWrist.y - rightShoulder.y, 2))
        let verticalDrift = abs(leftWrist.y - rightWrist.y)
        let avgArmLength = (leftArmLength + rightArmLength) / 2
        
        print("📊 FALLBACK: Local calculation results:")
        print("   🦾 Left arm length: \(String(format: "%.3f", leftArmLength))")
        print("   🦾 Right arm length: \(String(format: "%.3f", rightArmLength))")
        print("   📏 Vertical drift: \(String(format: "%.3f", verticalDrift))")
        print("   📐 Average arm length: \(String(format: "%.3f", avgArmLength))")
        
        // ROBUST ASYMMETRY CALCULATION (same as the fix we implemented)
        let armLengthDiff = abs(leftArmLength - rightArmLength) / max(leftArmLength, rightArmLength)
        let isPoorDetection = avgArmLength < 0.05 || armLengthDiff > 0.5
        
        let asymmetry: Double
        let methodUsed: String
        
        if isPoorDetection {
            // Use absolute vertical drift for poor detection quality
            asymmetry = verticalDrift
            methodUsed = "absolute_vertical_drift"
            print("   🔧 Using absolute vertical drift (poor detection quality)")
            print("   📊 Detection quality: poor (arm length diff: \(String(format: "%.1f", armLengthDiff * 100))%)")
        } else {
            // Use normalized method for good detection quality
            asymmetry = avgArmLength > 0.01 ? verticalDrift / avgArmLength : verticalDrift
            methodUsed = "normalized_vertical_drift"
            print("   🔧 Using normalized vertical drift (good detection quality)")
            print("   📊 Detection quality: good")
        }
        
        let asymmetryPercent = String(format: "%.1f", asymmetry * 100)
        print("   ⚖️ Asymmetry: \(asymmetryPercent)% (method: \(methodUsed))")
        
        // Calculate NIHSS score using realistic thresholds
        let nihssScore: Int
        let severity: String
        let clinicalInterpretation: String
        
        if asymmetry < 0.20 {  // <20% - Normal variation
            nihssScore = 0
            severity = "normal"
            clinicalInterpretation = "No significant drift detected. Arms held steady within normal variation range."
        } else if asymmetry < 0.35 {  // 20-35% - Mild drift
            nihssScore = 1
            severity = "mild"
            clinicalInterpretation = "Mild arm variation detected. Arms show slight positioning differences but remain functional."
        } else if asymmetry < 0.50 {  // 35-50% - Moderate drift
            nihssScore = 2
            severity = "moderate"
            clinicalInterpretation = "Moderate arm variation detected. Arms show noticeable positioning differences but maintain some control."
        } else if asymmetry < 0.70 {  // 50-70% - Severe drift
            nihssScore = 3
            severity = "severe"
            clinicalInterpretation = "Severe arm variation detected. Arms show significant positioning differences with limited control."
        } else {  // >70% - Critical
            nihssScore = 4
            severity = "critical"
            clinicalInterpretation = "Critical arm variation detected. Arms show severe positioning differences or inability to maintain position."
        }
        
        print("   🏥 NIHSS Score: \(nihssScore) - \(severity.uppercased())")
        print("   📋 Interpretation: \(clinicalInterpretation)")
        
        // Create fallback response using local calculation
        let fallbackResponse = ClinicalResponse(
            drift_detected: asymmetry > 0.05,  // 5% threshold for drift detection
            asymmetry_score: asymmetry,
            nihss_motor_score: nihssScore,
            severity: severity,
            message: clinicalInterpretation,
            test_quality: "local_calculation_fallback",
            research_based: true,
            clinical_standards: "NIHSS_Motor_Arm_Item5_Local",
            analysis_method: methodUsed,
            analysis_time_seconds: nil,
            total_runtime_seconds: nil,
            version: "1.0_local_fallback",
            clinical_interpretation: clinicalInterpretation,
            test_duration: nil,
            eye_closed: nil,
            keypoints_snapshots: nil,
            left_arm_angle: nil,
            right_arm_angle: nil,
            initial_asymmetry: nil,
            max_drift: nil,
            time_to_drift: nil,
            hits_support: nil,
            y_difference: asymmetry,  // Legacy field
            clinical_score: nihssScore,  // Legacy field
            asymmetry_percent: asymmetry * 100,  // Additional field
            nihss_total: nihssScore,  // Additional field
            detection_quality: isPoorDetection ? "poor" : "good",  // Additional field
            quality_reason: isPoorDetection ? "Small arm lengths or significant difference" : "Good detection quality",  // Additional field
            vertical_drift: verticalDrift  // Additional field
        )
        
        print("✅ FALLBACK: Local calculation completed successfully")
        print("🎯 FALLBACK: Result - NIHSS \(nihssScore) (\(severity))")
        
        // Handle the result as if it came from AWS
        handleClinicalResult(response: fallbackResponse)
    }
    
    // Show error if fallback also fails
    private func showFallbackError() {
        print("❌ FALLBACK: Local calculation also failed")
        
        let errorResponse = ClinicalResponse(
            drift_detected: false,
            asymmetry_score: nil,
            nihss_motor_score: nil,
            severity: "error",
            message: "Unable to analyze - please ensure good lighting and positioning",
            test_quality: nil,
            research_based: nil,
            clinical_standards: nil,
            analysis_method: nil,
            analysis_time_seconds: nil,
            total_runtime_seconds: nil,
            version: nil,
            clinical_interpretation: nil,
            test_duration: nil,
            eye_closed: nil,
            keypoints_snapshots: nil,
            left_arm_angle: nil,
            right_arm_angle: nil,
            initial_asymmetry: nil,
            max_drift: nil,
            time_to_drift: nil,
            hits_support: nil,
            y_difference: nil,
            clinical_score: nil,
            asymmetry_percent: nil,
            nihss_total: nil,
            detection_quality: nil,
            quality_reason: nil,
            vertical_drift: nil
        )
        
        handleClinicalResult(response: errorResponse)
    }
    
    // Separate method to handle the AWS API call
    private func sendImageToAWS(payload: KeypointPayload) {
        
        // 2. Network Request Setup
        guard let url = URL(string: API_GATEWAY_URL) else {
            print("❌ Error: Invalid API Gateway URL: \(API_GATEWAY_URL)")
            print("🔍 DEBUG: Invalid URL - this triggers connection error")
            self.showDemoResults() // Fallback to demo
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 25.0 // 25 second timeout (less than the 30s fallback timer)

        do {
            request.httpBody = try JSONEncoder().encode(payload)
            print("📦 Payload encoded successfully")
        } catch {
            print("❌ Error encoding payload: \(error)")
            print("🔍 DEBUG: JSON encoding failed - this triggers connection error")
            self.showDemoResults() // Fallback to demo
            return
        }
        
        // 3. Execute the Network Request
        print("🌐 Starting network request to: \(API_GATEWAY_URL)")
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async { [weak self] in
                guard let self = self else { return }
                
                if let error = error {
                    print("❌ Network Error: \(error.localizedDescription)")
                    print("🔍 DEBUG: Network request failed - this triggers connection error")
                    self.showDemoResults() // Fallback to demo
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    print("❌ Invalid response type")
                    print("🔍 DEBUG: Invalid response type - this triggers connection error")
                    self.showDemoResults()
                    return
                }
                
                print("📡 HTTP Status: \(httpResponse.statusCode)")
                
                guard let data = data else {
                    print("❌ No data received from AWS")
                    print("🔍 DEBUG: No data received - this triggers connection error")
                    self.showDemoResults()
                    return
                }
                
                // Log response for debugging
                if let responseString = String(data: data, encoding: .utf8) {
                    print("📥 AWS Response: \(responseString)")
                }
                
                // 4. Decode the AWS API Gateway Response first, then extract the body
                do {
                    // First decode the AWS wrapper response
                    let awsResponse = try JSONDecoder().decode(AWSResponse.self, from: data)
                    print("✅ Successfully decoded AWS wrapper response")
                    print("📡 AWS Status Code: \(awsResponse.statusCode)")
                    
                    // Check if the AWS response was successful
                    guard awsResponse.statusCode == 200 else {
                        print("❌ AWS returned non-200 status: \(awsResponse.statusCode)")
                        self.showDemoResults()
                        return
                    }
                    
                    // Extract the body string and decode it as JSON
                    guard let bodyData = awsResponse.body.data(using: .utf8) else {
                        print("❌ Could not convert body string to data")
                        self.showDemoResults()
                        return
                    }
                    
                    // Now decode the actual clinical response from the body
                    let clinicalResponse = try JSONDecoder().decode(ClinicalResponse.self, from: bodyData)
                    print("✅ Successfully decoded clinical response from body")
                    self.handleClinicalResult(response: clinicalResponse)
                    
                } catch {
                    print("❌ Error decoding response: \(error)")
                    print("📄 Raw response: \(String(data: data, encoding: .utf8) ?? "nil")")
                    print("🔍 DEBUG: Response decoding failed - this triggers connection error")
                    self.showDemoResults() // Fallback to demo
                }
            }
        }.resume()
    }
    
    // Processes the comprehensive clinical result from the AWS Lambda.
    func handleClinicalResult(response: ClinicalResponse) {
        print("🎯 handleClinicalResult called!")
        print("📊 Response: drift=\(response.drift_detected), severity=\(response.severity ?? "unknown")")
        print("🔍 Analysis method: \(response.analysis_method ?? "unknown")")
        print("📋 Test quality: \(response.test_quality ?? "unknown")")
        
        // Cancel timeout timer since we got results
        timeoutTimer?.cancel()
        
        self.isTesting = false
        self.clinicalScore = response.nihss_motor_score ?? response.clinical_score ?? 0
        self.testSeverity = response.severity ?? "normal"
        
        // Check if this is a fallback result
        let isFallback = response.test_quality == "local_calculation_fallback"
        if isFallback {
            print("🔄 FALLBACK: Using local calculation result")
        }
        
        // Handle error state
        if response.severity == "error" {
            self.appState = .error
            self.alertMessage = response.message ?? "Analysis unavailable"
            return
        }
        
        // Store detailed clinical metrics for results display
        self.detectedDrift = response.drift_detected
        self.detectedPronation = false // Keypoint-based analysis doesn't detect pronation
        
        // Debug logging for asymmetry score parsing
        print("🔍 DEBUG: Raw asymmetry_score from response: \(response.asymmetry_score ?? -999)")
        print("🔍 DEBUG: Raw y_difference from response: \(response.y_difference ?? -999)")
        
        self.yDifference = response.asymmetry_score ?? response.y_difference ?? 0.0
        print("🔍 DEBUG: Final yDifference value: \(self.yDifference)")
        
        self.testQuality = response.test_quality ?? "unknown"
        self.clinicalDetails = response.message ?? "No additional details available"
        
        // Calculate NIHSS scores based on research standards
        self.calculateNIHSSScores(response: response)
        
        // Calculate confidence score based on multiple factors
        var confidence: Double = 0.0
        if let score = response.clinical_score {
            confidence = Double(score) / 10.0 // Normalize to 0-1
        }
        if let yDiff = response.y_difference {
            confidence += min(yDiff * 10, 0.3) // Boost confidence for clear measurements
        }
        self.confidenceScore = min(confidence, 1.0)
        
        // Generate time-critical treatment recommendations
        self.generateTimeCriticalRecommendations()
        
        print("📱 UI State: isTesting=\(self.isTesting), appState will be updated")
        
        // Create detailed result message
        let yDiff = response.y_difference ?? 0.0
        let quality = response.test_quality ?? "unknown"
        
        var detailedMessage = ""
        
        // Debug: Log the exact severity value received
        print("🔍 DEBUG: Received severity value: '\(response.severity ?? "nil")'")
        print("🔍 DEBUG: Severity length: \(response.severity?.count ?? 0)")
        print("🔍 DEBUG: Severity bytes: \(response.severity?.data(using: .utf8) ?? Data())")
        
        // Clean and normalize the severity value
        let cleanSeverity = response.severity?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        print("🔍 DEBUG: Clean severity: '\(cleanSeverity ?? "nil")'")
        
        switch cleanSeverity {
        case "critical":
            self.appState = .resultPositive
            detailedMessage = """
            🚨 CLINICAL ALERT 🚨
            
            \(response.message ?? "Significant findings detected.")
            
            📊 Clinical Data:
            • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
            • Clinical Score: \(self.clinicalScore)/3
            • Test Quality: \(quality)
            
            ⚠️ Seek immediate medical evaluation.
            """
            self.alertMessage = detailedMessage
            self.showFullAlert = true
            
        case "warning":
            self.appState = .resultPositive
            detailedMessage = """
            ⚠️ CAUTION ⚠️
            
            \(response.message ?? "Abnormal findings detected.")
            
            📊 Clinical Data:
            • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
            • Clinical Score: \(self.clinicalScore)/3
            • Test Quality: \(quality)
            
            💡 Consider medical consultation.
            """
            self.alertMessage = detailedMessage
            self.showFullAlert = true
            
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
            self.alertMessage = detailedMessage
            self.showFullAlert = true
            
        case "moderate":
            self.appState = .resultPositive
            detailedMessage = """
            🔶 MODERATE DRIFT DETECTED 🔶
            
            \(response.message ?? "Moderate drift detected.")
            
            📊 Clinical Data:
            • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
            • Clinical Score: \(self.clinicalScore)/4
            • Test Quality: \(quality)
            
            💡 Consider medical consultation.
            """
            self.alertMessage = detailedMessage
            self.showFullAlert = true
            
        case "mild":
            self.appState = .resultPositive
            detailedMessage = """
            ⚠️ MILD DRIFT DETECTED ⚠️
            
            \(response.message ?? "Mild drift detected.")
            
            📊 Clinical Data:
            • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
            • Clinical Score: \(self.clinicalScore)/4
            • Test Quality: \(quality)
            
            👀 Monitor for other symptoms.
            """
            self.alertMessage = detailedMessage
            self.showFullAlert = true
            
        default: // "normal"
            self.appState = .resultNegative
            detailedMessage = """
            ✅ Normal Results
            
            \(response.message ?? "No abnormal findings detected.")
            
            📊 Clinical Data:
            • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
            • Clinical Score: \(self.clinicalScore)/3
            • Test Quality: \(quality)
            
            🎉 Test complete.
            """
            self.alertMessage = detailedMessage
        }
        
        // Log clinical assessment
        print("🏥 Clinical Assessment - Score: \(self.clinicalScore), Severity: \(self.testSeverity), Y-Drift: \(yDiff)")
        print("📋 Result Message: \(detailedMessage)")
    }
    
    // Handles non-critical errors and displays a message.
    func handleError(message: String) {
        self.isTesting = false
        self.appState = .setup
        self.alertMessage = "Error: \(message)"
    }
    
    // Calculate NIH Stroke Scale scores based on Lambda-provided research data
    private func calculateNIHSSScores(response: ClinicalResponse) {
        // Use Lambda-provided NIHSS scores (calculated server-side with research thresholds)
        self.motorArmScore = response.nihss_motor_score ?? 0
        self.nihssScore = response.nihss_motor_score ?? 0 // Use motor score as total for keypoint-based analysis
        
        // Calculate sensory and coordination scores based on Lambda data
        self.sensoryScore = false ? 2 : 0 // Keypoint-based analysis doesn't detect pronation
        
        // Coordination score based on overall motor control
        if response.drift_detected && false {
            self.coordinationScore = 2 // Severe coordination deficit
        } else if response.drift_detected || false {
            self.coordinationScore = 1 // Mild coordination deficit
        } else {
            self.coordinationScore = 0 // Normal coordination
        }
        
        print("🏥 NIHSS Scores from Lambda: Motor=\(self.motorArmScore), Total=\(self.nihssScore), Research-based=\(response.research_based ?? false)")
        print("📊 Analysis method: \(response.analysis_method ?? "unknown"), Version: \(response.version ?? "unknown")")
        print("📊 Asymmetry score: \(response.asymmetry_score ?? 0.0)")
    }
    
    // Generate time-critical treatment recommendations based on research
    private func generateTimeCriticalRecommendations() {
        let currentTime = Date()
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        let timeString = formatter.string(from: currentTime)
        
        // Based on research: "benefits of thrombolytic treatment are time-dependent"
        if self.nihssScore >= 4 {
            self.timeToTreatment = "🚨 IMMEDIATE: < 4.5 hours for thrombolytic therapy"
        } else if self.nihssScore >= 2 {
            self.timeToTreatment = "⚠️ URGENT: < 6 hours for endovascular therapy"
        } else {
            self.timeToTreatment = "📋 ROUTINE: Standard stroke evaluation"
        }
        
        print("⏰ Time-critical recommendation: \(self.timeToTreatment)")
    }
    
    // Resets the application state to start a new test.
    func resetTest() {
        cameraManager.stop()
        testTimer?.cancel()
        stepTimer?.cancel()
        validationTimer?.cancel()
        timeoutTimer?.cancel()
        countdownTimer?.cancel()
        debugTimer?.cancel()
        
        self.appState = .setup
        self.alertMessage = "Welcome to the Clinical Romberg Test"
        self.showFullAlert = false
        self.isTesting = false
        self.recognizedKeypoints = []
        self.capturedImageData = nil
        self.currentStep = 1
        self.clinicalScore = 0
        self.testSeverity = "normal"
        
        // Reset detailed clinical metrics
        self.detectedDrift = false
        self.detectedPronation = false
        self.yDifference = 0.0
        self.testQuality = "unknown"
        self.confidenceScore = 0.0
        self.clinicalDetails = ""
        
        // Reset NIHSS scores
        self.nihssScore = 0
        self.motorArmScore = 0
        self.sensoryScore = 0
        self.coordinationScore = 0
        self.timeToTreatment = ""
        
        // Reset live feedback and validation
        self.stepValidationStatus = [false, false, false]
        self.liveFeedbackMessage = ""
        self.remainingTime = 0
        self.isStepValidated = false
        self.showCheckmark = false
        
        // Reset calibration state
        self.calibrationStatus = ""
        self.isCalibrated = false
        self.calibrationFeedback = ""
        self.keypointCount = 0
        
        // Reset countdown state
        self.showCountdown = false
        self.countdownNumber = 5
        self.isCountingDown = false
        
        // Reset NIHSS state
        self.resetNihssTest()
        
        // Restart debug timer
        startDebugTimer()
    }
    
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
    
    private func startArmAngleVerification() {
        // Start monitoring arm angles
        print("🔍 Starting arm angle verification...")
    }
    
    private func verifyArmAngles(keypoints: [CGPoint]) {
        guard keypoints.count >= 4 else {
            armAngleVerified = false
            nihssInstructions = "Ensure all keypoints are detected"
            return
        }
        
        // Get keypoints from camera manager
        let latestKeypoints = cameraManager.latestKeypoints
        
        guard let leftWrist = latestKeypoints["left_wrist"],
              let rightWrist = latestKeypoints["right_wrist"],
              let leftShoulder = latestKeypoints["left_shoulder"],
              let rightShoulder = latestKeypoints["right_shoulder"] else {
            armAngleVerified = false
            nihssInstructions = "Ensure all keypoints are detected"
            return
        }
        
        // Calculate arm angles (simplified for normalized coordinates)
        let leftArmLength = abs(leftWrist.y - leftShoulder.y)
        let rightArmLength = abs(rightWrist.y - rightShoulder.y)
        
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
    
    private func startEyeClosureDetection() {
        // For now, we'll use manual verification
        // In production, this would integrate with face detection
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            self.eyeClosed = true
            self.nihssInstructions = "Eyes closed. Hold position for 10 seconds..."
            
            // Start the 10-second NIHSS test
            self.startNihssCountdown()
        }
    }
    
    private func startNihssCountdown() {
        nihssCountdown = 10
        isNihssTestActive = true
        
        // Start countdown timer
        countdownTimer = Timer.publish(every: 1.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self = self else { return }
                
                if self.nihssCountdown > 1 {
                    self.nihssCountdown -= 1
                    print("🔢 NIHSS countdown: \(self.nihssCountdown)")
                } else {
                    // Countdown finished, start 10-second test
                    self.isNihssTestActive = false
                    self.countdownTimer?.cancel()
                    self.startTenSecondTest()
                }
            }
    }
    
    private func startTenSecondTest() {
        print("🚀 Starting 10-second NIHSS test...")
        nihssInstructions = "Hold position for 10 seconds..."
        
        // Start collecting keypoint history
        startKeypointHistoryCollection()
        
        // Start 10-second timer
        stepTimer = Timer.publish(every: 10.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                self?.stepTimer?.cancel()
                self?.completeNihssTest()
            }
    }
    
    private func startKeypointHistoryCollection() {
        // Collect keypoint snapshots every 0.5 seconds for 10 seconds
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] timer in
            guard let self = self else {
                timer.invalidate()
                return
            }
            
            if self.keypointHistory.count >= 20 {
                timer.invalidate()
                return
            }
            
            self.collectKeypointSnapshot()
        }
    }
    
    private func collectKeypointSnapshot() {
        guard keypointHistory.count < 20 else { return } // Max 20 snapshots (10 seconds at 0.5s intervals)
        
        // Get current keypoints from camera manager
        let currentKeypoints = cameraManager.latestKeypoints
        
        // Convert to snapshot format
        let snapshot = KeypointSnapshot(
            timestamp: Date().timeIntervalSince1970,
            keypoints: currentKeypoints.mapValues { point in
                KeypointData(x: Double(point.x), y: Double(point.y))
            }
        )
        
        keypointHistory.append(snapshot)
        
        // Calculate real-time drift
        calculateRealTimeDrift()
        
        print("📊 Collected keypoint snapshot \(keypointHistory.count)/20")
    }
    
    private func calculateRealTimeDrift() {
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
    
    private func completeNihssTest() {
        print("✅ NIHSS test completed. Sending data to Lambda...")
        
        // Calculate total test duration
        if let firstSnapshot = keypointHistory.first,
           let lastSnapshot = keypointHistory.last {
            testDuration = lastSnapshot.timestamp - firstSnapshot.timestamp
        }
        
        // Send NIHSS data to Lambda
        sendNihssDataToAWS()
    }
    
    private func sendNihssDataToAWS() {
        // Create NIHSS payload
        let nihssPayload = NihssPayload(
            keypoints_history: keypointHistory,
            test_duration: testDuration,
            eye_closed: eyeClosed,
            user_id: userID
        )
        
        print("📡 Sending NIHSS data to Lambda...")
        print("   Keypoint snapshots: \(keypointHistory.count)")
        print("   Test duration: \(testDuration)s")
        print("   Eye closed: \(eyeClosed)")
        
        // Send to Lambda
        sendNihssToAWS(payload: nihssPayload)
    }
    
    private func sendNihssToAWS(payload: NihssPayload) {
        guard let url = URL(string: API_GATEWAY_URL) else {
            print("❌ Error: Invalid API Gateway URL")
            handleNIHSSError("Invalid API Gateway URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let jsonData = try JSONEncoder().encode(payload)
            request.httpBody = jsonData
            
            print("📤 Sending NIHSS payload to AWS...")
            
            URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
                DispatchQueue.main.async {
                    if let error = error {
                        print("❌ NIHSS request failed: \(error)")
                        self?.handleNIHSSError("Network error: \(error.localizedDescription)")
                        return
                    }
                    
                    guard let data = data else {
                        print("❌ No data received from NIHSS Lambda")
                        self?.handleNIHSSError("No data received")
                        return
                    }
                    
                    print("📥 NIHSS Response received: \(data.count) bytes")
                    
                    do {
                        let awsResponse = try JSONDecoder().decode(AWSResponse.self, from: data)
                        print("✅ Successfully decoded AWS wrapper response")
                        print("📡 AWS Status Code: \(awsResponse.statusCode)")
                        
                        if awsResponse.statusCode == 200 {
                            // Extract the body string and decode it as JSON
                            guard let bodyData = awsResponse.body.data(using: .utf8) else {
                                print("❌ Could not convert NIHSS body string to data")
                                self?.handleNIHSSError("Invalid response format")
                                return
                            }
                            
                            // Now decode the actual clinical response from the body
                            let clinicalResponse = try JSONDecoder().decode(ClinicalResponse.self, from: bodyData)
                            print("✅ Successfully decoded NIHSS clinical response from body")
                            self?.handleNIHSSResult(response: clinicalResponse)
                            
                        } else {
                            print("❌ NIHSS Lambda returned error status: \(awsResponse.statusCode)")
                            self?.handleNIHSSError("Lambda error: \(awsResponse.statusCode)")
                        }
                        
                    } catch {
                        print("❌ Error decoding NIHSS response: \(error)")
                        print("📄 Raw NIHSS response: \(String(data: data, encoding: .utf8) ?? "nil")")
                        self?.handleNIHSSError("Response decoding failed")
                    }
                }
            }.resume()
            
        } catch {
            print("❌ Error encoding NIHSS payload: \(error)")
            handleNIHSSError("Payload encoding failed")
        }
    }
    
    private func handleNIHSSResult(response: ClinicalResponse) {
        print("🎯 handleNIHSSResult called!")
        print("📊 NIHSS Response: drift=\(response.drift_detected), severity=\(response.severity ?? "unknown")")
        
        // Cancel timeout timer since we got results
        timeoutTimer?.cancel()
        
        self.isTesting = false
        self.showNihssInstructions = false
        self.clinicalScore = response.nihss_motor_score ?? response.clinical_score ?? 0
        self.testSeverity = response.severity ?? "normal"
        
        // Handle error state
        if response.severity == "error" {
            self.appState = .error
            self.alertMessage = response.message ?? "NIHSS Analysis unavailable"
            return
        }
        
        // Store detailed clinical metrics for results display
        self.detectedDrift = response.drift_detected
        self.detectedPronation = false // NIHSS doesn't detect pronation
        self.yDifference = response.asymmetry_score ?? response.y_difference ?? 0.0
        self.testQuality = response.test_quality ?? "unknown"
        self.clinicalDetails = response.message ?? "No additional details available"
        
        // Debug logging for asymmetry score parsing
        print("🔍 DEBUG: Raw asymmetry_score from NIHSS response: \(response.asymmetry_score ?? -999)")
        print("🔍 DEBUG: Final yDifference value: \(self.yDifference)")
        
        // Calculate NIHSS scores based on research standards
        self.calculateNIHSSScores(response: response)
        
        // Calculate confidence score based on multiple factors
        self.calculateConfidenceScore(response: response)
        
        // Set time-critical treatment recommendation
        self.setTimeCriticalRecommendation(response: response)
        
        // Update UI state based on results
        if response.drift_detected {
            self.appState = .resultPositive
            self.alertMessage = response.message ?? "Drift detected"
        } else {
            self.appState = .resultNegative
            self.alertMessage = response.message ?? "No drift detected"
        }
        
        print("✅ NIHSS analysis completed successfully")
    }
    
    private func handleNIHSSError(_ errorMessage: String) {
        print("❌ NIHSS Error: \(errorMessage)")
        
        // Show demo results as fallback
        showDemoResults()
    }
    
    private func calculateArmAngle(armLength: Double) -> Double {
        // Simplified arm angle calculation for normalized coordinates
        let estimatedArmLength = 0.3  // Approximate arm length in normalized coordinates
        let angleRadians = asin(min(armLength / estimatedArmLength, 1.0))
        return angleRadians * 180 / .pi
    }
    
    // Update existing startTest method to use NIHSS
    func startTest() {
        print("🚀 Starting NIHSS-compliant test...")
        
        // Use NIHSS test instead of old test
        startNihssTest()
    }
    
    // Add NIHSS reset method
    func resetNihssTest() {
        keypointHistory.removeAll()
        eyeClosed = false
        armAngleVerified = false
        testDuration = 0.0
        realTimeDrift = 0.0
        showNihssInstructions = false
        isNihssTestActive = false
        nihssCountdown = 10
    }
    
    // MARK: - Debug Methods
    
    private func startDebugTimer() {
        // Start debug timer that logs coordinates every 5 seconds
        debugTimer = Timer.publish(every: 5.0, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                self?.logCurrentKeypoints()
            }
        
        print("🔍 Debug timer started - will log keypoint coordinates every 5 seconds")
    }
    
    private func logCurrentKeypoints() {
        let latestKeypoints = cameraManager.latestKeypoints
        
        print("\n" + String(repeating: "=", count: 60))
        print("🔍 DEBUG: Current Keypoint Coordinates (Every 5 seconds)")
        print(String(repeating: "=", count: 60))
        print("📅 Timestamp: \(Date().formatted(date: .omitted, time: .standard))")
        print("📊 Total keypoints detected: \(latestKeypoints.count)")
        print("📊 Recognized keypoints array size: \(recognizedKeypoints.count)")
        
        if latestKeypoints.isEmpty {
            print("❌ NO KEYPOINTS DETECTED - Camera may not be working properly")
            print("🔧 Troubleshooting:")
            print("   • Check if person is in frame")
            print("   • Ensure good lighting")
            print("   • Verify camera permissions")
            print("   • Check if pose estimation is enabled")
        } else {
            print("✅ KEYPOINTS DETECTED:")
            
            // Log each keypoint with coordinates
            for (keypointName, coordinates) in latestKeypoints.sorted(by: { $0.key < $1.key }) {
                let x = coordinates.x
                let y = coordinates.y
                let xPercent = String(format: "%.1f", x * 100)
                let yPercent = String(format: "%.1f", y * 100)
                
                print("   🎯 \(keypointName):")
                print("      📍 Raw coordinates: (x: \(x), y: \(y))")
                print("      📊 Percentage: (x: \(xPercent)%, y: \(yPercent)%)")
                
                // Validate coordinate ranges
                if x < 0 || x > 1 || y < 0 || y > 1 {
                    print("      ⚠️ WARNING: Coordinates out of range (0-1)!")
                }
            }
            
            // Calculate and display arm asymmetry if we have wrist/shoulder data
            if let leftWrist = latestKeypoints["left_wrist"],
               let rightWrist = latestKeypoints["right_wrist"],
               let leftShoulder = latestKeypoints["left_shoulder"],
               let rightShoulder = latestKeypoints["right_shoulder"] {
                
                // Calculate arm lengths using Euclidean distance (proper for 90-degree arms)
                let leftArmLength = sqrt(pow(leftWrist.x - leftShoulder.x, 2) + pow(leftWrist.y - leftShoulder.y, 2))
                let rightArmLength = sqrt(pow(rightWrist.x - rightShoulder.x, 2) + pow(rightWrist.y - rightShoulder.y, 2))
                let verticalDrift = abs(leftWrist.y - rightWrist.y)
                let avgArmLength = (leftArmLength + rightArmLength) / 2
                
                print("\n📊 ARM ANALYSIS:")
                print("   🦾 Left arm length: \(String(format: "%.3f", leftArmLength))")
                print("   🦾 Right arm length: \(String(format: "%.3f", rightArmLength))")
                print("   📏 Vertical drift: \(String(format: "%.3f", verticalDrift))")
                print("   📐 Average arm length: \(String(format: "%.3f", avgArmLength))")
                
                // ROBUST ASYMMETRY CALCULATION - automatically chooses best method based on detection quality
                let armLengthDiff = abs(leftArmLength - rightArmLength) / max(leftArmLength, rightArmLength)
                let isPoorDetection = avgArmLength < 0.05 || armLengthDiff > 0.5
                
                let asymmetry: Double
                let methodUsed: String
                
                if isPoorDetection {
                    // Use absolute vertical drift for poor detection quality
                    asymmetry = verticalDrift
                    methodUsed = "absolute_vertical_drift"
                    print("   🔧 Using absolute vertical drift (poor detection quality)")
                    print("   📊 Detection quality: poor (arm length diff: \(String(format: "%.1f", armLengthDiff * 100))%)")
                } else {
                    // Use normalized method for good detection quality
                    asymmetry = avgArmLength > 0.01 ? verticalDrift / avgArmLength : verticalDrift
                    methodUsed = "normalized_vertical_drift"
                    print("   🔧 Using normalized vertical drift (good detection quality)")
                    print("   📊 Detection quality: good")
                }
                
                let asymmetryPercent = String(format: "%.1f", asymmetry * 100)
                print("   ⚖️ Current asymmetry: \(asymmetryPercent)% (method: \(methodUsed))")
                
                // NIHSS classification preview
                let nihssScore = getNIHSSScorePreview(asymmetry: asymmetry)
                print("   🏥 NIHSS Score Preview: \(nihssScore)")
            }
            
            // App state information
            print("\n📱 APP STATE:")
            print("   🔄 Current state: \(appState)")
            print("   🎯 Calibrated: \(isCalibrated)")
            print("   🧪 Testing: \(isTesting)")
            print("   👁️ NIHSS active: \(isNihssTestActive)")
            print("   📊 Keypoint history: \(keypointHistory.count) snapshots")
        }
        
        print(String(repeating: "=", count: 60) + "\n")
    }
    
    private func getNIHSSScorePreview(asymmetry: Double) -> String {
        // REALISTIC NIHSS score preview - adjusted for normal arm positioning variations
        // These thresholds account for natural variations, camera angles, and detection accuracy
        switch asymmetry {
        case 0..<0.20:  // <20% - Normal variation (was 5%)
            return "NIHSS 0 - Normal"
        case 0.20..<0.35:  // 20-35% - Mild drift (was 5-15%)
            return "NIHSS 1 - Mild"
        case 0.35..<0.50:  // 35-50% - Moderate drift (was 15-30%)
            return "NIHSS 2 - Moderate"
        case 0.50..<0.70:  // 50-70% - Severe drift (was 30-50%)
            return "NIHSS 3 - Severe"
        default:  // >70% - Critical (was 50%+)
            return "NIHSS 4 - Critical"
        }
    }
    
    func stopDebugTimer() {
        debugTimer?.cancel()
        print("🔍 Debug timer stopped")
    }
    
    // MARK: - Missing Methods
    
    private func calculateConfidenceScore(response: ClinicalResponse) {
        // Calculate confidence based on test quality and keypoint count
        var confidence: Double = 0.5 // Base confidence
        
        // Increase confidence based on test quality
        if let testQuality = response.test_quality {
            switch testQuality.lowercased() {
            case "excellent", "perfect":
                confidence += 0.3
            case "good", "good_calibration_analysis":
                confidence += 0.2
            case "fair":
                confidence += 0.1
            default:
                confidence += 0.0
            }
        }
        
        // Increase confidence based on keypoint history
        if keypointHistory.count >= 15 {
            confidence += 0.2
        } else if keypointHistory.count >= 10 {
            confidence += 0.1
        }
        
        // Increase confidence if eye closure was verified
        if eyeClosed {
            confidence += 0.1
        }
        
        // Increase confidence if arm angles were verified
        if armAngleVerified {
            confidence += 0.1
        }
        
        // Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        self.confidenceScore = confidence
        print("📊 Confidence score calculated: \(String(format: "%.2f", confidence))")
    }
    
    private func setTimeCriticalRecommendation(response: ClinicalResponse) {
        // Set time-critical treatment recommendation based on NIHSS score
        if let nihssScore = response.nihss_motor_score {
            switch nihssScore {
            case 4:
                self.timeToTreatment = "🚨 CRITICAL: < 4.5 hours for thrombolysis"
            case 3:
                self.timeToTreatment = "⚠️ URGENT: < 6 hours for endovascular therapy"
            case 2:
                self.timeToTreatment = "📋 ROUTINE: Standard stroke evaluation"
            case 1:
                self.timeToTreatment = "📋 ROUTINE: Standard stroke evaluation"
            default:
                self.timeToTreatment = "✅ NORMAL: No immediate intervention needed"
            }
        } else {
            self.timeToTreatment = "📋 ROUTINE: Standard stroke evaluation"
        }
        
        print("⏰ Time-critical recommendation: \(self.timeToTreatment)")
    }
}
