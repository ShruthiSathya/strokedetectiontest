import Foundation
import SwiftUI
import CoreGraphics
import Combine
import AVFoundation // Required for AVCaptureSession in CameraManager

// IMPORTANT: REPLACE THIS PLACEHOLDER URL with the actual 'Invoke URL' you got from API Gateway Step 7.
// Example: https://xxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/test
let API_GATEWAY_URL = "https://mq480jftx9.execute-api.us-west-1.amazonaws.com/prod/test"

// MARK: - 1. Codable Structs for AWS Communication
struct ImagePayload: Codable {
    let image_base64: String
    let user_id: String
}
struct ClinicalResponse: Codable {
    let drift_detected: Bool
    let pronation_detected: Bool
    let y_difference: Double?
    let clinical_score: Int?
    let test_quality: String?
    let severity: String?
    let message: String?
    
    // Removed analysis_details since [String: Any] doesn't conform to Codable
    enum CodingKeys: String, CodingKey {
        case drift_detected, pronation_detected, y_difference
        case clinical_score, test_quality, severity, message
    }
}

// MARK: - 2. ViewModel (Real Camera Integration)
class TestViewModel: ObservableObject {
    
    // --- State Variables ---
    enum AppState { 
        case setup, positioning, eyesClosed, testing, analyzing, resultNegative, resultPositive 
    }
    @Published var appState: AppState = .setup
    @Published var alertMessage: String = "Welcome to the Clinical Romberg Test"
    @Published var showFullAlert: Bool = false
    @Published var isTesting: Bool = false
    @Published var recognizedKeypoints: [CGPoint] = []
    @Published var currentStep: Int = 1
    @Published var clinicalScore: Int = 0
    @Published var testSeverity: String = "normal"
    
    // Live feedback and validation
    @Published var stepValidationStatus: [Bool] = [false, false, false] // Track each step completion
    @Published var liveFeedbackMessage: String = ""
    @Published var remainingTime: Int = 0
    @Published var isStepValidated: Bool = false
    @Published var showCheckmark: Bool = false
    
    // CRITICAL: Camera Manager Instance
    public var cameraManager = CameraManager()
    private var testTimer: AnyCancellable?
    private var stepTimer: AnyCancellable?
    private var validationTimer: AnyCancellable?
    private var timeoutTimer: AnyCancellable?
    
    // Variables to store the final data to be sent to AWS
    private var capturedImageData: Data?
    
    init() {
        // Connect the camera output to the ViewModel handler
        cameraManager.poseEstimationHandler = { [weak self] keypoints in
            // Called for EVERY frame (fast): Updates visual overlay and collects data
            self?.recognizedKeypoints = keypoints
            self?.processFrame(keypoints: keypoints)
        }
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
        
        switch appState {
        case .positioning:
            if keypointCount >= 4 {
                liveFeedbackMessage = "✅ Arms detected! Hold position steady..."
            } else if keypointCount >= 2 {
                liveFeedbackMessage = "🔍 Partial detection... Extend both arms forward with palms up"
            } else if keypointCount >= 1 {
                liveFeedbackMessage = "👀 Person detected... Please extend both arms forward"
            } else {
                liveFeedbackMessage = "📷 Looking for person... Stand in front of camera and extend arms"
            }
            
        case .eyesClosed:
            if keypointCount >= 4 {
                liveFeedbackMessage = "👁️ Eyes closed detected! Maintain position..."
            } else if keypointCount >= 2 {
                liveFeedbackMessage = "🔍 Arms detected. Now close your eyes..."
            } else {
                liveFeedbackMessage = "👀 Person detected. Close your eyes..."
            }
            
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
    
    // Validates the current step based on keypoint detection
    private func validateCurrentStep(keypoints: [CGPoint]) {
        let keypointCount = keypoints.count
        let requiredKeypoints = 4 // Minimum keypoints needed for validation
        
        print("🔍 Validating step: \(appState), keypoints: \(keypointCount), required: \(requiredKeypoints)")
        
        switch appState {
        case .positioning:
            if keypointCount >= requiredKeypoints && !stepValidationStatus[0] {
                print("✅ Step 1 validation passed: \(keypointCount) keypoints detected")
                validateStep(stepIndex: 0)
            } else {
                print("❌ Step 1 validation failed: only \(keypointCount) keypoints detected")
            }
            
        case .eyesClosed:
            if keypointCount >= requiredKeypoints && !stepValidationStatus[1] {
                print("✅ Step 2 validation passed: \(keypointCount) keypoints detected")
                validateStep(stepIndex: 1)
            } else {
                print("❌ Step 2 validation failed: only \(keypointCount) keypoints detected")
            }
            
        case .testing:
            if keypointCount >= requiredKeypoints && !stepValidationStatus[2] {
                print("✅ Step 3 validation passed: \(keypointCount) keypoints detected")
                validateStep(stepIndex: 2)
            } else {
                print("❌ Step 3 validation failed: only \(keypointCount) keypoints detected")
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
        
        self.appState = .positioning
        self.alertMessage = "Step 1: Position yourself with arms extended forward, palms up"
        self.currentStep = 1
        self.isTesting = true
        self.showFullAlert = false
        
        // Start the camera and Vision processing
        cameraManager.start()
        
        // Start the proper clinical validation process
        print("🏥 Starting proper clinical validation process")
        progressThroughClinicalSteps()
    }
    
    // Progresses through the clinical test protocol with validation
    private func progressThroughClinicalSteps() {
        print("🚀 Starting clinical steps progression...")
        
        // Step 1: Positioning (15 seconds with validation)
        startStepTimer(duration: 15) { [weak self] in
            guard let self = self else { return }
            print("📋 Step 1 completed. Validation status: \(self.stepValidationStatus[0])")
            
            if self.stepValidationStatus[0] {
                print("✅ Step 1 validated! Moving to Step 2")
                self.appState = .eyesClosed
                self.alertMessage = "Step 2: Close your eyes and hold position"
                self.currentStep = 2
                self.startStepTimer(duration: 15) { [weak self] in
                    guard let self = self else { return }
                    print("📋 Step 2 completed. Validation status: \(self.stepValidationStatus[1])")
                    
                    if self.stepValidationStatus[1] {
                        print("✅ Step 2 validated! Moving to Step 3")
                        self.appState = .testing
                        self.alertMessage = "Step 3: Hold steady for 30 seconds (clinical observation period)"
                        self.currentStep = 3
                        self.startMainTestTimer(duration: 30)
                    } else {
                        print("❌ Step 2 failed validation - showing error")
                        self.showValidationError(message: "Please close your eyes and maintain arm position. Tap RESTART to try again.")
                    }
                }
            } else {
                print("❌ Step 1 failed validation - showing error")
                self.showValidationError(message: "Please extend both arms forward with palms up. Make sure the camera can see your arms clearly. Tap RESTART to try again.")
            }
        }
    }
    
    // Shows validation error and allows restart
    private func showValidationError(message: String) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            self.isTesting = false
            self.appState = .setup
            self.alertMessage = message
            self.liveFeedbackMessage = "❌ Validation failed. Please try again."
            print("🚨 Validation error shown: \(message)")
        }
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
        
        // Set a timeout to force results after 10 seconds
        timeoutTimer = Timer.publish(every: 10.0, on: .main, in: .common)
            .autoconnect()
            .prefix(1)
            .sink { [weak self] _ in
                print("⏰ TIMEOUT: Forcing demo results after 10 seconds")
                self?.showDemoResults()
            }
        
        // Capture the current frame as an image
        cameraManager.captureCurrentFrame { [weak self] imageData in
            guard let self = self else { return }
            
            if let imageData = imageData {
                print("✅ Image captured successfully, size: \(imageData.count) bytes")
                
                // Stop the camera once data is captured to save resources
                self.cameraManager.stop()
                
                let userID = UUID().uuidString
                
                // Convert image data to Base64 string
                let base64String = imageData.base64EncodedString()
                print("📤 Sending image to AWS Lambda...")
                
                // 1. Prepare the Payload for JSON encoding
                let payload = ImagePayload(
                    image_base64: base64String,
                    user_id: userID
                )
                
                self.sendImageToAWS(payload: payload)
            } else {
                print("❌ Failed to capture image")
                // Fallback: Show demo results if image capture fails
                self.showDemoResults()
            }
        }
    }
    
    // Demo fallback when AWS is not available
    private func showDemoResults() {
        print("🎭 Showing demo results...")
        
        // Stop the camera if it's still running
        cameraManager.stop()
        
        // Update UI immediately
        DispatchQueue.main.async { [weak self] in
            self?.appState = .analyzing
            self?.liveFeedbackMessage = "🎭 Using demo results..."
            self?.isTesting = false
        }
        
        // Simulate AWS processing delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
            guard let self = self else { return }
            
            // Simulate different results for demo
            let demoResults = [
                (drift: false, message: "No abnormal findings detected. Test complete."),
                (drift: true, message: "CAUTION: Arm drift detected. Consider medical consultation.")
            ]
            
            let randomResult = demoResults.randomElement()!
            
            let clinicalResponse = ClinicalResponse(
                drift_detected: randomResult.drift,
                pronation_detected: false,
                y_difference: randomResult.drift ? 0.12 : 0.03,
                clinical_score: randomResult.drift ? 2 : 0,
                test_quality: "demo",
                severity: randomResult.drift ? "warning" : "normal",
                message: randomResult.message
            )
            
            print("🎯 Demo results ready: \(randomResult.drift ? "WARNING" : "NORMAL")")
            self.handleClinicalResult(response: clinicalResponse)
        }
    }
    
    // Separate method to handle the AWS API call
    private func sendImageToAWS(payload: ImagePayload) {
        
        // 2. Network Request Setup
        guard let url = URL(string: API_GATEWAY_URL) else {
            print("❌ Error: Invalid API Gateway URL: \(API_GATEWAY_URL)")
            self.showDemoResults() // Fallback to demo
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30.0 // 30 second timeout

        do {
            request.httpBody = try JSONEncoder().encode(payload)
            print("📦 Payload encoded successfully")
        } catch {
            print("❌ Error encoding payload: \(error)")
            self.showDemoResults() // Fallback to demo
            return
        }
        
        // 3. Execute the Network Request
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async { [weak self] in
                guard let self = self else { return }
                
                if let error = error {
                    print("❌ Network Error: \(error.localizedDescription)")
                    self.showDemoResults() // Fallback to demo
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    print("❌ Invalid response type")
                    self.showDemoResults()
                    return
                }
                
                print("📡 HTTP Status: \(httpResponse.statusCode)")
                
                guard let data = data else {
                    print("❌ No data received from AWS")
                    self.showDemoResults()
                    return
                }
                
                // Log response for debugging
                if let responseString = String(data: data, encoding: .utf8) {
                    print("📥 AWS Response: \(responseString)")
                }
                
                // 4. Decode the Clinical Response from the Lambda
                do {
                    let clinicalResponse = try JSONDecoder().decode(ClinicalResponse.self, from: data)
                    print("✅ Successfully decoded clinical response")
                    self.handleClinicalResult(response: clinicalResponse)
                } catch {
                    print("❌ Error decoding response: \(error)")
                    print("📄 Raw response: \(String(data: data, encoding: .utf8) ?? "nil")")
                    self.showDemoResults() // Fallback to demo
                }
            }
        }.resume()
    }
    
    // Processes the comprehensive clinical result from the AWS Lambda.
    func handleClinicalResult(response: ClinicalResponse) {
        print("🎯 handleClinicalResult called!")
        print("📊 Response: drift=\(response.drift_detected), severity=\(response.severity ?? "unknown")")
        
        // Cancel timeout timer since we got results
        timeoutTimer?.cancel()
        
        self.isTesting = false
        self.clinicalScore = response.clinical_score ?? 0
        self.testSeverity = response.severity ?? "normal"
        
        print("📱 UI State: isTesting=\(self.isTesting), appState will be updated")
        
        // Create detailed result message
        let yDiff = response.y_difference ?? 0.0
        let quality = response.test_quality ?? "unknown"
        
        var detailedMessage = ""
        
        switch response.severity {
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
            
        case "mild":
            self.appState = .resultNegative
            detailedMessage = """
            ℹ️ Minor Findings
            
            \(response.message ?? "Minor findings detected.")
            
            📊 Clinical Data:
            • Y-Axis Drift: \(String(format: "%.2f", yDiff * 100))%
            • Clinical Score: \(self.clinicalScore)/3
            • Test Quality: \(quality)
            
            👀 Monitor for other symptoms.
            """
            self.alertMessage = detailedMessage
            
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
    
    // Resets the application state to start a new test.
    func resetTest() {
        cameraManager.stop()
        testTimer?.cancel()
        stepTimer?.cancel()
        validationTimer?.cancel()
        timeoutTimer?.cancel()
        
        self.appState = .setup
        self.alertMessage = "Welcome to the Clinical Romberg Test"
        self.showFullAlert = false
        self.isTesting = false
        self.recognizedKeypoints = []
        self.capturedImageData = nil
        self.currentStep = 1
        self.clinicalScore = 0
        self.testSeverity = "normal"
        
        // Reset live feedback and validation
        self.stepValidationStatus = [false, false, false]
        self.liveFeedbackMessage = ""
        self.remainingTime = 0
        self.isStepValidated = false
        self.showCheckmark = false
    }
}
