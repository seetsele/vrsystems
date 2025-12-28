"""
Verity Systems - AWS Mock Server for Development
Uses moto to mock AWS services when Docker/LocalStack isn't available

This allows development without:
- Docker installed
- LocalStack running
- Real AWS credentials
"""

import os
import sys
import json
import logging
import threading
from typing import Optional

logger = logging.getLogger('VerityAWSMock')

# Check if we should use mocks
USE_MOCKS = os.getenv('USE_AWS_MOCKS', 'true').lower() == 'true'
USE_LOCALSTACK = os.getenv('USE_LOCALSTACK', 'false').lower() == 'true'

_mock_servers_started = False
_moto_server = None


def start_mock_aws_services():
    """Start moto mock AWS services in a background thread"""
    global _mock_servers_started, _moto_server
    
    if _mock_servers_started:
        return True
    
    if not USE_MOCKS:
        logger.info("AWS mocks disabled - using real AWS or LocalStack")
        return False
    
    try:
        from moto import mock_aws
        
        # Start all AWS mocks
        _moto_server = mock_aws()
        _moto_server.start()
        
        _mock_servers_started = True
        logger.info("✅ Moto AWS mock services started")
        
        # Initialize resources
        _initialize_mock_resources()
        
        return True
        
    except ImportError:
        logger.warning("Moto not installed. Run: pip install moto")
        return False
    except Exception as e:
        logger.error(f"Failed to start mock AWS services: {e}")
        return False


def stop_mock_aws_services():
    """Stop moto mock AWS services"""
    global _mock_servers_started, _moto_server
    
    if _moto_server:
        _moto_server.stop()
        _mock_servers_started = False
        logger.info("✅ Moto AWS mock services stopped")


def _initialize_mock_resources():
    """Initialize mock AWS resources (buckets, tables, queues)"""
    import boto3
    
    # Use default region
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    # Create S3 buckets
    s3 = boto3.client('s3', region_name=region)
    buckets = [
        'verity-verification-results',
        'verity-reports',
        'verity-exports',
        'verity-backups'
    ]
    
    for bucket in buckets:
        try:
            s3.create_bucket(Bucket=bucket)
            logger.debug(f"Created mock S3 bucket: {bucket}")
        except Exception as e:
            logger.debug(f"Bucket {bucket} might already exist: {e}")
    
    # Create DynamoDB tables
    dynamodb = boto3.client('dynamodb', region_name=region)
    
    tables = [
        {
            'TableName': 'verity-claim-cache',
            'KeySchema': [{'AttributeName': 'claim_hash', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'claim_hash', 'AttributeType': 'S'}],
        },
        {
            'TableName': 'verity-user-sessions',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'session_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'session_id', 'AttributeType': 'S'}
            ],
        },
        {
            'TableName': 'verity-verification-history',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
        }
    ]
    
    for table_config in tables:
        try:
            dynamodb.create_table(
                **table_config,
                BillingMode='PAY_PER_REQUEST'
            )
            logger.debug(f"Created mock DynamoDB table: {table_config['TableName']}")
        except Exception as e:
            logger.debug(f"Table might already exist: {e}")
    
    # Create SQS queues
    sqs = boto3.client('sqs', region_name=region)
    
    queues = [
        'verity-verification-queue',
        'verity-verification-dlq',
        'verity-batch-queue',
        'verity-priority-queue'
    ]
    
    for queue in queues:
        try:
            sqs.create_queue(QueueName=queue)
            logger.debug(f"Created mock SQS queue: {queue}")
        except Exception as e:
            logger.debug(f"Queue might already exist: {e}")
    
    logger.info("✅ Mock AWS resources initialized (S3, DynamoDB, SQS)")


def get_aws_config():
    """Get AWS configuration for boto3 clients"""
    if USE_LOCALSTACK:
        return {
            'endpoint_url': os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566'),
            'aws_access_key_id': 'test',
            'aws_secret_access_key': 'test',
            'region_name': os.getenv('AWS_REGION', 'us-east-1')
        }
    elif USE_MOCKS:
        # Moto mocks work with default config
        return {
            'region_name': os.getenv('AWS_REGION', 'us-east-1')
        }
    else:
        # Real AWS - use environment credentials
        return {
            'region_name': os.getenv('AWS_REGION', 'us-east-1')
        }


# Context manager for testing
class MockAWSContext:
    """Context manager for temporary AWS mocking"""
    
    def __enter__(self):
        start_mock_aws_services()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        stop_mock_aws_services()
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing AWS Mock Server...")
    print(f"USE_MOCKS: {USE_MOCKS}")
    print(f"USE_LOCALSTACK: {USE_LOCALSTACK}")
    
    # Start mocks
    success = start_mock_aws_services()
    
    if success:
        import boto3
        
        # Test S3
        s3 = boto3.client('s3', **get_aws_config())
        buckets = s3.list_buckets()
        print(f"\n📦 S3 Buckets: {[b['Name'] for b in buckets['Buckets']]}")
        
        # Test DynamoDB
        dynamodb = boto3.client('dynamodb', **get_aws_config())
        tables = dynamodb.list_tables()
        print(f"📊 DynamoDB Tables: {tables['TableNames']}")
        
        # Test SQS
        sqs = boto3.client('sqs', **get_aws_config())
        queues = sqs.list_queues()
        queue_urls = queues.get('QueueUrls', [])
        print(f"📬 SQS Queues: {[q.split('/')[-1] for q in queue_urls]}")
        
        print("\n✅ All mock AWS services working!")
        
        # Stop mocks
        stop_mock_aws_services()
    else:
        print("❌ Failed to start mock services")
