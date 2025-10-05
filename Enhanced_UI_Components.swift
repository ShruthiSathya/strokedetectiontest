// MARK: - Enhanced UI Components for Frame Collection
import SwiftUI

// MARK: - Enhanced TestView with Frame Collection UI
struct EnhancedTestView: View {
    @StateObject private var viewModel = TestViewModel()
    
    var body: some View {
        ZStack {
            // Camera view
            CameraView()
                .ignoresSafeArea()
            
            VStack {
                // Top status bar
                HStack {
                    Text("🧠 Stroke Detection")
                        .font(.headline)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Text("Enhanced v2.0")
                        .font(.caption)
                        .foregroundColor(.blue)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.2))
                        .cornerRadius(8)
                }
                .padding()
                .background(Color.black.opacity(0.7))
                
                Spacer()
                
                // Enhanced frame collection progress
                if viewModel.frameCollectionActive {
                    VStack {
                        Text("🎬 Collecting frames for analysis...")
                            .font(.headline)
                            .foregroundColor(.blue)
                            .multilineTextAlignment(.center)
                        
                        ProgressView(value: viewModel.frameCollectionProgress)
                            .progressViewStyle(LinearProgressViewStyle())
                            .frame(height: 8)
                            .tint(.blue)
                        
                        HStack {
                            Text("\(viewModel.framesCollected)")
                                .fontWeight(.bold)
                                .foregroundColor(.blue)
                            Text("/ \(viewModel.totalFramesToCollect) frames")
                                .foregroundColor(.secondary)
                        }
                        .font(.caption)
                        
                        Text("Frame-by-frame video analysis")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(12)
                    .padding(.horizontal)
                }
                
                // Main content based on app state
                VStack(spacing: 20) {
                    switch viewModel.appState {
                    case .setup:
                        SetupView()
                    case .calibrating:
                        CalibrationView()
                    case .testing:
                        TestingView()
                    case .analyzing:
                        AnalyzingView()
                    case .resultPositive, .resultNegative:
                        EnhancedResultsView()
                    case .error:
                        ErrorView()
                    }
                }
                .padding()
                .background(Color.black.opacity(0.7))
                .cornerRadius(16)
                .padding()
                
                Spacer()
            }
        }
    }
}

// MARK: - Enhanced Results View with Temporal Metrics
struct EnhancedResultsView: View {
    @ObservedObject var viewModel: TestViewModel
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Main result header
                HStack {
                    Image(systemName: viewModel.testSeverity == "normal" ? "checkmark.circle.fill" : "exclamationmark.triangle.fill")
                        .font(.largeTitle)
                        .foregroundColor(viewModel.testSeverity == "normal" ? .green : .orange)
                    
                    VStack(alignment: .leading) {
                        Text(viewModel.testSeverity == "normal" ? "✅ Normal Results" : "⚠️ Drift Detected")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(viewModel.testSeverity == "normal" ? .green : .orange)
                        
                        Text("Enhanced Frame-by-Frame Analysis")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                }
                
                // NIHSS Score Card
                HStack {
                    VStack(alignment: .leading) {
                        Text("NIHSS Motor Score")
                            .font(.headline)
                            .fontWeight(.semibold)
                        
                        Text("Arm Drift Assessment")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text("\(viewModel.motorArmScore)/4")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.blue)
                        
                        Text(getNIHSSSeverityText(viewModel.motorArmScore))
                            .font(.caption)
                            .foregroundColor(.blue)
                    }
                }
                .padding()
                .background(Color.blue.opacity(0.1))
                .cornerRadius(12)
                
                // Enhanced Analysis Metrics
                if viewModel.testQuality.contains("enhanced") {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("📊 Enhanced Analysis Results")
                            .font(.headline)
                            .fontWeight(.semibold)
                        
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 12) {
                            MetricCard(title: "Y-Difference", value: "\(viewModel.yDifference * 100, specifier: "%.2f")%", color: .blue)
                            MetricCard(title: "Test Quality", value: viewModel.testQuality, color: .green)
                            MetricCard(title: "Analysis Method", value: "Frame-by-Frame", color: .purple)
                            MetricCard(title: "Clinical Standards", value: "NIHSS Motor", color: .orange)
                        }
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                }
                
                // Clinical Assessment
                VStack(alignment: .leading, spacing: 8) {
                    Text("🏥 Clinical Assessment")
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    Text(viewModel.clinicalDetails.isEmpty ? "Assessment completed successfully." : viewModel.clinicalDetails)
                        .font(.body)
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                }
                
                // Enhanced Features Info
                VStack(alignment: .leading, spacing: 8) {
                    Text("🚀 Enhanced Features")
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        FeatureRow(icon: "🎬", title: "Frame-by-Frame Analysis", description: "600 frames analyzed over 20 seconds")
                        FeatureRow(icon: "⚡", title: "Drift Velocity Detection", description: "Measures arm movement speed")
                        FeatureRow(icon: "📊", title: "Temporal Pattern Analysis", description: "Tracks drift trends over time")
                        FeatureRow(icon: "🏥", title: "NIHSS Clinical Standards", description: "Research-based scoring system")
                    }
                }
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(12)
                
                // Action buttons
                HStack(spacing: 16) {
                    Button("🔄 Test Again") {
                        viewModel.resetTest()
                    }
                    .buttonStyle(PrimaryButtonStyle())
                    
                    Button("📋 Share Results") {
                        // Share functionality
                    }
                    .buttonStyle(SecondaryButtonStyle())
                }
            }
            .padding()
        }
    }
    
    private func getNIHSSSeverityText(_ score: Int) -> String {
        switch score {
        case 0: return "Normal"
        case 1: return "Mild"
        case 2: return "Moderate"
        case 3: return "Severe"
        case 4: return "Critical"
        default: return "Unknown"
        }
    }
}

// MARK: - Supporting UI Components
struct MetricCard: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(value)
                .font(.headline)
                .fontWeight(.semibold)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

struct FeatureRow: View {
    let icon: String
    let title: String
    let description: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text(icon)
                .font(.title2)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
    }
}

struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundColor(.white)
            .padding()
            .frame(maxWidth: .infinity)
            .background(Color.blue)
            .cornerRadius(12)
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
    }
}

struct SecondaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundColor(.blue)
            .padding()
            .frame(maxWidth: .infinity)
            .background(Color.blue.opacity(0.1))
            .cornerRadius(12)
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
    }
}

// MARK: - Placeholder Views
struct SetupView: View {
    var body: some View {
        Text("Setup View")
    }
}

struct CalibrationView: View {
    var body: some View {
        Text("Calibration View")
    }
}

struct TestingView: View {
    var body: some View {
        Text("Testing View")
    }
}

struct AnalyzingView: View {
    var body: some View {
        Text("Analyzing View")
    }
}

struct ErrorView: View {
    var body: some View {
        Text("Error View")
    }
}
