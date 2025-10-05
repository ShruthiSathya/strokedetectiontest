#!/usr/bin/env python3
"""
Enhanced Video Analysis for Stroke Detection
Proper temporal analysis and computer vision for video streams
"""

import cv2
import numpy as np
import base64
import json
from typing import List, Dict, Tuple
import time
from collections import deque

class VideoStrokeAnalyzer:
    """
    Advanced video analysis for stroke detection using temporal patterns
    """
    
    def __init__(self, frame_buffer_size: int = 30, fps: int = 30):
        self.frame_buffer_size = frame_buffer_size
        self.fps = fps
        self.frame_buffer = deque(maxlen=frame_buffer_size)
        self.timestamp_buffer = deque(maxlen=frame_buffer_size)
        
        # NIHSS Clinical Thresholds
        self.NIHSS_0_NORMAL = 0.01      # <1% - No drift
        self.NIHSS_1_MILD = 0.03        # 1-3% - Mild drift
        self.NIHSS_2_MODERATE = 0.08    # 3-8% - Moderate drift
        self.NIHSS_3_SEVERE = 0.15      # 8-15% - Severe drift
        self.NIHSS_4_PARALYSIS = 0.25   # >15% - No movement
        
        # Temporal analysis parameters
        self.MINIMUM_TEST_DURATION = 10.0  # 10 seconds minimum
        self.DRIFT_DETECTION_WINDOW = 3.0  # Look for drift in first 3 seconds
        self.STABILITY_PERIOD = 7.0        # Need 7+ seconds of stability
        
    def add_frame(self, image_bytes: bytes) -> Dict:
        """
        Add a new frame to the analysis buffer
        
        Args:
            image_bytes: Base64 decoded image data
            
        Returns:
            Dict with current frame analysis
        """
        try:
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "Failed to decode image"}
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Store frame and timestamp
            current_time = time.time()
            self.frame_buffer.append(gray)
            self.timestamp_buffer.append(current_time)
            
            # Analyze current frame
            frame_analysis = self._analyze_single_frame(gray)
            
            # Perform temporal analysis if we have enough frames
            if len(self.frame_buffer) >= 10:  # At least 10 frames
                temporal_analysis = self._analyze_temporal_patterns()
                frame_analysis.update(temporal_analysis)
            
            return frame_analysis
            
        except Exception as e:
            return {"error": f"Frame analysis failed: {str(e)}"}
    
    def _analyze_single_frame(self, gray_image: np.ndarray) -> Dict:
        """
        Analyze a single frame for asymmetry patterns
        
        Args:
            gray_image: Grayscale image array
            
        Returns:
            Dict with frame analysis results
        """
        try:
            height, width = gray_image.shape
            
            # Split image into left and right halves
            left_half = gray_image[:, :width//2]
            right_half = gray_image[:, width//2:]
            
            # Calculate brightness asymmetry
            left_mean = np.mean(left_half)
            right_mean = np.mean(right_half)
            brightness_asymmetry = abs(left_mean - right_mean) / 255.0
            
            # Calculate texture asymmetry
            left_std = np.std(left_half)
            right_std = np.std(right_half)
            texture_asymmetry = abs(left_std - right_std) / 255.0
            
            # Calculate edge asymmetry (for movement detection)
            left_edges = cv2.Canny(left_half, 50, 150)
            right_edges = cv2.Canny(right_half, 50, 150)
            left_edge_density = np.sum(left_edges > 0) / (left_half.size)
            right_edge_density = np.sum(right_edges > 0) / (right_half.size)
            edge_asymmetry = abs(left_edge_density - right_edge_density)
            
            # Combined asymmetry score
            asymmetry_score = (brightness_asymmetry + texture_asymmetry + edge_asymmetry) / 3
            
            # Detect potential arm regions using edge detection
            arm_regions = self._detect_arm_regions(gray_image)
            
            return {
                'asymmetry_score': float(asymmetry_score),
                'brightness_asymmetry': float(brightness_asymmetry),
                'texture_asymmetry': float(texture_asymmetry),
                'edge_asymmetry': float(edge_asymmetry),
                'arm_regions_detected': len(arm_regions),
                'frame_quality': self._assess_frame_quality(gray_image),
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {"error": f"Single frame analysis failed: {str(e)}"}
    
    def _detect_arm_regions(self, gray_image: np.ndarray) -> List[Tuple]:
        """
        Detect potential arm regions using computer vision
        
        Args:
            gray_image: Grayscale image
            
        Returns:
            List of detected arm region coordinates
        """
        try:
            # Use contour detection to find potential arm regions
            edges = cv2.Canny(gray_image, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            arm_regions = []
            height, width = gray_image.shape
            
            for contour in contours:
                # Filter contours by size and position
                area = cv2.contourArea(contour)
                if area > 1000 and area < 10000:  # Reasonable arm size
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check if contour is in upper half (where arms would be)
                    if y < height // 2 and w > h:  # Horizontal orientation
                        arm_regions.append((x, y, w, h))
            
            return arm_regions
            
        except Exception as e:
            return []
    
    def _assess_frame_quality(self, gray_image: np.ndarray) -> Dict:
        """
        Assess the quality of the current frame
        
        Args:
            gray_image: Grayscale image
            
        Returns:
            Dict with quality metrics
        """
        try:
            # Calculate image sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
            
            # Calculate image brightness
            brightness = np.mean(gray_image)
            
            # Calculate image contrast
            contrast = np.std(gray_image)
            
            # Overall quality score (0-1)
            quality_score = min(laplacian_var / 1000.0, 1.0)  # Normalize sharpness
            
            return {
                'sharpness': float(laplacian_var),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'quality_score': float(quality_score),
                'is_good_quality': quality_score > 0.5
            }
            
        except Exception as e:
            return {"quality_score": 0.0, "is_good_quality": False}
    
    def _analyze_temporal_patterns(self) -> Dict:
        """
        Analyze temporal patterns across multiple frames
        
        Returns:
            Dict with temporal analysis results
        """
        try:
            if len(self.frame_buffer) < 5:
                return {"temporal_analysis": "insufficient_frames"}
            
            # Extract asymmetry scores over time
            asymmetry_scores = []
            timestamps = []
            
            for i, (frame, timestamp) in enumerate(zip(self.frame_buffer, self.timestamp_buffer)):
                # Re-analyze frame for consistency
                frame_analysis = self._analyze_single_frame(frame)
                if 'asymmetry_score' in frame_analysis:
                    asymmetry_scores.append(frame_analysis['asymmetry_score'])
                    timestamps.append(timestamp)
            
            if len(asymmetry_scores) < 3:
                return {"temporal_analysis": "insufficient_data"}
            
            # Calculate temporal metrics
            mean_asymmetry = np.mean(asymmetry_scores)
            std_asymmetry = np.std(asymmetry_scores)
            max_asymmetry = np.max(asymmetry_scores)
            min_asymmetry = np.min(asymmetry_scores)
            
            # Detect drift patterns
            drift_trend = self._calculate_drift_trend(asymmetry_scores, timestamps)
            drift_velocity = self._calculate_drift_velocity(asymmetry_scores, timestamps)
            
            # Calculate NIHSS score based on temporal analysis
            nihss_result = self._calculate_nihss_temporal(mean_asymmetry, drift_trend, drift_velocity)
            
            return {
                'temporal_analysis': 'complete',
                'mean_asymmetry': float(mean_asymmetry),
                'asymmetry_std': float(std_asymmetry),
                'max_asymmetry': float(max_asymmetry),
                'min_asymmetry': float(min_asymmetry),
                'drift_trend': float(drift_trend),
                'drift_velocity': float(drift_velocity),
                'nihss_temporal': nihss_result,
                'frame_count': len(asymmetry_scores),
                'analysis_duration': timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0
            }
            
        except Exception as e:
            return {"temporal_analysis": "failed", "error": str(e)}
    
    def _calculate_drift_trend(self, asymmetry_scores: List[float], timestamps: List[float]) -> float:
        """
        Calculate the drift trend over time (positive = increasing drift)
        
        Args:
            asymmetry_scores: List of asymmetry scores over time
            timestamps: Corresponding timestamps
            
        Returns:
            Drift trend (slope of asymmetry over time)
        """
        try:
            if len(asymmetry_scores) < 2:
                return 0.0
            
            # Simple linear regression to find trend
            x = np.array(timestamps)
            y = np.array(asymmetry_scores)
            
            # Calculate slope
            n = len(x)
            slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
            
            return slope
            
        except:
            return 0.0
    
    def _calculate_drift_velocity(self, asymmetry_scores: List[float], timestamps: List[float]) -> float:
        """
        Calculate the velocity of drift change
        
        Args:
            asymmetry_scores: List of asymmetry scores
            timestamps: Corresponding timestamps
            
        Returns:
            Drift velocity (change per second)
        """
        try:
            if len(asymmetry_scores) < 2:
                return 0.0
            
            # Calculate instantaneous velocities
            velocities = []
            for i in range(1, len(asymmetry_scores)):
                dt = timestamps[i] - timestamps[i-1]
                if dt > 0:
                    velocity = (asymmetry_scores[i] - asymmetry_scores[i-1]) / dt
                    velocities.append(velocity)
            
            return np.mean(velocities) if velocities else 0.0
            
        except:
            return 0.0
    
    def _calculate_nihss_temporal(self, mean_asymmetry: float, drift_trend: float, drift_velocity: float) -> Dict:
        """
        Calculate NIHSS score based on temporal analysis
        
        Args:
            mean_asymmetry: Average asymmetry over time
            drift_trend: Trend of drift over time
            drift_velocity: Velocity of drift change
            
        Returns:
            NIHSS assessment based on temporal patterns
        """
        # Base NIHSS score on mean asymmetry
        if mean_asymmetry < self.NIHSS_0_NORMAL:
            base_score = 0
            severity = "normal"
            interpretation = "No drift detected over test duration. Arms maintained stable position."
        elif mean_asymmetry < self.NIHSS_1_MILD:
            base_score = 1
            severity = "mild"
            interpretation = "Mild drift detected. Arms showed slight movement but maintained position."
        elif mean_asymmetry < self.NIHSS_2_MODERATE:
            base_score = 2
            severity = "moderate"
            interpretation = "Moderate drift detected. Arms showed noticeable movement."
        elif mean_asymmetry < self.NIHSS_3_SEVERE:
            base_score = 3
            severity = "severe"
            interpretation = "Severe drift detected. Arms showed significant movement or falling."
        else:
            base_score = 4
            severity = "critical"
            interpretation = "No movement detected or complete paralysis."
        
        # Adjust score based on temporal patterns
        if drift_trend > 0.01:  # Increasing drift over time
            base_score = min(base_score + 1, 4)
            interpretation += " Drift increased over time."
        
        if abs(drift_velocity) > 0.05:  # High drift velocity
            base_score = min(base_score + 1, 4)
            interpretation += " Rapid drift changes detected."
        
        return {
            'nihss_motor_score': base_score,
            'severity': severity,
            'interpretation': interpretation,
            'mean_asymmetry': mean_asymmetry,
            'drift_trend': drift_trend,
            'drift_velocity': drift_velocity
        }
    
    def get_final_assessment(self) -> Dict:
        """
        Get final assessment after video analysis
        
        Returns:
            Complete clinical assessment
        """
        try:
            if len(self.frame_buffer) < 5:
                return {"error": "Insufficient frames for assessment"}
            
            # Perform final temporal analysis
            temporal_analysis = self._analyze_temporal_patterns()
            
            # Calculate overall assessment
            if 'nihss_temporal' in temporal_analysis:
                nihss_result = temporal_analysis['nihss_temporal']
                
                return {
                    'assessment_complete': True,
                    'nihss_motor_score': nihss_result['nihss_motor_score'],
                    'severity': nihss_result['severity'],
                    'clinical_interpretation': nihss_result['interpretation'],
                    'mean_asymmetry': temporal_analysis.get('mean_asymmetry', 0),
                    'drift_trend': temporal_analysis.get('drift_trend', 0),
                    'drift_velocity': temporal_analysis.get('drift_velocity', 0),
                    'total_frames_analyzed': temporal_analysis.get('frame_count', 0),
                    'analysis_duration': temporal_analysis.get('analysis_duration', 0),
                    'assessment_method': 'temporal_video_analysis'
                }
            else:
                return {"error": "Failed to complete temporal analysis"}
                
        except Exception as e:
            return {"error": f"Final assessment failed: {str(e)}"}

# Example usage function
def analyze_video_stream(frame_data_list: List[bytes]) -> Dict:
    """
    Analyze a complete video stream for stroke detection
    
    Args:
        frame_data_list: List of base64 decoded image frames
        
    Returns:
        Complete stroke detection assessment
    """
    analyzer = VideoStrokeAnalyzer()
    
    # Process each frame
    frame_results = []
    for i, frame_data in enumerate(frame_data_list):
        result = analyzer.add_frame(frame_data)
        frame_results.append(result)
        
        # Log progress every 10 frames
        if i % 10 == 0:
            print(f"Processed frame {i+1}/{len(frame_data_list)}")
    
    # Get final assessment
    final_assessment = analyzer.get_final_assessment()
    
    return {
        'frame_results': frame_results,
        'final_assessment': final_assessment,
        'total_frames': len(frame_data_list)
    }

if __name__ == "__main__":
    # Example usage
    print("Enhanced Video Analysis for Stroke Detection")
    print("This system provides proper temporal analysis for video streams")
