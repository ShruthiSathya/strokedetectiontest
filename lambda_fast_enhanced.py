#!/usr/bin/env python3
"""
Fast Enhanced Lambda Function - Corrected and Optimized for Keypoint Analysis
Based on PMC3859007 - Facilitating Stroke Management using Modern Information Technology
This version calculates drift based on skeletal keypoints for clinical accuracy.
"""

import json
import base64
import logging
import time
from typing import Dict

# No boto3/rekognition needed for this logic
# import boto3 

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- CLINICALLY CALIBRATED THRESHOLDS (REAL-WORLD ADJUSTED) ---
# Adjusted for natural human body asymmetry and Vision framework detection accuracy
# These thresholds account for normal variations in arm positioning
NIHSS_0_NORMAL = 0.15           # <15% drift - Normal arm position (no stroke)
NIHSS_1_MILD = 0.25             # 15-25% drift - Mild drift (NIHSS Score 1)
NIHSS_2_MODERATE = 0.40         # 25-40% drift - Moderate drift (NIHSS Score 2)
NIHSS_3_SEVERE = 0.60           # 40-60% drift - Severe drift (NIHSS Score 3)
NIHSS_4_PARALYSIS = 0.80        # >60% drift - Critical/Paralysis (NIHSS Score 4)

def analyze_drift_from_keypoints(keypoints: Dict) -> Dict:
    """
    Calculates a clinically relevant drift score based on keypoint coordinates.
    Returns a normalized asymmetry score representing drift as a fraction of arm length.
    """
    start_time = time.time()
    try:
        # Extract Y-coordinates (vertical position) from the input
        left_wrist_y = keypoints['left_wrist']['y']
        right_wrist_y = keypoints['right_wrist']['y']
        left_shoulder_y = keypoints['left_shoulder']['y']
        right_shoulder_y = keypoints['right_shoulder']['y']

        # 1. Calculate the raw vertical drift in pixels
        vertical_drift_pixels = abs(left_wrist_y - right_wrist_y)

        # 2. Normalize the drift by the average arm length to make it scale-invariant
        left_arm_length = abs(left_wrist_y - left_shoulder_y)
        right_arm_length = abs(right_wrist_y - right_shoulder_y)
        avg_arm_length = (left_arm_length + right_arm_length) / 2

        # Debug logging
        print(f"🔍 Keypoint Analysis Debug:")
        print(f"   Left wrist Y: {left_wrist_y}")
        print(f"   Right wrist Y: {right_wrist_y}")
        print(f"   Vertical drift: {vertical_drift_pixels:.4f}")
        print(f"   Left arm length: {left_arm_length:.4f}")
        print(f"   Right arm length: {right_arm_length:.4f}")
        print(f"   Avg arm length: {avg_arm_length:.4f}")
        
        # Avoid division by zero if keypoints are overlapping
        if avg_arm_length < 0.01:  # Use small threshold for normalized coordinates
            print(f"   ⚠️ Avg arm length too small: {avg_arm_length:.4f}")
            asymmetry_score = 0.0
        else:
            # The final score is the drift as a fraction of the average arm length.
            # e.g., a score of 0.1 means one arm drifted down by 10% of its length.
            asymmetry_score = vertical_drift_pixels / avg_arm_length
            print(f"   ✅ Calculated asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
            
        analysis_time = time.time() - start_time
        
        return {
            'asymmetry_score': asymmetry_score,
            'analysis_time': analysis_time,
            'error': None
        }

    except (KeyError, TypeError) as e:
        logger.error(f"Keypoint analysis failed due to missing key: {e}")
        return {
            'asymmetry_score': 0.0,
            'analysis_time': time.time() - start_time,
            'error': f"Missing keypoints: {str(e)}"
        }


def calculate_fast_nihss_score(asymmetry_score: float, keypoints_detected: int) -> Dict:
    """
    Calculates an NIHSS motor score based on the normalized keypoint drift.
    """
    # Base NIHSS score on the clinically relevant asymmetry score
    if asymmetry_score < NIHSS_0_NORMAL:
        base_score = 0
        severity = "normal"
        message = "✅ Normal Results - No significant arm drift detected."
    elif asymmetry_score < NIHSS_1_MILD:
        base_score = 1
        severity = "mild"
        message = "⚠️ Mild Drift Detected - Slight downward movement of one arm observed."
    elif asymmetry_score < NIHSS_2_MODERATE:
        base_score = 2
        severity = "moderate"
        message = "🔶 Moderate Drift Detected - Noticeable downward movement of one arm."
    elif asymmetry_score < NIHSS_3_SEVERE:
        base_score = 3
        severity = "severe"
        message = "🚨 Severe Drift Detected - Significant downward movement of one arm."
    else:
        base_score = 4
        severity = "critical"
        message = "🚨 CRITICAL - Extreme drift detected, arm may have hit bed or lap."

    # Adjustments based on the quality of keypoint detection
    if keypoints_detected < 4:
        test_quality = "poor_calibration_analysis"
    elif keypoints_detected < 8:
        test_quality = "good_calibration_analysis"
    else:
        test_quality = "excellent_calibration_analysis"
    
    return {
        'nihss_motor_score': base_score,
        'severity': severity,
        'message': message,
        'test_quality': test_quality,
        'drift_detected': base_score > 0
    }

def create_error_response(error_message: str) -> Dict:
    """Creates a standardized HTTP 500 error response."""
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': error_message,
            'drift_detected': False,
            'nihss_motor_score': 0,
            'severity': 'error'
        })
    }


def lambda_handler(event, context):
    """
    Lambda handler that processes skeletal keypoints to detect stroke-related arm drift.
    """
    try:
        start_time = time.time()
        
        # Parse the incoming request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # --- EXPECTS KEYPOINTS DICTIONARY IN THE BODY ---
        # Example: { "keypoints": { "left_wrist": {"y": 255, "x": 150}, ... } }
        keypoints = body.get('keypoints', {})
        user_id = body.get('user_id', 'unknown')

        if not keypoints:
            return create_error_response("Request body must contain a 'keypoints' object.")
        
        # Perform the drift analysis using the new, correct function
        analysis_result = analyze_drift_from_keypoints(keypoints)
        if analysis_result['error']:
            return create_error_response(analysis_result['error'])
            
        asymmetry_score = analysis_result['asymmetry_score']
        keypoints_detected = len(keypoints)
        
        print(f"📊 Processing for user {user_id} with {keypoints_detected} keypoints.")
        print(f"🔧 Using REAL-WORLD ADJUSTED thresholds: Normal<15%, Mild<25%, Moderate<40%, Severe<60%")
        print(f"⚡ Analysis completed in {analysis_result['analysis_time']:.4f}s")
        print(f"📈 Normalized Asymmetry Score: {asymmetry_score:.4f}")

        # Calculate NIHSS score based on the meaningful asymmetry value
        nihss_result = calculate_fast_nihss_score(asymmetry_score, keypoints_detected)

        # Assemble the final response
        response_body = {
            'drift_detected': nihss_result['drift_detected'],
            'asymmetry_score': asymmetry_score,
            'nihss_motor_score': nihss_result['nihss_motor_score'],
            'severity': nihss_result['severity'],
            'message': nihss_result['message'],
            'test_quality': nihss_result['test_quality'],
            'research_based': True,
            'clinical_standards': 'NIHSS_Motor_Arm_Item5',
            'analysis_method': 'normalized_keypoint_drift_v3',
            'analysis_time_seconds': analysis_result['analysis_time'],
            'total_runtime_seconds': time.time() - start_time,
            'version': 'real_world_adjusted_thresholds_v4'
        }
        
        print(f"🎯 NIHSS Score: {nihss_result['nihss_motor_score']}/4")
        print(f"✅ Total processing time: {response_body['total_runtime_seconds']:.4f}s")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }

    except json.JSONDecodeError:
        logger.error("Error: Invalid JSON in request body.")
        return create_error_response("Invalid JSON format in request body.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in lambda_handler: {e}", exc_info=True)
        return create_error_response(f"An unexpected server error occurred: {str(e)}")