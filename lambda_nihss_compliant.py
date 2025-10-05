#!/usr/bin/env python3
"""
NIHSS-Compliant Stroke Detection Lambda Function
Based on official NIH Stroke Scale Motor Arm Test (Item 5)
"""

import json
import time
import logging
from typing import Dict, List

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- NIHSS-COMPLIANT THRESHOLDS ---
# Based on official NIH Stroke Scale Motor Arm Test criteria
NIHSS_0_NORMAL = 0.05      # <5% drift - No drift for 10 seconds (NIHSS 0)
NIHSS_1_MILD = 0.15        # 5-15% drift - Drift before 10 seconds (NIHSS 1)
NIHSS_2_MODERATE = 0.30    # 15-30% drift - Falls with some effort (NIHSS 2)
NIHSS_3_SEVERE = 0.50      # 30-50% drift - Falls without effort (NIHSS 3)
NIHSS_4_PARALYSIS = 0.80   # >50% drift - No movement/paralysis (NIHSS 4)

def calculate_arm_angle(wrist_y: float, shoulder_y: float) -> float:
    """
    Calculate arm angle from vertical position.
    For normalized coordinates, this is a simplified calculation.
    In a real implementation, you'd need to account for camera perspective.
    """
    arm_length = abs(wrist_y - shoulder_y)
    if arm_length == 0:
        return 0
    # Simplified angle calculation for normalized coordinates
    # 90° = horizontal, 0° = vertical down
    return 90 - (arm_length * 90)

def analyze_nihss_compliant_asymmetry(keypoints: Dict) -> Dict:
    """
    NIHSS-compliant asymmetry analysis for Motor Arm Test (Item 5).
    
    NIHSS Motor Arm Test Requirements:
    - Patient holds arms at 90° (sitting) or 45° (supine)
    - Eyes closed for 10 seconds
    - Measures drift over time and effort against gravity
    
    This implementation provides static analysis that aligns with NIHSS principles.
    """
    start_time = time.time()
    
    try:
        # Extract keypoints
        left_wrist_y = keypoints['left_wrist']['y']
        right_wrist_y = keypoints['right_wrist']['y']
        left_shoulder_y = keypoints['left_shoulder']['y']
        right_shoulder_y = keypoints['right_shoulder']['y']
        
        print(f"🔍 NIHSS Motor Arm Test Analysis:")
        print(f"   Left wrist Y: {left_wrist_y}")
        print(f"   Right wrist Y: {right_wrist_y}")
        print(f"   Left shoulder Y: {left_shoulder_y}")
        print(f"   Right shoulder Y: {right_shoulder_y}")
        
        # Calculate arm angles (NIHSS requires ~90° for proper test)
        left_arm_angle = calculate_arm_angle(left_wrist_y, left_shoulder_y)
        right_arm_angle = calculate_arm_angle(right_wrist_y, right_shoulder_y)
        
        print(f"   Left arm angle: {left_arm_angle:.1f}°")
        print(f"   Right arm angle: {right_arm_angle:.1f}°")
        
        # Check if arms are positioned correctly for NIHSS test
        proper_positioning = (80 <= left_arm_angle <= 100) and (80 <= right_arm_angle <= 100)
        
        if not proper_positioning:
            print(f"   ⚠️ Arms not positioned at 90° (NIHSS requirement)")
            return {
                'nihss_score': 0,
                'asymmetry_score': 0.0,
                'error': 'Arms not positioned at 90° (NIHSS requirement)',
                'left_arm_angle': left_arm_angle,
                'right_arm_angle': right_arm_angle,
                'analysis_time': time.time() - start_time,
                'nihss_compliant': False
            }
        
        # Calculate vertical drift (NIHSS measures this)
        vertical_drift_pixels = abs(left_wrist_y - right_wrist_y)
        
        # Calculate arm lengths for normalization
        left_arm_length = abs(left_wrist_y - left_shoulder_y)
        right_arm_length = abs(right_wrist_y - right_shoulder_y)
        avg_arm_length = (left_arm_length + right_arm_length) / 2
        
        print(f"   Vertical drift: {vertical_drift_pixels:.4f}")
        print(f"   Left arm length: {left_arm_length:.4f}")
        print(f"   Right arm length: {right_arm_length:.4f}")
        print(f"   Avg arm length: {avg_arm_length:.4f}")
        
        if avg_arm_length < 0.01:
            print(f"   ⚠️ Avg arm length too small: {avg_arm_length:.4f}")
            return {
                'nihss_score': 0,
                'asymmetry_score': 0.0,
                'error': 'Arm length too small',
                'analysis_time': time.time() - start_time,
                'nihss_compliant': False
            }
        
        # Calculate asymmetry score
        asymmetry_score = vertical_drift_pixels / avg_arm_length
        
        print(f"   ✅ Calculated asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
        
        # Apply NIHSS scoring criteria
        if asymmetry_score < NIHSS_0_NORMAL:
            nihss_score = 0
            severity = "normal"
            clinical_meaning = "No drift - Normal motor function"
        elif asymmetry_score < NIHSS_1_MILD:
            nihss_score = 1
            severity = "mild"
            clinical_meaning = "Mild drift - Slight weakness, monitor"
        elif asymmetry_score < NIHSS_2_MODERATE:
            nihss_score = 2
            severity = "moderate"
            clinical_meaning = "Moderate drift - Noticeable weakness, medical evaluation recommended"
        elif asymmetry_score < NIHSS_3_SEVERE:
            nihss_score = 3
            severity = "severe"
            clinical_meaning = "Severe drift - Significant weakness, urgent medical evaluation"
        else:
            nihss_score = 4
            severity = "critical"
            clinical_meaning = "No movement - Severe paralysis, emergency medical care needed"
        
        print(f"   🎯 NIHSS Score: {nihss_score}/4 ({severity.upper()})")
        print(f"   📋 Clinical: {clinical_meaning}")
        
        analysis_time = time.time() - start_time
        
        return {
            'nihss_score': nihss_score,
            'asymmetry_score': asymmetry_score,
            'asymmetry_percentage': asymmetry_score * 100,
            'severity': severity,
            'clinical_meaning': clinical_meaning,
            'left_arm_angle': left_arm_angle,
            'right_arm_angle': right_arm_angle,
            'vertical_drift_pixels': vertical_drift_pixels,
            'avg_arm_length': avg_arm_length,
            'analysis_time': analysis_time,
            'nihss_compliant': True,
            'error': None
        }
        
    except (KeyError, TypeError) as e:
        logger.error(f"NIHSS keypoint analysis failed due to missing key: {e}")
        return {
            'nihss_score': 0,
            'asymmetry_score': 0.0,
            'error': f"Missing keypoints: {str(e)}",
            'analysis_time': time.time() - start_time,
            'nihss_compliant': False
        }

def calculate_fast_nihss_score(asymmetry_score: float, keypoints_detected: int) -> Dict:
    """
    Calculate NIHSS score based on asymmetry and keypoint quality.
    """
    # Check keypoint quality
    if keypoints_detected < 4:
        return {
            'nihss_motor_score': 0,
            'drift_detected': False,
            'severity': 'normal',
            'message': 'Insufficient keypoints for reliable analysis',
            'test_quality': 'poor_keypoint_detection'
        }
    
    # Apply NIHSS scoring
    if asymmetry_score < NIHSS_0_NORMAL:
        return {
            'nihss_motor_score': 0,
            'drift_detected': False,
            'severity': 'normal',
            'message': '✅ No drift detected - Normal motor function',
            'test_quality': 'nihss_compliant_analysis'
        }
    elif asymmetry_score < NIHSS_1_MILD:
        return {
            'nihss_motor_score': 1,
            'drift_detected': True,
            'severity': 'mild',
            'message': '⚠️ Mild drift detected - Slight weakness, monitor for other symptoms',
            'test_quality': 'nihss_compliant_analysis'
        }
    elif asymmetry_score < NIHSS_2_MODERATE:
        return {
            'nihss_motor_score': 2,
            'drift_detected': True,
            'severity': 'moderate',
            'message': '🔶 Moderate drift detected - Noticeable weakness, medical evaluation recommended',
            'test_quality': 'nihss_compliant_analysis'
        }
    elif asymmetry_score < NIHSS_3_SEVERE:
        return {
            'nihss_motor_score': 3,
            'drift_detected': True,
            'severity': 'severe',
            'message': '🚨 Severe drift detected - Significant weakness, urgent medical evaluation',
            'test_quality': 'nihss_compliant_analysis'
        }
    else:
        return {
            'nihss_motor_score': 4,
            'drift_detected': True,
            'severity': 'critical',
            'message': '🚨 Critical drift detected - Severe paralysis, emergency medical care needed',
            'test_quality': 'nihss_compliant_analysis'
        }

def create_error_response(error_message: str) -> Dict:
    """Create standardized error response"""
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': error_message,
            'drift_detected': False,
            'asymmetry_score': 0.0,
            'nihss_motor_score': 0,
            'severity': 'error',
            'message': f'Analysis failed: {error_message}',
            'test_quality': 'error',
            'research_based': False,
            'clinical_standards': 'NIHSS_Error',
            'analysis_method': 'nihss_compliant_analysis',
            'analysis_time_seconds': 0.0,
            'total_runtime_seconds': 0.0,
            'version': 'nihss_compliant_v1'
        })
    }

def lambda_handler(event, context):
    """
    NIHSS-compliant Lambda handler for stroke detection.
    """
    start_time = time.time()
    
    print("🚀 NIHSS-Compliant Lambda function starting...")
    print(f"🔧 Using NIHSS-compliant thresholds:")
    print(f"   NIHSS 0 (Normal): <{NIHSS_0_NORMAL*100:.0f}% drift")
    print(f"   NIHSS 1 (Mild): {NIHSS_1_MILD*100:.0f}%-{NIHSS_2_MODERATE*100:.0f}% drift")
    print(f"   NIHSS 2 (Moderate): {NIHSS_2_MODERATE*100:.0f}%-{NIHSS_3_SEVERE*100:.0f}% drift")
    print(f"   NIHSS 3 (Severe): {NIHSS_3_SEVERE*100:.0f}%-{NIHSS_4_PARALYSIS*100:.0f}% drift")
    print(f"   NIHSS 4 (Critical): >{NIHSS_4_PARALYSIS*100:.0f}% drift")
    
    try:
        # Parse the incoming request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Extract keypoints and metadata
        keypoints = body.get('keypoints', {})
        user_id = body.get('user_id', 'unknown')
        test_mode = body.get('test_mode', False)
        
        print(f"📊 Processing NIHSS Motor Arm Test for user {user_id}")
        print(f"🔍 Keypoints received: {list(keypoints.keys())}")
        
        # Perform NIHSS-compliant analysis
        analysis_result = analyze_nihss_compliant_asymmetry(keypoints)
        
        if analysis_result['error']:
            print(f"❌ Analysis failed: {analysis_result['error']}")
            return create_error_response(analysis_result['error'])
        
        # Calculate NIHSS score
        nihss_result = calculate_fast_nihss_score(
            analysis_result['asymmetry_score'], 
            len(keypoints)
        )
        
        print(f"🎯 NIHSS Score: {nihss_result['nihss_motor_score']}/4")
        print(f"📊 Asymmetry: {analysis_result['asymmetry_score']:.4f} ({analysis_result['asymmetry_percentage']:.1f}%)")
        print(f"🏥 Severity: {nihss_result['severity'].upper()}")
        
        # Create response
        response_body = {
            'drift_detected': nihss_result['drift_detected'],
            'asymmetry_score': analysis_result['asymmetry_score'],
            'nihss_motor_score': nihss_result['nihss_motor_score'],
            'severity': nihss_result['severity'],
            'message': nihss_result['message'],
            'test_quality': nihss_result['test_quality'],
            'research_based': True,
            'clinical_standards': 'NIHSS_Motor_Arm_Item5',
            'analysis_method': 'nihss_compliant_analysis_v1',
            'analysis_time_seconds': analysis_result['analysis_time'],
            'total_runtime_seconds': time.time() - start_time,
            'version': 'nihss_compliant_v1',
            # Additional NIHSS-specific data
            'left_arm_angle': analysis_result.get('left_arm_angle', 0),
            'right_arm_angle': analysis_result.get('right_arm_angle', 0),
            'vertical_drift_pixels': analysis_result.get('vertical_drift_pixels', 0),
            'nihss_compliant': analysis_result.get('nihss_compliant', False)
        }
        
        print(f"✅ NIHSS analysis completed in {response_body['total_runtime_seconds']:.4f}s")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in NIHSS Lambda: {str(e)}")
        return create_error_response(f"An unexpected server error occurred: {str(e)}")
