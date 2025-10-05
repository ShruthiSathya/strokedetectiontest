// UPDATED TestView.swift - NIHSS Compliant Version
// Replace your existing TestView.swift with this updated version

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
                if viewModel.appState != .setup && viewModel.appState != .analyzing && viewModel.appState != .resultNegative && viewModel.appState != .resultPositive && viewModel.appState != .error {
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
                    } else if viewModel.appState == .error {
                        Color.orange.opacity(0.9) // Orange for error
                    } else {
                        Color.black.opacity(0.8) // Black for setup
                    }
                    
                    VStack(spacing: 20) {
                        if viewModel.appState == .analyzing {
                            // Analyzing state content
                            Text("📊 ANALYZING NIHSS RESULTS")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                            
                            Text("Processing NIHSS Motor Arm Test data...")
                                .font(.title2)
                                .foregroundColor(.white)
                            
                            // NIHSS Analysis Progress
                            VStack(spacing: 10) {
                                Text("🏥 NIHSS Motor Arm Test Analysis")
                                    .font(.headline)
                                    .foregroundColor(.cyan)
                                
                                Text("• Analyzing 10-second keypoint history")
                                Text("• Calculating drift progression")
                                Text("• Applying NIHSS scoring criteria")
                                Text("• Generating clinical assessment")
                            }
                            .font(.body)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.black.opacity(0.7))
                            .cornerRadius(10)
                        }
                        
                        else if viewModel.appState == .resultPositive {
                            // Positive results content with detailed NIHSS stats
                            VStack(spacing: 15) {
                                Text("⚠️ NIHSS CLINICAL SIGNS DETECTED")
                                    .font(.largeTitle)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                
                                Text("NIHSS Motor Arm Test indicates neurological findings")
                                    .font(.title2)
                                    .foregroundColor(.white)
                                    .multilineTextAlignment(.center)
                                
                                // Prominent Severity Display for Results
                                VStack(spacing: 8) {
                                    Text("NIHSS SEVERITY LEVEL")
                                        .font(.headline)
                                        .fontWeight(.bold)
                                        .foregroundColor(.yellow)
                                    
                                    Text(getDriftLevelDisplay(viewModel.testSeverity))
                                        .font(.title)
                                        .fontWeight(.bold)
                                        .foregroundColor(getSeverityColor(viewModel.testSeverity))
                                        .padding(.horizontal, 20)
                                        .padding(.vertical, 10)
                                        .background(Color.black.opacity(0.7))
                                        .cornerRadius(15)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 15)
                                                .stroke(getSeverityColor(viewModel.testSeverity), lineWidth: 2)
                                        )
                                    
                                    Text("Asymmetry: \(String(format: "%.1f", viewModel.yDifference * 100))%")
                                        .font(.subheadline)
                                        .foregroundColor(.white)
                                }
                                .padding(.vertical, 10)
                                
                                // NIHSS Medical Statistics Section
                                VStack(spacing: 10) {
                                    Text("🏥 NIHSS MOTOR ARM TEST RESULTS")
                                        .font(.headline)
                                        .foregroundColor(.yellow)
                                    
                                    VStack(spacing: 10) {
                                        // NIHSS Scores Section
                                        HStack {
                                            VStack(alignment: .leading, spacing: 5) {
                                                Text("📊 NIHSS SCORING")
                                                    .font(.caption)
                                                    .fontWeight(.bold)
                                                    .foregroundColor(.yellow)
                                                
                                                Text("Motor Arm Score: \(viewModel.clinicalScore)/4")
                                                Text("Severity Level: \(viewModel.testSeverity.uppercased())")
                                                Text("Clinical Interpretation: \(viewModel.clinicalDetails)")
                                            }
                                            
                                            Spacer()
                                            
                                            VStack(alignment: .trailing, spacing: 5) {
                                                Text("🔬 TEST QUALITY")
                                                    .font(.caption)
                                                    .fontWeight(.bold)
                                                    .foregroundColor(.yellow)
                                                
                                                Text("Test Duration: \(String(format: "%.1f", viewModel.testDuration))s")
                                                Text("Keypoint Snapshots: \(viewModel.keypointHistory.count)")
                                                Text("Eye Closure: \(viewModel.eyeClosed ? "✅" : "❌")")
                                                Text("Arm Angle Verified: \(viewModel.armAngleVerified ? "✅" : "❌")")
                                            }
                                        }
                                        .font(.caption)
                                        .foregroundColor(.white)
                                        
                                        // NIHSS Clinical Recommendation
                                        Text("NIHSS Clinical Assessment: \(viewModel.clinicalDetails)")
                                            .font(.caption)
                                            .fontWeight(.bold)
                                            .foregroundColor(.red)
                                            .multilineTextAlignment(.center)
                                            .padding(.vertical, 5)
                                            .background(Color.black.opacity(0.5))
                                            .cornerRadius(5)
                                    }
                                    .font(.caption)
                                    .foregroundColor(.white)
                                    .padding()
                                    .background(Color.black.opacity(0.3))
                                    .cornerRadius(10)
                                }
                                
                                Button("🔄 Run Another NIHSS Test") {
                                    viewModel.resetNihssTest()
                                    viewModel.resetTest()
                                }
                                .font(.title2)
                                .foregroundColor(.white)
                                .padding()
                                .background(Color.orange)
                                .cornerRadius(10)
                            }
                            
                        } else if viewModel.appState == .resultNegative {
                            // Negative results content with NIHSS stats
                            VStack(spacing: 15) {
                                Text("✅ NIHSS NO CLINICAL SIGNS")
                                    .font(.largeTitle)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                
                                Text("NIHSS Motor Arm Test shows normal motor function")
                                    .font(.title2)
                                    .foregroundColor(.white)
                                    .multilineTextAlignment(.center)
                                
                                // Prominent Severity Display for Results
                                VStack(spacing: 8) {
                                    Text("NIHSS SEVERITY LEVEL")
                                        .font(.headline)
                                        .fontWeight(.bold)
                                        .foregroundColor(.yellow)
                                    
                                    Text(getDriftLevelDisplay(viewModel.testSeverity))
                                        .font(.title)
                                        .fontWeight(.bold)
                                        .foregroundColor(getSeverityColor(viewModel.testSeverity))
                                        .padding(.horizontal, 20)
                                        .padding(.vertical, 10)
                                        .background(Color.black.opacity(0.7))
                                        .cornerRadius(15)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 15)
                                                .stroke(getSeverityColor(viewModel.testSeverity), lineWidth: 2)
                                        )
                                    
                                    Text("Asymmetry: \(String(format: "%.1f", viewModel.yDifference * 100))%")
                                        .font(.subheadline)
                                        .foregroundColor(.white)
                                }
                                .padding(.vertical, 10)
                                
                                // NIHSS Test Quality Section
                                VStack(spacing: 10) {
                                    Text("🏥 NIHSS MOTOR ARM TEST RESULTS")
                                        .font(.headline)
                                        .foregroundColor(.yellow)
                                    
                                    VStack(spacing: 10) {
                                        HStack {
                                            VStack(alignment: .leading, spacing: 5) {
                                                Text("📊 NIHSS SCORING")
                                                    .font(.caption)
                                                    .fontWeight(.bold)
                                                    .foregroundColor(.yellow)
                                                
                                                Text("Motor Arm Score: \(viewModel.clinicalScore)/4")
                                                Text("Severity Level: \(viewModel.testSeverity.uppercased())")
                                                Text("Clinical Interpretation: \(viewModel.clinicalDetails)")
                                            }
                                            
                                            Spacer()
                                            
                                            VStack(alignment: .trailing, spacing: 5) {
                                                Text("🔬 TEST QUALITY")
                                                    .font(.caption)
                                                    .fontWeight(.bold)
                                                    .foregroundColor(.yellow)
                                                
                                                Text("Test Duration: \(String(format: "%.1f", viewModel.testDuration))s")
                                                Text("Keypoint Snapshots: \(viewModel.keypointHistory.count)")
                                                Text("Eye Closure: \(viewModel.eyeClosed ? "✅" : "❌")")
                                                Text("Arm Angle Verified: \(viewModel.armAngleVerified ? "✅" : "❌")")
                                            }
                                        }
                                        .font(.caption)
                                        .foregroundColor(.white)
                                        
                                        Text("NIHSS Clinical Assessment: \(viewModel.clinicalDetails)")
                                            .font(.caption)
                                            .fontWeight(.bold)
                                            .foregroundColor(.green)
                                            .multilineTextAlignment(.center)
                                            .padding(.vertical, 5)
                                            .background(Color.black.opacity(0.5))
                                            .cornerRadius(5)
                                    }
                                    .font(.caption)
                                    .foregroundColor(.white)
                                    .padding()
                                    .background(Color.black.opacity(0.3))
                                    .cornerRadius(10)
                                }
                                
                                Button("🔄 Run Another NIHSS Test") {
                                    viewModel.resetNihssTest()
                                    viewModel.resetTest()
                                }
                                .font(.title2)
                                .foregroundColor(.white)
                                .padding()
                                .background(Color.blue)
                                .cornerRadius(10)
                            }
                        }
                        
                        else if viewModel.appState == .error {
                            // Error state content
                            VStack(spacing: 15) {
                                Text("❌ NIHSS TEST ERROR")
                                    .font(.largeTitle)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                
                                Text("NIHSS Motor Arm Test encountered an error")
                                    .font(.title2)
                                    .foregroundColor(.white)
                                
                                Text(viewModel.alertMessage)
                                    .font(.body)
                                    .foregroundColor(.white)
                                    .multilineTextAlignment(.center)
                                    .padding()
                                    .background(Color.black.opacity(0.7))
                                    .cornerRadius(10)
                                
                                Button("🔄 Retry NIHSS Test") {
                                    viewModel.resetNihssTest()
                                    viewModel.resetTest()
                                }
                                .font(.title2)
                                .foregroundColor(.white)
                                .padding()
                                .background(Color.blue)
                                .cornerRadius(10)
                            }
                        }
                    }
                    .padding()
                }

                // 2. The Pose Keypoint Overlay (Visual feedback for the user)
                if viewModel.appState != .analyzing && viewModel.appState != .resultNegative && viewModel.appState != .resultPositive && viewModel.appState != .error {
                KeypointDrawingView(keypoints: viewModel.recognizedKeypoints)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .ignoresSafeArea()

            // Main UI overlay - hide during analyzing, results, and error states
            if viewModel.appState != .analyzing && viewModel.appState != .resultNegative && viewModel.appState != .resultPositive && viewModel.appState != .error {
            VStack {
                Spacer()
                
                // Enhanced main title with better styling
                VStack(spacing: 8) {
                    Text("🏥 NIHSS Stroke Detection")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Text("Motor Arm Drift Test")
                        .font(.title2)
                        .fontWeight(.medium)
                        .foregroundColor(.cyan)
                }
                .padding(.top, 20)
                
                // Enhanced status/instruction message
                Text(viewModel.alertMessage)
                    .font(.title3)
                    .fontWeight(.medium)
                    .foregroundColor(viewModel.appState == .resultPositive ? .yellow : .white)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 20)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.black.opacity(0.6))
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.white.opacity(0.3), lineWidth: 1)
                            )
                    )
                
                // NIHSS Instructions Overlay
                if viewModel.showNihssInstructions {
                    VStack(spacing: 15) {
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
                                Text("Starting NIHSS test in:")
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
                                Text("Real-time NIHSS Drift:")
                                    .font(.headline)
                                    .foregroundColor(.white)
                                
                                Text("\(viewModel.realTimeDrift * 100, specifier: "%.1f")%")
                                    .font(.title)
                                    .fontWeight(.bold)
                                    .foregroundColor(viewModel.realTimeDrift > 0.15 ? .red : .green)
                                
                                Text("Snapshots: \(viewModel.keypointHistory.count)/20")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            .padding()
                        }
                    }
                    .padding()
                    .background(Color.black.opacity(0.8))
                    .cornerRadius(15)
                }
                
                Spacer()
                
                // Enhanced Main Action Button
                Button(action: {
                    switch viewModel.appState {
                    case .setup:
                        viewModel.startClinicalTest()
                    case .calibrating:
                        if viewModel.isCalibrated && !viewModel.isCountingDown {
                            viewModel.startTest() // This will now start NIHSS test
                        } else {
                            // Still calibrating or countdown in progress
                        }
                    case .testing:
                        // Test in progress
                        break
                    case .analyzing:
                        // Analysis in progress
                        break
                    case .resultPositive, .resultNegative:
                        viewModel.resetNihssTest()
                        viewModel.resetTest()
                    case .error:
                        viewModel.resetNihssTest()
                        viewModel.resetTest()
                    }
                }) {
                    HStack(spacing: 10) {
                        if viewModel.appState == .calibrating && viewModel.isCountingDown {
                            Image(systemName: "clock.fill")
                                .font(.title2)
                        } else if viewModel.appState == .testing {
                            Image(systemName: "hourglass")
                                .font(.title2)
                        } else if viewModel.appState == .analyzing {
                            Image(systemName: "brain.head.profile")
                                .font(.title2)
                        } else {
                            Image(systemName: "play.circle.fill")
                                .font(.title2)
                        }
                        
                        Text(buttonText(for: viewModel.appState))
                            .font(.title2)
                            .fontWeight(.bold)
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 18)
                    .padding(.horizontal, 20)
                    .background(
                        RoundedRectangle(cornerRadius: 20)
                            .fill(buttonColor(for: viewModel.appState))
                            .overlay(
                                RoundedRectangle(cornerRadius: 20)
                                    .stroke(Color.white.opacity(0.3), lineWidth: 1)
                            )
                    )
                    .scaleEffect(viewModel.appState == .calibrating && viewModel.isCountingDown ? 0.95 : 1.0)
                    .animation(.spring(response: 0.3), value: viewModel.isCountingDown)
                }
                .disabled(viewModel.appState == .testing || viewModel.appState == .analyzing || (viewModel.appState == .calibrating && viewModel.isCountingDown))
                .padding(.horizontal, 30)
                .padding(.bottom, 50)
            }
            }
            
            // Conditional UI overlay for different states
            if viewModel.appState != .analyzing && viewModel.appState != .resultNegative && viewModel.appState != .resultPositive && viewModel.appState != .error {
            VStack {
                // Calibration Status Display
                if viewModel.appState == .calibrating {
                    VStack(spacing: 15) {
                        Text("🔧 NIHSS Calibration Status")
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        // Enhanced calibration status with better visual feedback
                        VStack(spacing: 8) {
                            Text(viewModel.calibrationStatus)
                                .font(.title)
                                .fontWeight(.bold)
                                .foregroundColor(getCalibrationColor(viewModel.calibrationStatus))
                                .padding(.horizontal, 20)
                                .padding(.vertical, 10)
                                .background(getCalibrationBackgroundColor(viewModel.calibrationStatus))
                                .cornerRadius(15)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 15)
                                        .stroke(getCalibrationColor(viewModel.calibrationStatus), lineWidth: 2)
                                )
                            
                            Text(viewModel.calibrationFeedback)
                                .font(.body)
                                .foregroundColor(.white)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }
                        
                        // Auto-start countdown display (very prominent)
                        if viewModel.isCountingDown {
                            VStack(spacing: 10) {
                                Text("🚀 AUTO-STARTING TEST")
                                    .font(.headline)
                                    .fontWeight(.bold)
                                    .foregroundColor(.cyan)
                                
                                Text("\(viewModel.countdownNumber)")
                                    .font(.system(size: 72, weight: .bold, design: .rounded))
                                    .foregroundColor(.cyan)
                                    .scaleEffect(1.2)
                                    .animation(.spring(response: 0.3), value: viewModel.countdownNumber)
                                
                                Text("seconds")
                                    .font(.title2)
                                    .foregroundColor(.white)
                                
                                Text("Hold your position!")
                                    .font(.caption)
                                    .foregroundColor(.yellow)
                            }
                            .padding(20)
                            .background(
                                RoundedRectangle(cornerRadius: 20)
                                    .fill(Color.black.opacity(0.8))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 20)
                                            .stroke(Color.cyan, lineWidth: 3)
                                    )
                            )
                            .scaleEffect(1.05)
                            .animation(.spring(response: 0.5), value: viewModel.isCountingDown)
                        }
                        
                        // NIHSS-specific calibration info
                        if viewModel.armAngleVerified {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.green)
                                Text("Arms positioned correctly for NIHSS test")
                                    .font(.caption)
                                    .foregroundColor(.green)
                            }
                        }
                    }
                    .padding()
                    .background(Color.black.opacity(0.7))
                    .cornerRadius(15)
                    .padding(.top, 100)
                }
                
                // Enhanced live timer display for testing
                if viewModel.isTesting && viewModel.remainingTime > 0 {
                    VStack(spacing: 15) {
                        Text("🧪 NIHSS TEST IN PROGRESS")
                            .font(.headline)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                        
                        VStack(spacing: 10) {
                            Text("\(viewModel.remainingTime)")
                                .font(.system(size: 80, weight: .bold, design: .rounded))
                                .foregroundColor(viewModel.remainingTime <= 5 ? .red : .green)
                                .scaleEffect(viewModel.remainingTime <= 5 ? 1.3 : 1.0)
                                .animation(.spring(response: 0.3), value: viewModel.remainingTime)
                            
                            Text("seconds remaining")
                                .font(.title2)
                                .foregroundColor(.white)
                            
                            if viewModel.remainingTime <= 5 {
                                Text("⚠️ FINAL COUNTDOWN!")
                                    .font(.headline)
                                    .fontWeight(.bold)
                                    .foregroundColor(.red)
                                    .padding(.horizontal, 20)
                                    .padding(.vertical, 8)
                                    .background(Color.red.opacity(0.2))
                                    .cornerRadius(10)
                            }
                        }
                        .padding(25)
                        .background(
                            RoundedRectangle(cornerRadius: 25)
                                .fill(Color.black.opacity(0.8))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 25)
                                        .stroke(viewModel.remainingTime <= 5 ? Color.red : Color.green, lineWidth: 4)
                                )
                        )
                        .scaleEffect(viewModel.remainingTime <= 5 ? 1.1 : 1.0)
                        .animation(.spring(response: 0.5), value: viewModel.remainingTime)
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
                        Text("NIHSS Step Complete!")
                            .font(.headline)
                            .foregroundColor(.green)
                    }
                    .padding(.vertical, 10)
                }
                
                // Clinical Test Progress Indicator
                if viewModel.isTesting {
                    VStack {
                        Text("NIHSS Clinical Step: \(viewModel.currentStep)/3")
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        ProgressView(value: Double(viewModel.currentStep), total: 3.0)
                            .progressViewStyle(LinearProgressViewStyle(tint: .white))
                            .frame(width: 200)
                        
                        Text("NIHSS Motor Arm Test in Progress")
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                    .padding()
                    .background(Color.black.opacity(0.7))
                    .cornerRadius(10)
                }
                
                // Live feedback message
                if !viewModel.liveFeedbackMessage.isEmpty {
                    Text(viewModel.liveFeedbackMessage)
                        .font(.body)
                        .foregroundColor(.cyan)
                        .multilineTextAlignment(.center)
                        .padding()
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(10)
                }
                
                Spacer()
            }
            
            // Loading indicators
            if viewModel.isTesting {
                VStack(spacing: 10) {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    .scaleEffect(2)
                    
                    Text("NIHSS Analysis in Progress...")
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
                    
                    Text("AWS NIHSS Analysis in Progress...")
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
            return "START NIHSS CALIBRATION"
        case .calibrating:
            if viewModel.isCountingDown {
                return "AUTO-STARTING IN \(viewModel.countdownNumber)s"
            } else if viewModel.isCalibrated {
                return "START NIHSS TEST"
            } else {
                return "CALIBRATING..."
            }
        case .testing:
            return "NIHSS TEST IN PROGRESS..."
        case .analyzing:
            return "ANALYZING NIHSS RESULTS..."
        case .resultNegative:
            return "RUN ANOTHER NIHSS TEST"
        case .resultPositive:
            return "RUN ANOTHER NIHSS TEST"
        case .error:
            return "RETRY NIHSS TEST"
        }
    }
    
    // Helper function to dynamically change button color
    private func buttonColor(for state: TestViewModel.AppState) -> Color {
        switch state {
        case .setup:
            return .blue
        case .calibrating:
            if viewModel.isCountingDown {
                return .cyan
            } else if viewModel.isCalibrated {
                return .green
            } else {
                return .orange
            }
        case .testing:
            return .gray
        case .analyzing:
            return .blue
        case .resultNegative, .resultPositive:
            return .blue
        case .error:
            return .blue
        }
    }
    
    // Helper function for drift level display
    private func getDriftLevelDisplay(_ severity: String) -> String {
        switch severity.lowercased() {
        case "normal": return "✅ NORMAL"
        case "mild": return "⚠️ MILD"
        case "moderate": return "🔶 MODERATE"
        case "severe": return "🚨 SEVERE"
        case "critical": return "🚨 CRITICAL"
        default: return "❓ UNKNOWN"
        }
    }
    
    // Helper function for severity color
    private func getSeverityColor(_ severity: String) -> Color {
        switch severity.lowercased() {
        case "normal": return .green
        case "mild": return .yellow
        case "moderate": return .orange
        case "severe": return .red
        case "critical": return .purple
        default: return .gray
        }
    }
    
    // Helper function for calibration status color
    private func getCalibrationColor(_ status: String) -> Color {
        if status.contains("Perfect") {
            return .green
        } else if status.contains("Good") {
            return .blue
        } else if status.contains("Acceptable") {
            return .yellow
        } else if status.contains("Poor") {
            return .orange
        } else if status.contains("Too Far") {
            return .red
        } else {
            return .gray
        }
    }
    
    // Helper function for calibration background color
    private func getCalibrationBackgroundColor(_ status: String) -> Color {
        if status.contains("Perfect") {
            return Color.green.opacity(0.2)
        } else if status.contains("Good") {
            return Color.blue.opacity(0.2)
        } else if status.contains("Acceptable") {
            return Color.yellow.opacity(0.2)
        } else if status.contains("Poor") {
            return Color.orange.opacity(0.2)
        } else if status.contains("Too Far") {
            return Color.red.opacity(0.2)
        } else {
            return Color.gray.opacity(0.2)
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
            
            Text("NIHSS EMERGENCY ALERT")
                .font(.system(size: 40, weight: .heavy))
                .foregroundColor(.white)
            
            Text(message)
                .font(.system(size: 24, weight: .medium))
                .foregroundColor(.white)
                .multilineTextAlignment(.center)
                .padding()
            
            Button("OK") {
                onDismiss()
            }
            .font(.system(size: 20, weight: .bold))
            .foregroundColor(.black)
            .padding()
            .background(Color.yellow)
            .cornerRadius(10)
            
            Spacer()
        }
        .background(Color.red.opacity(0.9))
        .ignoresSafeArea()
    }
}

// MARK: - KeypointDrawingView

struct KeypointDrawingView: View {
    let keypoints: [CGPoint]
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // Draw keypoints as circles with different colors for different body parts
                ForEach(Array(keypoints.enumerated()), id: \.offset) { index, keypoint in
                    Circle()
                        .fill(getKeypointColor(for: index))
                        .frame(width: 10, height: 10)
                        .overlay(
                            Circle()
                                .stroke(Color.white, lineWidth: 2)
                        )
                        .position(
                            x: keypoint.x * geometry.size.width,
                            y: keypoint.y * geometry.size.height
                        )
                }
                
                // Draw arm connections if we have enough keypoints
                if keypoints.count >= 6 {
                    // Left arm connection
                    Path { path in
                        let shoulder = CGPoint(
                            x: keypoints[2].x * geometry.size.width,
                            y: keypoints[2].y * geometry.size.height
                        )
                        let elbow = CGPoint(
                            x: keypoints[1].x * geometry.size.width,
                            y: keypoints[1].y * geometry.size.height
                        )
                        let wrist = CGPoint(
                            x: keypoints[0].x * geometry.size.width,
                            y: keypoints[0].y * geometry.size.height
                        )
                        
                        path.move(to: shoulder)
                        path.addLine(to: elbow)
                        path.addLine(to: wrist)
                    }
                    .stroke(Color.red, lineWidth: 2)
                    
                    // Right arm connection
                    Path { path in
                        let shoulder = CGPoint(
                            x: keypoints[5].x * geometry.size.width,
                            y: keypoints[5].y * geometry.size.height
                        )
                        let elbow = CGPoint(
                            x: keypoints[4].x * geometry.size.width,
                            y: keypoints[4].y * geometry.size.height
                        )
                        let wrist = CGPoint(
                            x: keypoints[3].x * geometry.size.width,
                            y: keypoints[3].y * geometry.size.height
                        )
                        
                        path.move(to: shoulder)
                        path.addLine(to: elbow)
                        path.addLine(to: wrist)
                    }
                    .stroke(Color.blue, lineWidth: 2)
                }
            }
        }
    }
    
    private func getKeypointColor(for index: Int) -> Color {
        // Color-code different keypoints for easier identification
        switch index {
        case 0...2: return .red      // Left arm (wrist, elbow, shoulder)
        case 3...5: return .blue     // Right arm (wrist, elbow, shoulder)
        default: return .green       // Other keypoints
        }
    }
}
