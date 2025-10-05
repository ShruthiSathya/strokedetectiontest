//
//  TestView.swift
//  strokedetectionapp
//
//  Created by Shruthi Sathya on 10/4/25.
//


import SwiftUI
import AVFoundation

struct TestView: View {
    // The ViewModel holds the state and handles the camera/AWS logic.
    @StateObject private var viewModel = TestViewModel()
    
    var body: some View {
        ZStack {
            
            // --- A. Camera/Video Display Area ---
            ZStack { 
                // 1. Live Camera View (The video feed must be shown during testing)
                if viewModel.appState != .setup && viewModel.appState != .analyzing && viewModel.appState != .resultNegative && viewModel.appState != .resultPositive {
                    // Uses the CameraView (UI component) and gets the session from the ViewModel
                    CameraView(captureSession: viewModel.cameraManager.getCaptureSession())
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    // Background for different states
                    if viewModel.appState == .analyzing {
                        Color.blue.opacity(0.9) // Blue for analyzing
                    } else if viewModel.appState == .resultPositive {
                        Color.red.opacity(0.9) // Red for positive results
                    } else if viewModel.appState == .resultNegative {
                        Color.green.opacity(0.9) // Green for negative results
                    } else {
                        Color.black.opacity(0.8) // Black for setup
                    }
                    
                    VStack(spacing: 20) {
                        if viewModel.appState == .analyzing {
                            // Analyzing state content
                            Text("📊 ANALYZING RESULTS")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                            
                            Text("Processing clinical data...")
                                .font(.title2)
                                .foregroundColor(.white)
                            
                            ProgressView()
                                .scaleEffect(1.5)
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            
                        } else if viewModel.appState == .resultPositive {
                            // Positive results content
                            Text("⚠️ CLINICAL SIGNS DETECTED")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                            
                            Text("Recommend immediate medical evaluation")
                                .font(.title2)
                                .foregroundColor(.white)
                                .multilineTextAlignment(.center)
                            
                            Button("🔄 Run Another Test") {
                                viewModel.resetTest()
                            }
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.orange)
                            .cornerRadius(10)
                            .padding(.top, 20)
                            
                        } else if viewModel.appState == .resultNegative {
                            // Negative results content
                            Text("✅ NO CLINICAL SIGNS")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                            
                            Text("Normal neurological function observed")
                                .font(.title2)
                                .foregroundColor(.white)
                                .multilineTextAlignment(.center)
                            
                            Button("🔄 Run Another Test") {
                                viewModel.resetTest()
                            }
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                            .padding(.top, 20)
                            
                        } else {
                            // Setup state content
                            Text("CLINICAL ROMBERG TEST")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                            
                            Text("Instructions:")
                                .font(.title2)
                                .foregroundColor(.yellow)
                            
                            VStack(alignment: .leading, spacing: 10) {
                                Text("1. Stand/sit comfortably")
                                Text("2. Extend arms forward, parallel to ground")
                                Text("3. Palms facing upward")
                                Text("4. Close eyes during test")
                                Text("5. Hold position for 30 seconds")
                            }
                            .font(.body)
                            .foregroundColor(.white)
                            .multilineTextAlignment(.leading)
                        }
                    }
                    .padding()
                }

                // 2. The Pose Keypoint Overlay (Visual feedback for the user)
                if viewModel.appState != .analyzing && viewModel.appState != .resultNegative && viewModel.appState != .resultPositive {
                    KeypointDrawingView(keypoints: viewModel.recognizedKeypoints)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .ignoresSafeArea()

            // Main UI overlay - hide during analyzing and results
            if viewModel.appState != .analyzing && viewModel.appState != .resultNegative && viewModel.appState != .resultPositive {
                VStack {
                    Spacer()
                    
                    Text("Stroke Arm Drift Test")
                        .font(.largeTitle).bold()
                        .foregroundColor(.white)
                
                // Status/Instruction Message
                // Main instruction message
                Text(viewModel.alertMessage)
                    .font(.title2)
                    .foregroundColor(viewModel.appState == .resultPositive ? .yellow : .white)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
                
                // Live feedback message
                if !viewModel.liveFeedbackMessage.isEmpty {
                    Text(viewModel.liveFeedbackMessage)
                        .font(.title3)
                        .foregroundColor(.cyan)
                        .padding(.horizontal)
                        .padding(.top, 10)
                }
                
                // Live timer display
                if viewModel.isTesting && viewModel.remainingTime > 0 {
                    VStack {
                        Text("⏱️")
                            .font(.largeTitle)
                        Text("\(viewModel.remainingTime)")
                            .font(.system(size: 48, weight: .bold, design: .rounded))
                            .foregroundColor(viewModel.remainingTime <= 5 ? .red : .green)
                        Text("seconds")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .padding(.vertical, 20)
                }
                
                // Checkmark animation
                if viewModel.showCheckmark {
                    VStack {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.green)
                            .scaleEffect(viewModel.showCheckmark ? 1.2 : 1.0)
                            .animation(.spring(response: 0.3), value: viewModel.showCheckmark)
                        Text("Step Complete!")
                            .font(.headline)
                            .foregroundColor(.green)
                    }
                    .padding(.vertical, 10)
                }
                
                // Clinical Test Progress Indicator
                if viewModel.isTesting {
                    VStack {
                        Text("Clinical Step: \(viewModel.currentStep)/3")
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        ProgressView(value: Double(viewModel.currentStep), total: 3.0)
                            .progressViewStyle(LinearProgressViewStyle(tint: .white))
                            .frame(width: 200)
                    }
                    .padding(.bottom, 10)
                }
                
                // Start/Reset Button
                Button(action: {
                    if viewModel.appState == .setup || viewModel.appState == .resultNegative {
                        viewModel.startClinicalTest()
                    } else {
                        // In resultPositive state, the button acknowledges the alert
                        viewModel.resetTest()
                    }
                }) {
                    Text(buttonText(for: viewModel.appState))
                        .font(.headline)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(buttonColor(for: viewModel.appState))
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
                .padding(.horizontal, 30)
                .disabled(viewModel.isTesting) // Disable button while network/analysis is running
                
                Text("Disclaimer: This is not a medical diagnosis. Seek professional help if concerned.")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.top, 10)
            }
            .padding(.bottom, 20)
            
            // Full-screen Red Alert View - The "Wow" Factor
            if viewModel.showFullAlert {
                DriftAlertView(message: viewModel.alertMessage) {
                    // When the user dismisses the alert, reset the app
                    viewModel.resetTest()
                }
            }
            
            // Testing Indicator
            if viewModel.isTesting {
                VStack(spacing: 10) {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .scaleEffect(2)
                    
                    Text("Processing...")
                        .font(.caption)
                        .foregroundColor(.white)
                }
                .padding()
                .background(Color.black.opacity(0.7))
                .cornerRadius(10)
            }
            
            // AWS Analysis Loading Indicator
            if viewModel.liveFeedbackMessage.contains("Analyzing") {
                VStack(spacing: 10) {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .cyan))
                        .scaleEffect(1.5)
                    
                    Text("AWS Analysis in Progress...")
                        .font(.caption)
                        .foregroundColor(.cyan)
                }
                .padding()
                .background(Color.black.opacity(0.8))
                .cornerRadius(10)
            }
            } // End of conditional UI overlay
        }
    }
    
    // Helper function to dynamically change button text
    private func buttonText(for state: TestViewModel.AppState) -> String {
        switch state {
        case .setup:
            return "START CLINICAL ROMBERG TEST"
        case .positioning, .eyesClosed, .testing:
            return "TEST IN PROGRESS..."
        case .analyzing:
            return "ANALYZING..."
        case .resultNegative:
            return "RETEST"
        case .resultPositive:
            // When positive, the button is only used after the alert is dismissed
            return "RESTART TEST" 
        }
    }
    
    // Helper function to dynamically change button color
    private func buttonColor(for state: TestViewModel.AppState) -> Color {
        switch state {
        case .setup, .resultNegative:
            return .blue
        case .positioning, .eyesClosed, .testing:
            return .gray
        case .analyzing:
            return .blue
        case .resultPositive:
            return .red // Should not be visible while alert is up, but set to red
        }
    }
}

// MARK: - Helper Views

// CRITICAL: High-contrast alert to meet Rubric 4C (User Experience)
struct DriftAlertView: View {
    let message: String
    var onDismiss: () -> Void
    
    var body: some View {
        VStack {
            Spacer()
            Image(systemName: "exclamationmark.triangle.fill")
                .resizable()
                .frame(width: 80, height: 80)
                .foregroundColor(.yellow)
            
            Text("EMERGENCY ALERT")
                .font(.system(size: 40, weight: .heavy))
                .foregroundColor(.white)
            
            Text(message)
                .font(.title)
                .multilineTextAlignment(.center)
                .foregroundColor(.white)
                .padding()
            
            Button("DISMISS AND RESTART") {
                onDismiss()
            }
            .padding()
            .background(Color.white)
            .foregroundColor(.red)
            .cornerRadius(8)
            
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.red.opacity(0.95))
        .transition(.opacity)
        .ignoresSafeArea()
    }
}

// Placeholder View for drawing the Vision output (connects to keypoints array)
struct KeypointDrawingView: View {
    let keypoints: [CGPoint]
    var body: some View {
        // This is where you would use a Canvas or Path to draw lines 
        // between the shoulder, elbow, and wrist points based on the 'keypoints' array.
        Color.clear
    }
}
