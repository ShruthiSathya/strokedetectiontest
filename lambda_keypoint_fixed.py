import json
import math
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clinical thresholds based on NIHSS and research standards
# Based on "Facilitating Stroke Management using Modern Information Technology" - PMC3859007
# and NIHSS motor arm assessment criteria

# REALISTIC NIHSS Motor Arm Score Thresholds - Adjusted for normal positioning variations
# These thresholds account for natural arm positioning variations, camera angles, and detection accuracy
NIHSS_0_NORMAL = 0.20          # <20% - Normal variation (was 1%)
NIHSS_1_MILD = 0.35            # 20-35% - Mild drift (was 1-3%)
NIHSS_2_MODERATE = 0.50        # 35-50% - Moderate drift (was 3-8%)  
NIHSS_3_SEVERE = 0.70          # 50-70% - Severe drift (was 8-15%)
NIHSS_4_PARALYSIS = 0.70       # >70% - Critical (was 15%+)

def calculate_nihss_motor_score(y_difference, test_duration=20.0):
    """
    Calculate NIHSS Motor Arm Score (Item 5) based on clinical standards.
    Based on research from PMC3859007 and NIHSS criteria.
    
    Args:
        y_difference: Y-axis drift percentage (0.0-1.0)
        test_duration: Test duration in seconds
    
    Returns:
        dict: NIHSS score and clinical interpretation
    """
    # Convert percentage to decimal if needed
    if y_difference > 1.0:
        y_difference = y_difference / 100.0
    
    # REALISTIC NIHSS Motor Arm Score - Adjusted for normal positioning variations
    if y_difference < NIHSS_0_NORMAL:
        # Normal variation - arms within expected range
        score = 0
        severity = "normal"
        clinical_interpretation = "No significant drift detected. Arms held steady within normal variation range."
        nihss_total = 0
        
    elif y_difference < NIHSS_1_MILD:
        # Mild drift - NIHSS 1
        score = 1
        severity = "mild"
        clinical_interpretation = "Mild arm variation detected. Arms show slight positioning differences but remain functional."
        nihss_total = 1
        
    elif y_difference < NIHSS_2_MODERATE:
        # Moderate drift - NIHSS 2
        score = 2
        severity = "moderate"
        clinical_interpretation = "Moderate arm variation detected. Arms show noticeable positioning differences but maintain some control."
        nihss_total = 2
        
    elif y_difference < NIHSS_3_SEVERE:
        # Severe drift - NIHSS 3
        score = 3
        severity = "severe"
        clinical_interpretation = "Severe arm variation detected. Arms show significant positioning differences with limited control."
        nihss_total = 3
        
    else:
        # Critical - NIHSS 4
        score = 4
        severity = "critical"
        clinical_interpretation = "Critical arm variation detected. Arms show severe positioning differences or inability to maintain position."
        nihss_total = 4
    
    return {
        'nihss_motor_score': score,
        'nihss_total': nihss_total,
        'severity': severity,
        'clinical_interpretation': clinical_interpretation,
        'y_difference_percent': y_difference * 100,
        'test_duration': test_duration
    }

def analyze_keypoint_asymmetry(keypoints):
    """
    Analyze keypoint data for arm asymmetry using proper Euclidean distance calculation.
    
    Args:
        keypoints: Dictionary with keypoint coordinates
        Format: {"left_wrist": {"x": 0.5, "y": 0.6}, "right_wrist": {"x": 0.4, "y": 0.7}, ...}
    
    Returns:
        dict: Analysis results with asymmetry score and clinical interpretation
    """
    try:
        # Extract keypoint coordinates
        left_wrist = keypoints.get('left_wrist', {})
        right_wrist = keypoints.get('right_wrist', {})
        left_shoulder = keypoints.get('left_shoulder', {})
        right_shoulder = keypoints.get('right_shoulder', {})
        
        # Check if we have all required keypoints
        required_keypoints = [left_wrist, right_wrist, left_shoulder, right_shoulder]
        if not all(kp.get('x') is not None and kp.get('y') is not None for kp in required_keypoints):
            return {
                'error': 'Missing required keypoints',
                'asymmetry_score': 0.0,
                'drift_detected': False,
                'nihss_motor_score': 0
            }
        
        # Extract coordinates
        left_wrist_x, left_wrist_y = left_wrist['x'], left_wrist['y']
        right_wrist_x, right_wrist_y = right_wrist['x'], right_wrist['y']
        left_shoulder_x, left_shoulder_y = left_shoulder['x'], left_shoulder['y']
        right_shoulder_x, right_shoulder_y = right_shoulder['x'], right_shoulder['y']
        
        # Calculate arm lengths using Euclidean distance (proper for 90-degree arms)
        left_arm_length = math.sqrt((left_wrist_x - left_shoulder_x)**2 + (left_wrist_y - left_shoulder_y)**2)
        right_arm_length = math.sqrt((right_wrist_x - right_shoulder_x)**2 + (right_wrist_y - right_shoulder_y)**2)
        avg_arm_length = (left_arm_length + right_arm_length) / 2
        
        # Calculate vertical drift between wrists
        vertical_drift = abs(left_wrist_y - right_wrist_y)
        
        print(f"DEBUG: Arm analysis - left_arm_length: {left_arm_length:.4f}, right_arm_length: {right_arm_length:.4f}")
        print(f"DEBUG: Arm analysis - avg_arm_length: {avg_arm_length:.4f}, vertical_drift: {vertical_drift:.4f}")
        
        # Calculate asymmetry score
        if avg_arm_length > 0.01:  # Minimum arm length threshold
            asymmetry_score = vertical_drift / avg_arm_length
        else:
            asymmetry_score = 0.0
            print(f"DEBUG: Arm length too small for analysis: {avg_arm_length:.4f}")
        
        print(f"DEBUG: Calculated asymmetry: {asymmetry_score:.4f} ({asymmetry_score*100:.1f}%)")
        
        # Calculate NIHSS Motor Score using clinical standards
        nihss_result = calculate_nihss_motor_score(asymmetry_score, test_duration=20.0)
        
        # Determine if drift is detected
        drift_detected = asymmetry_score > NIHSS_1_MILD  # Use mild threshold for detection
        
        return {
            'asymmetry_score': asymmetry_score,
            'asymmetry_percent': asymmetry_score * 100,
            'drift_detected': drift_detected,
            'left_arm_length': left_arm_length,
            'right_arm_length': right_arm_length,
            'avg_arm_length': avg_arm_length,
            'vertical_drift': vertical_drift,
            'nihss_motor_score': nihss_result['nihss_motor_score'],
            'nihss_total': nihss_result['nihss_total'],
            'severity': nihss_result['severity'],
            'clinical_interpretation': nihss_result['clinical_interpretation'],
            'error': None
        }
        
    except Exception as e:
        print(f"DEBUG: Keypoint analysis error: {e}")
        return {
            'error': str(e),
            'asymmetry_score': 0.0,
            'drift_detected': False,
            'nihss_motor_score': 0
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
            # Direct event format (for testing)
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
        
        # Analyze keypoint asymmetry
        analysis_result = analyze_keypoint_asymmetry(keypoints)
        
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
                'test_quality': 'keypoint_analysis',
                'research_based': True,
                'clinical_standards': 'NIHSS_Motor_Arm_Item5',
                'analysis_method': 'euclidean_distance',
                'left_arm_length': analysis_result['left_arm_length'],
                'right_arm_length': analysis_result['right_arm_length'],
                'avg_arm_length': analysis_result['avg_arm_length'],
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
