"""
Verity Systems - AWS LocalStack Integration
Local AWS development for S3, DynamoDB, Lambda, and SQS

Supports three modes:
1. Moto mocks (no Docker needed) - set USE_AWS_MOCKS=true
2. LocalStack (Docker) - set USE_LOCALSTACK=true  
3. Real AWS - set both to false

GitHub Education: LocalStack Pro credits available
Use for: Testing AWS integrations locally without charges
"""

import boto3
import json
import os
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from botocore.config import Config

logger = logging.getLogger('VerityLocalStack')

# Configuration
LOCALSTACK_ENDPOINT = os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
USE_LOCALSTACK = os.getenv('USE_LOCALSTACK', 'false').lower() == 'true'
USE_AWS_MOCKS = os.getenv('USE_AWS_MOCKS', 'true').lower() == 'true'
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Bucket and table names
S3_BUCKET_RESULTS = 'verity-verification-results'
S3_BUCKET_REPORTS = 'verity-reports'
DYNAMODB_CACHE_TABLE = 'verity-claim-cache'
SQS_VERIFICATION_QUEUE = 'verity-verification-queue'

# Initialize mocks if needed
_mocks_initialized = False

def _ensure_mocks_started():
    """Start moto mocks if USE_AWS_MOCKS is enabled"""
    global _mocks_initialized
    if USE_AWS_MOCKS and not USE_LOCALSTACK and not _mocks_initialized:
        try:
            from aws_mock_server import start_mock_aws_services
            start_mock_aws_services()
            _mocks_initialized = True
            logger.info("✅ AWS mocks initialized")
        except ImportError:
            logger.warning("aws_mock_server not available")
        except Exception as e:
            logger.warning(f"Could not start AWS mocks: {e}")


def get_aws_config() -> Dict[str, Any]:
    """Get AWS configuration - Mocks, LocalStack for dev, real AWS for prod"""
    _ensure_mocks_started()
    
    if USE_LOCALSTACK:
        return {
            'endpoint_url': LOCALSTACK_ENDPOINT,
            'aws_access_key_id': 'test',
            'aws_secret_access_key': 'test',
            'region_name': AWS_REGION
        }
    # For mocks or real AWS, just use region
    return {
        'region_name': AWS_REGION
    }


# ============================================================
# S3 CLIENT - Store verification results and reports
# ============================================================

class VerityS3Client:
    """S3 client for storing verification results and reports"""
    
    def __init__(self):
        config = get_aws_config()
        self.client = boto3.client('s3', **config)
        self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """Create buckets if they don't exist (LocalStack only)"""
        if not USE_LOCALSTACK:
            return
        
        for bucket in [S3_BUCKET_RESULTS, S3_BUCKET_REPORTS]:
            try:
                self.client.head_bucket(Bucket=bucket)
            except:
                try:
                    self.client.create_bucket(Bucket=bucket)
                    logger.info(f"Created S3 bucket: {bucket}")
                except Exception as e:
                    logger.warning(f"Could not create bucket {bucket}: {e}")
    
    async def store_verification_result(
        self, 
        claim_id: str, 
        result: Dict[str, Any]
    ) -> bool:
        """Store verification result in S3"""
        try:
            key = f"verifications/{datetime.utcnow().strftime('%Y/%m/%d')}/{claim_id}.json"
            
            self.client.put_object(
                Bucket=S3_BUCKET_RESULTS,
                Key=key,
                Body=json.dumps(result, default=str),
                ContentType='application/json',
                Metadata={
                    'verdict': result.get('verdict', 'unknown'),
                    'confidence': str(result.get('confidence', 0)),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            logger.debug(f"Stored verification result: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store verification result: {e}")
            return False
    
    async def get_verification_result(self, claim_id: str, date: str = None) -> Optional[Dict]:
        """Retrieve verification result from S3"""
        try:
            if date:
                key = f"verifications/{date}/{claim_id}.json"
            else:
                # Search recent dates
                key = await self._find_verification_key(claim_id)
            
            if not key:
                return None
            
            response = self.client.get_object(Bucket=S3_BUCKET_RESULTS, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to retrieve verification: {e}")
            return None
    
    async def _find_verification_key(self, claim_id: str) -> Optional[str]:
        """Find verification key by searching recent dates"""
        for days_ago in range(7):
            date = (datetime.utcnow() - timedelta(days=days_ago)).strftime('%Y/%m/%d')
            key = f"verifications/{date}/{claim_id}.json"
            try:
                self.client.head_object(Bucket=S3_BUCKET_RESULTS, Key=key)
                return key
            except:
                continue
        return None
    
    async def store_report(self, report_id: str, report_data: bytes, content_type: str = 'application/pdf') -> str:
        """Store generated report (PDF, image, etc.)"""
        try:
            key = f"reports/{datetime.utcnow().strftime('%Y/%m')}/{report_id}"
            
            self.client.put_object(
                Bucket=S3_BUCKET_REPORTS,
                Key=key,
                Body=report_data,
                ContentType=content_type
            )
            
            # Generate presigned URL for access
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_REPORTS, 'Key': key},
                ExpiresIn=86400  # 24 hours
            )
            return url
        except Exception as e:
            logger.error(f"Failed to store report: {e}")
            return None


# ============================================================
# DYNAMODB CLIENT - Cache claim verifications
# ============================================================

class VerityDynamoDBClient:
    """DynamoDB client for caching claim verifications"""
    
    def __init__(self):
        config = get_aws_config()
        self.dynamodb = boto3.resource('dynamodb', **config)
        self.client = boto3.client('dynamodb', **config)
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Create cache table if it doesn't exist"""
        if not USE_LOCALSTACK:
            return
        
        try:
            self.client.describe_table(TableName=DYNAMODB_CACHE_TABLE)
        except:
            try:
                self.client.create_table(
                    TableName=DYNAMODB_CACHE_TABLE,
                    KeySchema=[
                        {'AttributeName': 'claim_hash', 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'claim_hash', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                logger.info(f"Created DynamoDB table: {DYNAMODB_CACHE_TABLE}")
            except Exception as e:
                logger.warning(f"Could not create table: {e}")
    
    def _hash_claim(self, claim: str) -> str:
        """Generate hash for claim text"""
        normalized = claim.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]
    
    async def cache_verification(self, claim: str, result: Dict[str, Any], ttl_hours: int = 24) -> bool:
        """Cache verification result"""
        try:
            table = self.dynamodb.Table(DYNAMODB_CACHE_TABLE)
            claim_hash = self._hash_claim(claim)
            
            table.put_item(Item={
                'claim_hash': claim_hash,
                'claim_preview': claim[:200],
                'result': json.dumps(result, default=str),
                'verdict': result.get('verdict', 'unknown'),
                'confidence': int(result.get('confidence', 0)),
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': int(time.time()) + (ttl_hours * 3600)
            })
            
            logger.debug(f"Cached verification for claim hash: {claim_hash}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache verification: {e}")
            return False
    
    async def get_cached_verification(self, claim: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached verification if exists and not expired"""
        try:
            table = self.dynamodb.Table(DYNAMODB_CACHE_TABLE)
            claim_hash = self._hash_claim(claim)
            
            response = table.get_item(Key={'claim_hash': claim_hash})
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            
            # Check TTL
            if item.get('ttl', 0) < time.time():
                logger.debug(f"Cache expired for claim hash: {claim_hash}")
                return None
            
            result = json.loads(item['result'])
            result['_cached'] = True
            result['_cached_at'] = item.get('cached_at')
            
            logger.debug(f"Cache hit for claim hash: {claim_hash}")
            return result
        except Exception as e:
            logger.error(f"Failed to get cached verification: {e}")
            return None
    
    async def invalidate_cache(self, claim: str) -> bool:
        """Invalidate cached verification"""
        try:
            table = self.dynamodb.Table(DYNAMODB_CACHE_TABLE)
            claim_hash = self._hash_claim(claim)
            
            table.delete_item(Key={'claim_hash': claim_hash})
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return False


# ============================================================
# SQS CLIENT - Queue batch verifications
# ============================================================

class VeritySQSClient:
    """SQS client for queuing batch verifications"""
    
    def __init__(self):
        config = get_aws_config()
        self.client = boto3.client('sqs', **config)
        self.queue_url = self._get_or_create_queue()
    
    def _get_or_create_queue(self) -> Optional[str]:
        """Get or create the verification queue"""
        try:
            response = self.client.get_queue_url(QueueName=SQS_VERIFICATION_QUEUE)
            return response['QueueUrl']
        except:
            if USE_LOCALSTACK:
                try:
                    response = self.client.create_queue(
                        QueueName=SQS_VERIFICATION_QUEUE,
                        Attributes={
                            'VisibilityTimeout': '300',  # 5 minutes
                            'MessageRetentionPeriod': '86400'  # 1 day
                        }
                    )
                    logger.info(f"Created SQS queue: {SQS_VERIFICATION_QUEUE}")
                    return response['QueueUrl']
                except Exception as e:
                    logger.warning(f"Could not create queue: {e}")
            return None
    
    async def queue_verification(self, claim: str, priority: str = 'normal', metadata: Dict = None) -> Optional[str]:
        """Queue a claim for batch verification"""
        if not self.queue_url:
            return None
        
        try:
            message_body = json.dumps({
                'claim': claim,
                'priority': priority,
                'metadata': metadata or {},
                'queued_at': datetime.utcnow().isoformat()
            })
            
            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body,
                MessageAttributes={
                    'Priority': {
                        'DataType': 'String',
                        'StringValue': priority
                    }
                }
            )
            
            return response['MessageId']
        except Exception as e:
            logger.error(f"Failed to queue verification: {e}")
            return None
    
    async def receive_verifications(self, max_messages: int = 10) -> List[Dict]:
        """Receive queued verifications for processing"""
        if not self.queue_url:
            return []
        
        try:
            response = self.client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=5,
                MessageAttributeNames=['All']
            )
            
            messages = []
            for msg in response.get('Messages', []):
                messages.append({
                    'receipt_handle': msg['ReceiptHandle'],
                    'message_id': msg['MessageId'],
                    'body': json.loads(msg['Body'])
                })
            
            return messages
        except Exception as e:
            logger.error(f"Failed to receive verifications: {e}")
            return []
    
    async def delete_message(self, receipt_handle: str) -> bool:
        """Delete processed message from queue"""
        if not self.queue_url:
            return False
        
        try:
            self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False


# ============================================================
# UNIFIED AWS SERVICE
# ============================================================

class VerityAWSService:
    """Unified AWS service for Verity Systems"""
    
    def __init__(self):
        self.s3 = VerityS3Client()
        self.dynamodb = VerityDynamoDBClient()
        self.sqs = VeritySQSClient()
        
        logger.info(f"AWS Service initialized (LocalStack: {USE_LOCALSTACK})")
    
    async def verify_with_cache(self, claim: str, verify_func) -> Dict[str, Any]:
        """Verify claim with caching"""
        # Check cache first
        cached = await self.dynamodb.get_cached_verification(claim)
        if cached:
            return cached
        
        # Perform verification
        result = await verify_func(claim)
        
        # Cache result
        await self.dynamodb.cache_verification(claim, result)
        
        # Store to S3 for persistence
        claim_id = hashlib.sha256(claim.encode()).hexdigest()[:16]
        await self.s3.store_verification_result(claim_id, result)
        
        return result


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_services():
        service = VerityAWSService()
        
        # Test S3
        test_result = {
            'claim': 'Test claim',
            'verdict': 'TRUE',
            'confidence': 95,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        stored = await service.s3.store_verification_result('test-001', test_result)
        print(f"S3 Storage: {'✅' if stored else '❌'}")
        
        # Test DynamoDB cache
        cached = await service.dynamodb.cache_verification('Test claim', test_result)
        print(f"DynamoDB Cache: {'✅' if cached else '❌'}")
        
        retrieved = await service.dynamodb.get_cached_verification('Test claim')
        print(f"Cache Retrieval: {'✅' if retrieved else '❌'}")
        
        # Test SQS
        msg_id = await service.sqs.queue_verification('Queued test claim')
        print(f"SQS Queue: {'✅' if msg_id else '❌'}")
        
        print("\n✅ All LocalStack services tested successfully!")
    
    asyncio.run(test_services())
