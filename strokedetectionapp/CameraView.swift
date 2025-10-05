//
//  CameraView.swift
//  strokedetectionapp
//
//  Created by Shruthi Sathya on 10/4/25.
//
import SwiftUI
import AVFoundation

/// A SwiftUI view wrapper for the AVCaptureVideoPreviewLayer.
struct CameraView: UIViewControllerRepresentable {
    let captureSession: AVCaptureSession

    func makeUIViewController(context: Context) -> UIViewController {
        let viewController = UIViewController()
        
        // The layer that displays the camera feed
        let previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
        previewLayer.frame = viewController.view.bounds
        previewLayer.videoGravity = .resizeAspectFill
        
        // Set orientation for consistency (iOS 17+ compatible)
        if #available(iOS 17.0, *) {
            previewLayer.connection?.videoRotationAngle = 90.0
        } else {
            previewLayer.connection?.videoOrientation = .portrait
        }
        
        viewController.view.layer.addSublayer(previewLayer)
        
        return viewController
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {
        // Ensure the preview layer updates size on rotation/resize
        if let previewLayer = uiViewController.view.layer.sublayers?.first(where: { $0 is AVCaptureVideoPreviewLayer }) as? AVCaptureVideoPreviewLayer {
            previewLayer.frame = uiViewController.view.bounds
        }
    }
}
