//
//  CameraManager.swift
//  strokedetectionapp
//
//  Created by Shruthi Sathya on 10/4/25.
//


import Foundation
import AVFoundation
import Vision
import CoreGraphics
import CoreImage
import UIKit

/// Manages the camera session, captures frames, and runs the Vision pose estimation.
class CameraManager: NSObject, ObservableObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    
    // The main object that captures video/audio data
    private let captureSession = AVCaptureSession()
    
    // Delegate for pose estimation results
    var poseEstimationHandler: (([CGPoint]) -> Void)?
    
    // Store latest keypoints for AWS transmission
    @Published var latestKeypoints: [String: CGPoint] = [:]
    
    override init() {
        super.init()
        checkPermissions()
        setupSession()
    }
    
    // Checks if the user granted camera access
    private func checkPermissions() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized: // Already authorized
            break
        case .notDetermined: // Request permission
            AVCaptureDevice.requestAccess(for: .video) { granted in
                if !granted { fatalError("Camera access denied.") }
            }
        case .denied, .restricted: // Permission denied
            fatalError("Camera access required for this application.")
        @unknown default:
            fatalError("Unknown authorization status.")
        }
    }
    
    private func setupSession() {
        // Set up the front camera input
        guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) else {
            fatalError("Front camera not available.")
        }
        
        do {
            let input = try AVCaptureDeviceInput(device: camera)
            if captureSession.canAddInput(input) {
                captureSession.addInput(input)
            }
            
            // Set up video output for processing frames
            let videoOutput = AVCaptureVideoDataOutput()
            videoOutput.setSampleBufferDelegate(self, queue: DispatchQueue(label: "videoQueue"))
            
            // Set pixel format for Vision processing
            videoOutput.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
            
            if captureSession.canAddOutput(videoOutput) {
                captureSession.addOutput(videoOutput)
            }
            
            // Use the front camera's portrait orientation (iOS 17+ compatible)
            if let connection = videoOutput.connection(with: .video) {
                if #available(iOS 17.0, *) {
                    if connection.isVideoRotationAngleSupported(90.0) {
                        connection.videoRotationAngle = 90.0
                    }
                } else {
                    if connection.isVideoOrientationSupported {
                        connection.videoOrientation = .portrait
                    }
                }
            }
            
        } catch {
            fatalError("Error setting up camera input: \(error.localizedDescription)")
        }
    }
    
    /// Starts the camera feed and analysis.
    func start() {
        if !captureSession.isRunning {
            DispatchQueue.global(qos: .userInitiated).async {
                self.captureSession.startRunning()
            }
        }
    }
    
    /// Stops the camera feed.
    func stop() {
        if captureSession.isRunning {
            self.captureSession.stopRunning()
        }
    }
    
    // MARK: - AVCaptureVideoDataOutputSampleBufferDelegate (Frame Processing)
    
    // Called for every frame captured by the camera
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        // Store the latest pixel buffer for capture
        self.latestPixelBuffer = pixelBuffer
        
        // 1. Create a request to recognize the human body pose
        let request = VNDetectHumanBodyPoseRequest { [weak self] request, error in
            if let error = error {
                print("Vision error: \(error.localizedDescription)")
                return
            }
            
            // 2. Process results
            guard let observations = request.results as? [VNHumanBodyPoseObservation] else { return }
            
            var armKeypoints: [CGPoint] = []
            
            // Extract specific keypoints needed for stroke detection
            for observation in observations {
                // Extract specific keypoints with confidence filtering
                var specificKeypoints: [String: CGPoint] = [:]
                
                // Left arm keypoints
                do {
                    let leftWrist = try observation.recognizedPoint(.leftWrist)
                    print("🔍 Left wrist confidence: \(leftWrist.confidence)")
                    if leftWrist.confidence > 0.3 { // Lowered threshold for better detection
                        specificKeypoints["left_wrist"] = leftWrist.location
                        print("✅ Left wrist detected")
                    }
                } catch {
                    print("❌ Left wrist detection failed")
                }
                
                do {
                    let leftShoulder = try observation.recognizedPoint(.leftShoulder)
                    print("🔍 Left shoulder confidence: \(leftShoulder.confidence)")
                    if leftShoulder.confidence > 0.3 { // Lowered threshold
                        specificKeypoints["left_shoulder"] = leftShoulder.location
                        print("✅ Left shoulder detected")
                    }
                } catch {
                    print("❌ Left shoulder detection failed")
                }
                
                // Right arm keypoints
                do {
                    let rightWrist = try observation.recognizedPoint(.rightWrist)
                    print("🔍 Right wrist confidence: \(rightWrist.confidence)")
                    if rightWrist.confidence > 0.3 { // Lowered threshold
                        specificKeypoints["right_wrist"] = rightWrist.location
                        print("✅ Right wrist detected")
                    }
                } catch {
                    print("❌ Right wrist detection failed")
                }
                
                do {
                    let rightShoulder = try observation.recognizedPoint(.rightShoulder)
                    print("🔍 Right shoulder confidence: \(rightShoulder.confidence)")
                    if rightShoulder.confidence > 0.3 { // Lowered threshold
                        specificKeypoints["right_shoulder"] = rightShoulder.location
                        print("✅ Right shoulder detected")
                    }
                } catch {
                    print("❌ Right shoulder detection failed")
                }
                
                // Additional keypoints for better calibration
                do {
                    let leftElbow = try observation.recognizedPoint(.leftElbow)
                    print("🔍 Left elbow confidence: \(leftElbow.confidence)")
                    if leftElbow.confidence > 0.3 { // Lowered threshold
                        specificKeypoints["left_elbow"] = leftElbow.location
                        print("✅ Left elbow detected")
                    }
                } catch {
                    print("❌ Left elbow detection failed")
                }
                
                do {
                    let rightElbow = try observation.recognizedPoint(.rightElbow)
                    print("🔍 Right elbow confidence: \(rightElbow.confidence)")
                    if rightElbow.confidence > 0.3 { // Lowered threshold
                        specificKeypoints["right_elbow"] = rightElbow.location
                        print("✅ Right elbow detected")
                    }
                } catch {
                    print("❌ Right elbow detection failed")
                }
                
                // Validate keypoints are within bounds
                let validKeypoints = specificKeypoints.filter { (key, point) in
                    return point.x >= 0 && point.x <= 1 && point.y >= 0 && point.y <= 1
                }
                
                // Convert to array of CGPoints for backward compatibility
                let keypointArray = Array(validKeypoints.values)
                
                // Store the specific keypoints for AWS transmission
                DispatchQueue.main.async {
                    // Pass both the array (for backward compatibility) and the specific keypoints
                    self?.poseEstimationHandler?(keypointArray)
                    
                    // Store specific keypoints for AWS payload
                    self?.latestKeypoints = validKeypoints
                    
                    // Debug information
                    print("📊 Total keypoints detected: \(keypointArray.count)")
                    print("📊 Specific keypoints: \(validKeypoints.keys.joined(separator: ", "))")
                    print("📊 Confidence levels: \(validKeypoints.count) keypoints above 0.3 threshold")
                }
                
                break // Process first valid observation only
            }
        }
        
        // 3. Execute the request on the background queue
        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, options: [:])
        do {
            try handler.perform([request])
        } catch {
            print("Failed to perform Vision request: \(error.localizedDescription)")
        }
    }
    
    // Provides the AVCaptureSession to the CameraView for display
    func getCaptureSession() -> AVCaptureSession {
        return captureSession
    }
    
    // Captures the current frame as image data for AWS transmission
    func captureCurrentFrame(completion: @escaping (Data?) -> Void) {
        // Store the latest pixel buffer for capture
        // This will be set by the video output delegate
        guard let latestPixelBuffer = self.latestPixelBuffer else {
            print("❌ No pixel buffer available for capture")
            completion(nil)
            return
        }
        
        // Convert pixel buffer to JPEG data
        let ciImage = CIImage(cvPixelBuffer: latestPixelBuffer)
        let context = CIContext()
        
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else {
            print("❌ Failed to create CGImage from pixel buffer")
            completion(nil)
            return
        }
        
        let uiImage = UIImage(cgImage: cgImage)
        guard let imageData = uiImage.jpegData(compressionQuality: 0.8) else {
            print("❌ Failed to convert UIImage to JPEG data")
            completion(nil)
            return
        }
        
        print("✅ Captured real image from camera: \(imageData.count) bytes")
        completion(imageData)
    }
    
    // Store the latest pixel buffer for capture
    private var latestPixelBuffer: CVPixelBuffer?
}

// Helper class to handle photo capture completion
class PhotoCaptureDelegate: NSObject, AVCapturePhotoCaptureDelegate {
    private let completion: (Data?) -> Void
    
    init(completion: @escaping (Data?) -> Void) {
        self.completion = completion
    }
    
    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        if let error = error {
            print("Photo capture error: \(error.localizedDescription)")
            completion(nil)
            return
        }
        
        guard let imageData = photo.fileDataRepresentation() else {
            print("Failed to get image data from photo")
            completion(nil)
            return
        }
        
        completion(imageData)
    }
}
