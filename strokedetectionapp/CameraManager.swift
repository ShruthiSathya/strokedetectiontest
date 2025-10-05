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

/// Manages the camera session, captures frames, and runs the Vision pose estimation.
class CameraManager: NSObject, ObservableObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    
    // The main object that captures video/audio data
    private let captureSession = AVCaptureSession()
    
    // Delegate for pose estimation results
    var poseEstimationHandler: (([CGPoint]) -> Void)?
    
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
        
        // 1. Create a request to recognize the human body pose
        let request = VNDetectHumanBodyPoseRequest { [weak self] request, error in
            if let error = error {
                print("Vision error: \(error.localizedDescription)")
                return
            }
            
            // 2. Process results
            guard let observations = request.results as? [VNRecognizedPointsObservation] else { return }
            
            var armKeypoints: [CGPoint] = []
            
            // Simple logic to extract keypoints for the two arms
            for observation in observations {
                guard let recognizedPoints = try? observation.recognizedPoints(forGroupKey: .all) else { continue }
                
                // Extract keypoints with higher confidence and better filtering
                let availablePoints = recognizedPoints.compactMap { (key, point) -> CGPoint? in
                    // Only include points with high confidence
                    guard point.confidence > 0.7 else { return nil }
                    return point.location
                }
                
                // Ensure we have enough points for validation
                guard availablePoints.count >= 2 else { continue }
                
                // Additional validation: Check if points are in reasonable positions
                let validPoints = availablePoints.filter { point in
                    // Points should be within screen bounds (normalized coordinates 0-1)
                    return point.x >= 0 && point.x <= 1 && point.y >= 0 && point.y <= 1
                }
                
                guard validPoints.count >= 2 else { continue }
                
                // Pass back the validated points to the ViewModel
                armKeypoints.append(contentsOf: validPoints)
                
                // CRITICAL: We pass the average Y-coordinate of the whole arm to the ViewModel
                DispatchQueue.main.async {
                    self?.poseEstimationHandler?(armKeypoints)
                    
                    // Here is where the ViewModel will take the average Y-coordinate and send it to AWS!
                    // This is handled by the ViewModel, which holds a reference to this class.
                }
                
                // For a hackathon, we only process the first arm found for simplicity.
                break 
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
        // Create a photo output for capturing still images
        let photoOutput = AVCapturePhotoOutput()
        
        // Add photo output to session if possible
        if captureSession.canAddOutput(photoOutput) {
            captureSession.addOutput(photoOutput)
        }
        
        // Configure photo settings (iOS 16+ compatible)
        let settings = AVCapturePhotoSettings()
        if #available(iOS 16.0, *) {
            // Use maxPhotoDimensions for iOS 16+
            settings.maxPhotoDimensions = CMVideoDimensions(width: 1920, height: 1080)
        } else {
            // Use deprecated property for older iOS versions
            settings.isHighResolutionPhotoEnabled = false
        }
        
        // Capture the photo
        photoOutput.capturePhoto(with: settings, delegate: PhotoCaptureDelegate(completion: completion))
    }
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
