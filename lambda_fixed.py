import json
import base64
import logging
import boto3

# Initialize the Rekognition client (keeping for future use)
rekognition_client = boto3.client('rekognition')
# Initialize DynamoDB client for logging (Optional - needed for Stage 3)
dynamodb_client = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set a threshold for drift detection (Y-axis difference in normalized coordinates)
# 0.05 means 5% of the screen height difference is considered drift.
DRIFT_THRESHOLD = 0.05 
# You will need to fine-tune this value.

def lambda_handler(event, context):
    try:
        # 1. Extract the keypoint data from the API Gateway event payload
        # The iOS app sends: {"left_arm_y": {"value": 0.5}, "right_arm_y": {"value": 0.6}, "user_id": "123"}
        body = json.loads(event['body'])
        
        # 2. Extract the Y-coordinates from the iOS Vision Framework analysis
        left_arm_y = body.get('left_arm_y', {}).get('value', 0.0)
        right_arm_y = body.get('right_arm_y', {}).get('value', 0.0)
        user_id = body.get('user_id', 'unknown')
        
        # 3. Calculate the drift using the pre-processed keypoints from iOS
        y_difference = abs(left_arm_y - right_arm_y)
        drift_detected = y_difference > DRIFT_THRESHOLD
        
        logger.info(f"User {user_id}: left_arm_y={left_arm_y}, right_arm_y={right_arm_y}, y_diff={y_difference}, drift={drift_detected}")
        
        # 4. (Optional - Stage 3) Log the result to DynamoDB
        # table = dynamodb_client.Table('StrokeTestLogs')
        # table.put_item(Item={
        #     'user_id': user_id, 
        #     'timestamp': str(context.get_remaining_time_in_millis()), 
        #     'drift_detected': drift_detected, 
        #     'y_diff': y_difference,
        #     'left_arm_y': left_arm_y,
        #     'right_arm_y': right_arm_y
        # })
        
        # 5. Return the result to the mobile app
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # Required for API Gateway CORS
            },
            'body': json.dumps({
                'drift_detected': drift_detected,
                'y_difference': y_difference,
                'left_arm_y': left_arm_y,
                'right_arm_y': right_arm_y,
                'message': "Drift detected!" if drift_detected else "No drift detected."
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
            'body': json.dumps({'error': str(e), 'drift_detected': False})
        }

# This version works with your current iOS app that sends keypoint data from Vision Framework
# For true Rekognition integration, see the alternative version below
