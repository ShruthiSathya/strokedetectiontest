#!/usr/bin/env python3
"""
Deploy Fixed Lambda Function
Deploy the corrected keypoint analysis Lambda function
"""

import boto3
import json
import zipfile
import io

def deploy_fixed_lambda():
    """Deploy the fixed Lambda function"""
    
    print("🚀 Deploying Fixed Lambda Function")
    print("=" * 50)
    print("Deploying the corrected keypoint analysis function")
    print()
    
    try:
        # Read the fixed Lambda function code
        with open('lambda_fast_enhanced.py', 'r') as f:
            lambda_code = f.read()
        
        print("📄 Lambda code loaded successfully")
        print(f"   Code length: {len(lambda_code)} characters")
        
        # Create a zip file with the Lambda function
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        print(f"📦 Zip file created: {len(zip_data)} bytes")
        
        # Deploy to AWS Lambda
        lambda_client = boto3.client('lambda')
        
        print("🔧 Updating Lambda function...")
        response = lambda_client.update_function_code(
            FunctionName='strokedetectionapp',
            ZipFile=zip_data
        )
        
        print("✅ Lambda function updated successfully!")
        print(f"   Function ARN: {response['FunctionArn']}")
        print(f"   Last Modified: {response['LastModified']}")
        print(f"   Code Size: {response['CodeSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = deploy_fixed_lambda()
    
    if success:
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("✅ Fixed Lambda function is now deployed")
        print("✅ The keypoint analysis bug has been fixed")
        print()
        print("🧪 Test the fix with: python3 test_fixed_lambda.py")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("🔧 Check your AWS credentials and Lambda function name")
