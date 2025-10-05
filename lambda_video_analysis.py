#!/usr/bin/env python3
"""
Enhanced Lambda function with proper video analysis for stroke detection
"""

import json
import base64
import logging
import boto3
import time
from typing import List, Dict
from enhanced_video_analysis import VideoStrokeAnalyzer

# Initialize the Rekognition client
rekognition_client = boto3.client('rekognition')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clinical thresholds based on NIHSS and research standards
NIHSS_0_NORMAL = 0.01           # <1% - No drift
NIHSS_1_MILD = 0.03            # 1-3% - Mild drift
NIHSS_2_MODERATE = 0.08        # 3-8% - Moderate drift
NIHSS_3_SEVERE = 0.15          # 8-15% - Severe drift
NIHSS_4_PARALYSIS = 0.25       # >15% - No movement

def lambda_handler(event, context):
    try:
        print(f"DEBUG: Video analysis event received")
        
        # Parse the event - can handle single frames or video sequences
        if 'frames' in event:
            # Multi-frame video analysis
            return handle_video_analysis(event, context)
        else:
            # Single frame analysis (backward compatibility)
            return handle_single_frame(event, context)
            
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e), 'drift_detected': False})
        }

def handle_video_analysis(event, context):
    """
    Handle multi-frame video analysis for accurate stroke detection
    """
    try:
        print(f"DEBUG: Processing video analysis with {len(event.get('frames', []))} frames")
        
        # Extract video frames
        frames_data = event.get('frames', [])
        user_id = event.get('user_id', 'unknown')
        keypoints_detected = event.get('keypoints_detected', 0)
        test_duration = event.get('test_duration', 20.0)
        
        if not frames_data:
            return create_error_response("No video frames provided")
        
        # Initialize video analyzer
        analyzer = VideoStrokeAnalyzer(frame_buffer_size=len(frames_data), fps=30)
        
        # Process each frame
        frame_analyses = []
        for i, frame_data in enumerate(frames_data):
            try:
                # Decode base64 frame data
                image_bytes = base64.b64decode(frame_data)
                
                # Analyze frame
                frame_result = analyzer.add_frame(image_bytes)
                frame_analyses.append(frame_result)
                
                print(f"DEBUG: Processed frame {i+1}/{len(frames_data)}")
                
            except Exception as e:
                print(f"DEBUG: Error processing frame {i+1}: {e}")
                continue
        
        # Get final assessment
        final_assessment = analyzer.get_final_assessment()
        
        if 'error' in final_assessment:
            return create_error_response(f"Video analysis failed: {final_assessment['error']}")
        
        # Generate clinical response
        response = generate_clinical_response_video(final_assessment, user_id, keypoints_detected, test_duration)
        
        print(f"DEBUG: Video analysis complete - NIHSS: {final_assessment.get('nihss_motor_score', 'unknown')}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Error in video analysis: {e}")
        return create_error_response(f"Video analysis error: {str(e)}")

def handle_single_frame(event, context):
    """
    Handle single frame analysis (backward compatibility)
    """
    try:
        # Parse single frame event
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        image_base64 = body.get('image_base64')
        if not image_base64:
            return create_error_response("No image data provided")
        
        # Decode image
        image_bytes = base64.b64decode(image_base64)
        user_id = body.get('user_id', 'unknown')
        keypoints_detected = body.get('keypoints_detected', 0)
        
        # Use video analyzer for single frame
        analyzer = VideoStrokeAnalyzer(frame_buffer_size=1)
        frame_result = analyzer.add_frame(image_bytes)
        
        if 'error' in frame_result:
            return create_error_response(f"Frame analysis failed: {frame_result['error']}")
        
        # Generate response
        response = generate_clinical_response_single(frame_result, user_id, keypoints_detected)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Error in single frame analysis: {e}")
        return create_error_response(f"Single frame analysis error: {str(e)}")

def generate_clinical_response_video(assessment: Dict, user_id: str, keypoints_detected: int, test_duration: float) -> Dict:
    """
    Generate clinical response for video analysis
    """
    nihss_score = assessment.get('nihss_motor_score', 0)
    severity = assessment.get('severity', 'normal')
    interpretation = assessment.get('clinical_interpretation', 'No assessment available')
    
    # Determine drift detection based on NIHSS score
    drift_detected = nihss_score > 0
    
    # Calculate clinical score and message
    if nihss_score == 0:
        clinical_score = 0
        message = "✅ Normal Results - No drift detected over test duration"
        drift_severity = "none"
    elif nihss_score == 1:
        clinical_score = 1
        message = "⚠️ Mild Drift Detected - Arms showed slight movement"
        drift_severity = "mild"
    elif nihss_score == 2:
        clinical_score = 2
        message = "🔶 Moderate Drift Detected - Arms showed noticeable movement"
        drift_severity = "moderate"
    elif nihss_score == 3:
        clinical_score = 3
        message = "🚨 Severe Drift Detected - Significant arm movement or falling"
        drift_severity = "severe"
    else:  # nihss_score == 4
        clinical_score = 4
        message = "🚨 CRITICAL - No movement detected or complete paralysis"
        drift_severity = "critical"
    
    return {
        'drift_detected': drift_detected,
        'pronation_detected': False,  # TODO: Implement pronation detection
        'y_difference': assessment.get('mean_asymmetry', 0),
        'clinical_score': clinical_score,
        'test_quality': 'video_analysis',
        'severity': severity,
        'message': message,
        'nihss_motor_score': nihss_score,
        'nihss_total': nihss_score,
        'drift_severity': drift_severity,
        'research_based': True,
        'clinical_standards': 'NIHSS_Motor_Arm_Item5',
        'analysis_method': 'temporal_video_analysis',
        'test_duration': test_duration,
        'frames_analyzed': assessment.get('total_frames_analyzed', 0),
        'drift_trend': assessment.get('drift_trend', 0),
        'drift_velocity': assessment.get('drift_velocity', 0),
        'clinical_interpretation': interpretation
    }

def generate_clinical_response_single(frame_result: Dict, user_id: str, keypoints_detected: int) -> Dict:
    """
    Generate clinical response for single frame analysis
    """
    asymmetry_score = frame_result.get('asymmetry_score', 0)
    
    # Calculate NIHSS score based on asymmetry
    if asymmetry_score < NIHSS_0_NORMAL:
        nihss_score = 0
        severity = "normal"
        drift_severity = "none"
        message = "No drift detected in current frame"
    elif asymmetry_score < NIHSS_1_MILD:
        nihss_score = 1
        severity = "mild"
        drift_severity = "mild"
        message = "Mild drift detected in current frame"
    elif asymmetry_score < NIHSS_2_MODERATE:
        nihss_score = 2
        severity = "moderate"
        drift_severity = "moderate"
        message = "Moderate drift detected in current frame"
    elif asymmetry_score < NIHSS_3_SEVERE:
        nihss_score = 3
        severity = "severe"
        drift_severity = "severe"
        message = "Severe drift detected in current frame"
    else:
        nihss_score = 4
        severity = "critical"
        drift_severity = "critical"
        message = "Critical drift or no movement detected"
    
    drift_detected = nihss_score > 0
    
    return {
        'drift_detected': drift_detected,
        'pronation_detected': False,
        'y_difference': asymmetry_score,
        'clinical_score': nihss_score,
        'test_quality': 'single_frame_analysis',
        'severity': severity,
        'message': message,
        'nihss_motor_score': nihss_score,
        'nihss_total': nihss_score,
        'drift_severity': drift_severity,
        'research_based': True,
        'clinical_standards': 'NIHSS_Motor_Arm_Item5',
        'analysis_method': 'single_frame',
        'frame_quality': frame_result.get('frame_quality', {}),
        'arm_regions_detected': frame_result.get('arm_regions_detected', 0)
    }

def create_error_response(error_message: str) -> Dict:
    """
    Create standardized error response
    """
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': error_message,
            'drift_detected': False,
            'clinical_score': 0,
            'severity': 'error'
        })
    }

# Example usage for testing
if __name__ == "__main__":
    # Test single frame
    test_event_single = {
        'image_base64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
        'user_id': 'test_user',
        'keypoints_detected': 8
    }
    
    # Test video frames
    test_event_video = {
        'frames': [
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
        ],
        'user_id': 'test_user',
        'keypoints_detected': 8,
        'test_duration': 20.0
    }
    
    print("Enhanced Lambda function for video analysis")
    print("Supports both single frame and multi-frame video analysis")
