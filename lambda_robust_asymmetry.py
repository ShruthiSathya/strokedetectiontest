import json
import math
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# REALISTIC NIHSS Motor Arm Score Thresholds - Adjusted for normal positioning variations
NIHSS_0_NORMAL = 0.20          # <20% - Normal variation
NIHSS_1_MILD = 0.35            # 20-35% - Mild drift
NIHSS_2_MODERATE = 0.50        # 35-50% - Moderate drift  
NIHSS_3_SEVERE = 0.70          # 50-70% - Severe drift
NIHSS_4_PARALYSIS = 0.70       # >70% - Critical

def calculate_nihss_motor_score(y_difference, test_duration=20.0):
    """Calculate NIHSS Motor Arm Score with realistic thresholds."""
    if y_difference > 1.0:
        y_difference = y_difference / 100.0
    
    if y_difference < NIHSS_0_NORMAL:
        return {'nihss_motor_score': 0, 'severity': 'normal', 'clinical_interpretation': 'No significant drift detected. Arms held steady within normal variation range.'}
    elif y_difference < NIHSS_1_MILD:
        return {'nihss_motor_score': 1, 'severity': 'mild', 'clinical_interpretation': 'Mild arm variation detected. Arms show slight positioning differences but remain functional.'}
    elif y_difference < NIHSS_2_MODERATE:
        return {'nihss_motor_score': 2, 'severity': 'moderate', 'clinical_interpretation': 'Moderate arm variation detected. Arms show noticeable positioning differences but maintain some control.'}
    elif y_difference < NIHSS_3_SEVERE:
        return {'nihss_motor_score': 3, 'severity': 'severe', 'clinical_interpretation': 'Severe arm variation detected. Arms show significant positioning differences with limited control.'}
    else:
        return {'nihss_motor_score': 4, 'severity': 'critical', 'clinical_interpretation': 'Critical arm variation detected. Arms show severe positioning differences or inability to maintain position.'}

def assess_keypoint_detection_quality(keypoints):
    """Assess the quality of keypoint detection to choose the best asymmetry calculation method."""
    
    # Extract coordinates
    left_wrist = keypoints.get('left_wrist', {})
    right_wrist = keypoints.get('right_wrist', {})
    left_shoulder = keypoints.get('left_shoulder', {})
    right_shoulder = keypoints.get('right_shoulder', {})
    
    # Check if we have all required keypoints
    required_keypoints = [left_wrist, right_wrist, left_shoulder, right_shoulder]
    if not all(kp.get('x') is not None and kp.get('y') is not None for kp in required_keypoints):
        return {'quality': 'poor', 'reason': 'Missing required keypoints'}
    
    # Calculate arm lengths
    left_arm_length = math.sqrt((left_wrist['x'] - left_shoulder['x'])**2 + 
                               (left_wrist['y'] - left_shoulder['y'])**2)
    right_arm_length = math.sqrt((right_wrist['x'] - right_shoulder['x'])**2 + 
                                (right_wrist['y'] - right_shoulder['y'])**2)
    avg_arm_length = (left_arm_length + right_arm_length) / 2
    
    # Quality indicators
    arm_length_diff = abs(left_arm_length - right_arm_length) / max(left_arm_length, right_arm_length) if max(left_arm_length, right_arm_length) > 0 else 1.0
    small_arm_lengths = avg_arm_length < 0.05
    very_small_arm_lengths = avg_arm_length < 0.02
    
    # Determine quality
    if very_small_arm_lengths or arm_length_diff > 0.8:
        quality = 'very_poor'
        reason = f'Very small arm lengths ({avg_arm_length:.3f}) or large difference ({arm_length_diff:.1%})'
    elif small_arm_lengths or arm_length_diff > 0.5:
        quality = 'poor'
        reason = f'Small arm lengths ({avg_arm_length:.3f}) or significant difference ({arm_length_diff:.1%})'
    elif arm_length_diff > 0.3:
        quality = 'fair'
        reason = f'Moderate arm length difference ({arm_length_diff:.1%})'
    else:
        quality = 'good'
        reason = f'Good arm length consistency ({arm_length_diff:.1%})'
    
    return {
        'quality': quality,
        'reason': reason,
        'arm_length_diff': arm_length_diff,
        'avg_arm_length': avg_arm_length,
        'left_arm_length': left_arm_length,
        'right_arm_length': right_arm_length
    }

def calculate_robust_asymmetry(keypoints):
    """Calculate asymmetry using the most appropriate method based on detection quality."""
    
    # Assess detection quality
    quality_assessment = assess_keypoint_detection_quality(keypoints)
    
    if quality_assessment['quality'] == 'very_poor':
        return {
            'asymmetry_score': 0.0,
            'asymmetry_percent': 0.0,
            'drift_detected': False,
            'method_used': 'fallback',
            'quality_assessment': quality_assessment,
            'error': 'Very poor keypoint detection quality - cannot assess asymmetry'
        }
    
    # Extract coordinates
    left_wrist = keypoints['left_wrist']
    right_wrist = keypoints['right_wrist']
    left_shoulder = keypoints['left_shoulder']
    right_shoulder = keypoints['right_shoulder']
    
    # Calculate vertical drift
    vertical_drift = abs(left_wrist['y'] - right_wrist['y'])
    
    # Choose calculation method based on quality
    if quality_assessment['quality'] in ['poor', 'very_poor']:
        # Use absolute vertical drift for poor detection quality
        asymmetry_score = vertical_drift
        method_used = 'absolute_vertical_drift'
        print(f"DEBUG: Using absolute vertical drift method due to poor detection quality: {quality_assessment['reason']}")
    else:
        # Use normalized method for good detection quality
        left_arm_length = math.sqrt((left_wrist['x'] - left_shoulder['x'])**2 + 
                                   (left_wrist['y'] - left_shoulder['y'])**2)
        right_arm_length = math.sqrt((right_wrist['x'] - right_shoulder['x'])**2 + 
                                    (right_wrist['y'] - right_shoulder['y'])**2)
        avg_arm_length = (left_arm_length + right_arm_length) / 2
        
        if avg_arm_length > 0.01:
            asymmetry_score = vertical_drift / avg_arm_length
        else:
            asymmetry_score = vertical_drift  # Fallback to absolute
        method_used = 'normalized_vertical_drift'
        print(f"DEBUG: Using normalized vertical drift method due to good detection quality")
    
    # Calculate NIHSS score
    nihss_result = calculate_nihss_motor_score(asymmetry_score)
    
    # Determine if drift is detected
    drift_detected = asymmetry_score > 0.05  # 5% threshold for drift detection
    
    return {
        'asymmetry_score': asymmetry_score,
        'asymmetry_percent': asymmetry_score * 100,
        'drift_detected': drift_detected,
        'method_used': method_used,
        'quality_assessment': quality_assessment,
        'vertical_drift': vertical_drift,
        'nihss_motor_score': nihss_result['nihss_motor_score'],
        'nihss_total': nihss_result['nihss_motor_score'],
        'severity': nihss_result['severity'],
        'clinical_interpretation': nihss_result['clinical_interpretation'],
        'error': None
    }

def lambda_handler(event, context):
    try:
        # Debug: Log the incoming event structure
        print(f"DEBUG: Event received: {json.dumps(event, indent=2)}")
        
        # Handle different event formats
        body = None
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        # Extract keypoint data from iOS app
        keypoints = body.get('keypoints', {})
        user_id = body.get('user_id', 'unknown')
        test_mode = body.get('test_mode', False)
        force_drift = body.get('force_drift', False)
        user_intentionally_drifting = body.get('user_intentionally_drifting', False)
        
        print(f"DEBUG: User ID: {user_id}")
        print(f"DEBUG: Test mode: {test_mode}, Force drift: {force_drift}")
        print(f"DEBUG: User intentionally drifting: {user_intentionally_drifting}")
        print(f"DEBUG: Keypoints received: {list(keypoints.keys())}")
        
        # Analyze keypoint asymmetry with robust method
        analysis_result = calculate_robust_asymmetry(keypoints)
        
        if analysis_result.get('error'):
            print(f"DEBUG: Analysis error: {analysis_result['error']}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': analysis_result['error'],
                    'drift_detected': False,
                    'asymmetry_score': 0.0,
                    'nihss_motor_score': 0
                })
            }
        
        # Handle test modes
        if force_drift:
            analysis_result['drift_detected'] = True
            analysis_result['asymmetry_score'] = 0.08  # Force significant drift
            analysis_result['nihss_motor_score'] = 3
            analysis_result['severity'] = 'severe'
            analysis_result['clinical_interpretation'] = 'FORCED DRIFT for testing purposes'
            print(f"DEBUG: FORCED DRIFT for testing")
        
        # Return comprehensive clinical assessment
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'drift_detected': analysis_result['drift_detected'],
                'asymmetry_score': analysis_result['asymmetry_score'],
                'asymmetry_percent': analysis_result['asymmetry_percent'],
                'y_difference': analysis_result['asymmetry_score'],  # Legacy field
                'clinical_score': analysis_result['nihss_motor_score'],  # Legacy field
                'nihss_motor_score': analysis_result['nihss_motor_score'],
                'nihss_total': analysis_result['nihss_total'],
                'severity': analysis_result['severity'],
                'message': analysis_result['clinical_interpretation'],
                'clinical_interpretation': analysis_result['clinical_interpretation'],
                'test_quality': 'robust_keypoint_analysis',
                'research_based': True,
                'clinical_standards': 'NIHSS_Motor_Arm_Item5_Robust',
                'analysis_method': analysis_result['method_used'],
                'detection_quality': analysis_result['quality_assessment']['quality'],
                'quality_reason': analysis_result['quality_assessment']['reason'],
                'vertical_drift': analysis_result['vertical_drift']
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'drift_detected': False,
                'asymmetry_score': 0.0,
                'nihss_motor_score': 0
            })
        }
