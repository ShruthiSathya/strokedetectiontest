// MARK: - Enhanced Frame Collection for iOS
// Add these properties to your TestViewModel class

import Foundation
import SwiftUI
import Combine

// MARK: - Enhanced Frame Collection Properties
extension TestViewModel {
    
    // Frame collection properties
    @Published var frameCollectionProgress: Double = 0.0
    @Published var framesCollected: Int = 0
    @Published var totalFramesToCollect: Int = 600  // 20 seconds at 30fps
    @Published var frameCollectionActive: Bool = false
    
    // Frame collection data storage
    private var collectedFrames: [Data] = []
    private var frameCollectionTimer: AnyCancellable?
    private let targetFPS: Double = 30.0
    private let frameInterval: TimeInterval = 1.0 / 30.0  // 30fps
}

// MARK: - Enhanced Frame Collection Methods
extension TestViewModel {
    
    func startEnhancedFrameCollection() {
        print("🎬 Starting enhanced frame collection for video analysis")
        
        // Reset collection state
        collectedFrames.removeAll()
        framesCollected = 0
        frameCollectionProgress = 0.0
        frameCollectionActive = true
        
        // Start frame collection timer
        frameCollectionTimer = Timer.publish(every: frameInterval, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                self?.captureFrameForCollection()
            }
    }
    
    private func captureFrameForCollection() {
        guard frameCollectionActive && framesCollected < totalFramesToCollect else {
            if frameCollectionActive {
                completeFrameCollection()
            }
            return
        }
        
        cameraManager.captureCurrentFrame { [weak self] imageData in
            guard let self = self, let imageData = imageData else { return }
            
            // Add frame to collection
            self.collectedFrames.append(imageData)
            self.framesCollected += 1
            self.frameCollectionProgress = Double(self.framesCollected) / Double(self.totalFramesToCollect)
            
            print("📸 Collected frame \(self.framesCollected)/\(self.totalFramesToCollect)")
            
            // Check if collection is complete
            if self.framesCollected >= self.totalFramesToCollect {
                self.completeFrameCollection()
            }
        }
    }
    
    private func completeFrameCollection() {
        print("✅ Frame collection complete: \(framesCollected) frames")
        
        // Stop collection
        frameCollectionActive = false
        frameCollectionTimer?.cancel()
        
        // Send frames for enhanced analysis
        sendFramesForEnhancedAnalysis()
    }
    
    private func sendFramesForEnhancedAnalysis() {
        print("🚀 Sending \(collectedFrames.count) frames for enhanced analysis")
        
        // Convert frames to base64
        let base64Frames = collectedFrames.map { frame in
            frame.base64EncodedString()
        }
        
        // Create enhanced payload
        let payload = [
            "frames": base64Frames,
            "user_id": userID,
            "keypoints_detected": keypointCount,
            "test_duration": 20.0,
            "fps": 30,
            "analysis_type": "enhanced_frame_by_frame"
        ]
        
        // Send to enhanced Lambda endpoint
        sendToAWSEnhanced(payload: payload)
    }
    
    private func sendToAWSEnhanced(payload: [String: Any]) {
        guard let url = URL(string: API_GATEWAY_URL) else {
            handleError("Invalid URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        } catch {
            handleError("Failed to encode payload: \(error.localizedDescription)")
            return
        }
        
        print("📡 Sending enhanced frame-by-frame analysis request...")
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.handleError("Network error: \(error.localizedDescription)")
                    return
                }
                
                guard let data = data else {
                    self?.handleError("No data received")
                    return
                }
                
                self?.handleEnhancedAnalysisResponse(data: data)
            }
        }.resume()
    }
    
    private func handleEnhancedAnalysisResponse(data: Data) {
        do {
            let response = try JSONDecoder().decode(AWSResponse.self, from: data)
            
            guard response.statusCode == 200,
                  let bodyData = response.body.data(using: .utf8) else {
                handleError("Invalid response format")
                return
            }
            
            let clinicalResponse = try JSONDecoder().decode(ClinicalResponse.self, from: bodyData)
            
            // Handle enhanced response
            handleEnhancedClinicalResult(response: clinicalResponse)
            
        } catch {
            print("❌ Enhanced analysis response parsing failed: \(error)")
            handleError("Failed to parse enhanced analysis response")
        }
    }
    
    private func handleEnhancedClinicalResult(response: ClinicalResponse) {
        print("🎯 Enhanced frame-by-frame analysis result received")
        
        // Update existing properties
        detectedDrift = response.drift_detected
        detectedPronation = response.pronation_detected
        yDifference = response.y_difference ?? 0.0
        testQuality = response.test_quality ?? "unknown"
        clinicalScore = response.clinical_score ?? 0
        testSeverity = response.severity ?? "unknown"
        nihssScore = response.nihss_total ?? 0
        motorArmScore = response.nihss_motor_score ?? 0
        
        // Update enhanced properties if available
        if let driftTrend = response.drift_trend {
            print("📈 Drift Trend: \(driftTrend)")
        }
        
        if let meanVelocity = response.mean_velocity {
            print("⚡ Mean Velocity: \(meanVelocity)")
        }
        
        if let stabilityScore = response.stability_score {
            print("🎯 Stability Score: \(stabilityScore)")
        }
        
        // Transition to results state
        appState = response.drift_detected ? .resultPositive : .resultNegative
    }
}

// MARK: - Enhanced ClinicalResponse Model
struct EnhancedClinicalResponse: Codable {
    // Existing properties
    let drift_detected: Bool
    let pronation_detected: Bool
    let y_difference: Double?
    let clinical_score: Int?
    let test_quality: String?
    let severity: String?
    let message: String?
    let nihss_motor_score: Int?
    let nihss_total: Int?
    let drift_severity: String?
    let research_based: Bool?
    
    // Enhanced properties for frame-by-frame analysis
    let analysis_method: String?
    let frames_analyzed: Int?
    let fps: Int?
    let drift_trend: Double?
    let mean_velocity: Double?
    let max_velocity: Double?
    let stability_score: Double?
    let clinical_interpretation: String?
    
    // Temporal metrics
    let temporal_metrics: TemporalMetrics?
}

struct TemporalMetrics: Codable {
    let mean_asymmetry: Double
    let asymmetry_std: Double
    let velocity_std: Double
    let analysis_duration: Double
}

// MARK: - Modified Test Flow
extension TestViewModel {
    
    // Modified startDriftTest to use frame collection
    func startDriftTestEnhanced() {
        guard isCalibrated else { return }
        
        self.appState = .testing
        self.alertMessage = "Test: Close your eyes and hold steady for 20 seconds"
        self.currentStep = 2
        self.isTesting = true
        
        print("⏱️ Starting enhanced 20-second drift test with frame collection")
        
        // Start frame collection instead of just timer
        startEnhancedFrameCollection()
        
        // Also start timer for UI countdown
        startMainTestTimer(duration: 20)
    }
}
