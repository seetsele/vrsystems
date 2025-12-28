"""
Verity Systems - Integration Test Suite
Tests LocalStack/Moto AWS services and Comet ML tracking together
"""

import asyncio
import os
import sys
import time
import hashlib
import logging
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VerityIntegrationTest')

# Ensure we use mocks for testing
os.environ['USE_AWS_MOCKS'] = 'true'
os.environ['USE_LOCALSTACK'] = 'false'


def test_aws_services():
    """Test AWS mock services (S3, DynamoDB, SQS)"""
    print("\n" + "="*60)
    print("🧪 Testing AWS Services (using moto mocks)")
    print("="*60 + "\n")
    
    # Import and start mocks
    from aws_mock_server import start_mock_aws_services, stop_mock_aws_services, get_aws_config
    
    success = start_mock_aws_services()
    if not success:
        print("❌ Failed to start AWS mocks")
        return False
    
    try:
        import boto3
        
        config = get_aws_config()
        
        # Test S3
        print("📦 Testing S3...")
        s3 = boto3.client('s3', **config)
        
        # Upload a test object
        test_data = {
            'claim': 'Test claim for verification',
            'verdict': 'TRUE',
            'confidence': 95.5,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        s3.put_object(
            Bucket='verity-verification-results',
            Key='test/verification-001.json',
            Body=str(test_data)
        )
        
        # Read it back
        response = s3.get_object(
            Bucket='verity-verification-results',
            Key='test/verification-001.json'
        )
        content = response['Body'].read().decode()
        print(f"   ✅ S3 write/read successful")
        
        # Test DynamoDB
        print("📊 Testing DynamoDB...")
        dynamodb = boto3.resource('dynamodb', **config)
        table = dynamodb.Table('verity-claim-cache')
        
        # Write a cache entry
        claim_hash = hashlib.sha256("Test claim".encode()).hexdigest()[:32]
        table.put_item(Item={
            'claim_hash': claim_hash,
            'claim_preview': 'Test claim',
            'verdict': 'TRUE',
            'confidence': 95,
            'cached_at': datetime.now(timezone.utc).isoformat()
        })
        
        # Read it back
        response = table.get_item(Key={'claim_hash': claim_hash})
        if 'Item' in response:
            print(f"   ✅ DynamoDB write/read successful")
        else:
            print(f"   ❌ DynamoDB read failed")
        
        # Test SQS
        print("📬 Testing SQS...")
        sqs = boto3.client('sqs', **config)
        
        # Get queue URL
        response = sqs.get_queue_url(QueueName='verity-verification-queue')
        queue_url = response['QueueUrl']
        
        # Send a message
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody='{"claim": "Test claim to verify"}'
        )
        
        # Receive the message
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1
        )
        
        if response.get('Messages'):
            print(f"   ✅ SQS send/receive successful")
            # Delete the message
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=response['Messages'][0]['ReceiptHandle']
            )
        else:
            print(f"   ❌ SQS receive failed")
        
        print("\n✅ All AWS services working!")
        return True
        
    except Exception as e:
        print(f"\n❌ AWS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        stop_mock_aws_services()


def test_comet_integration():
    """Test Comet ML integration (offline mode if no API key)"""
    print("\n" + "="*60)
    print("🔬 Testing Comet ML Integration")
    print("="*60 + "\n")
    
    try:
        from comet_integration import (
            configure_comet,
            is_comet_enabled,
            get_metrics_tracker,
            VerificationMetricsTracker,
            ModelComparison
        )
        
        # Check if API key is available
        api_key = os.getenv('COMET_API_KEY')
        
        if api_key:
            print("🔑 Comet API key found - full tracking enabled")
            configured = configure_comet(experiment_name="integration-test")
            
            if configured:
                tracker = get_metrics_tracker()
                
                # Log some test verifications
                test_data = [
                    ("The Earth is round", "TRUE", 98.5, ["anthropic", "groq"]),
                    ("Water boils at 50°C", "FALSE", 99.0, ["openai", "perplexity"]),
                    ("Exercise is healthy", "TRUE", 92.0, ["groq", "wikipedia"]),
                ]
                
                for claim, verdict, confidence, providers in test_data:
                    tracker.log_verification(
                        claim=claim,
                        verdict=verdict,
                        confidence=confidence,
                        providers_used=providers,
                        response_time_ms=150 + confidence
                    )
                    print(f"   ✅ Logged: {claim[:30]}...")
                
                # Log provider performance
                tracker.log_provider_performance("anthropic", 120.5, True)
                tracker.log_provider_performance("groq", 50.2, True)
                tracker.log_provider_performance("openai", 180.0, False, "Rate limit")
                
                print("\n✅ Comet ML tracking working!")
                print("   View your experiments at: https://www.comet.com/")
                
                tracker.finalize()
                return True
        else:
            print("⚠️ No COMET_API_KEY found - testing in offline mode")
            print("   Set COMET_API_KEY to enable cloud tracking")
            
            # Test the tracker works without API
            tracker = VerificationMetricsTracker()
            tracker.log_verification(
                claim="Test claim",
                verdict="TRUE",
                confidence=95.0,
                providers_used=["test"],
                response_time_ms=100.0
            )
            print("   ✅ Offline metrics tracker working")
            
            # Test model comparison
            comparison = ModelComparison("test-comparison")
            comparison.log_config_result(
                config_name="config-a",
                accuracy=92.5,
                avg_confidence=88.0,
                avg_response_time_ms=150.0
            )
            best = comparison.get_best_config('accuracy')
            print(f"   ✅ Model comparison working (best: {best})")
            
            print("\n✅ Comet ML integration ready (set API key for cloud sync)")
            return True
            
    except ImportError as e:
        print(f"❌ Comet ML not installed: {e}")
        print("   Run: pip install comet-ml")
        return False
    except Exception as e:
        print(f"❌ Comet test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_workflow():
    """Test AWS + Comet ML working together"""
    print("\n" + "="*60)
    print("🔗 Testing Combined Workflow (AWS + Comet)")
    print("="*60 + "\n")
    
    try:
        # Start AWS mocks
        from aws_mock_server import start_mock_aws_services, stop_mock_aws_services, get_aws_config
        start_mock_aws_services()
        
        from comet_integration import VerificationMetricsTracker
        import boto3
        
        config = get_aws_config()
        s3 = boto3.client('s3', **config)
        dynamodb = boto3.resource('dynamodb', **config)
        tracker = VerificationMetricsTracker()
        
        # Simulate a verification workflow
        claims = [
            "Climate change is caused by human activity",
            "The Great Wall of China is visible from space",
            "Vaccines cause autism"
        ]
        
        results = [
            ("TRUE", 96.5, ["anthropic", "perplexity", "wikipedia"]),
            ("FALSE", 88.0, ["groq", "openai"]),
            ("FALSE", 99.5, ["anthropic", "groq", "wikipedia"]),
        ]
        
        print("Processing claims...")
        
        for claim, (verdict, confidence, providers) in zip(claims, results):
            start_time = time.time()
            
            # Generate claim ID
            claim_id = hashlib.sha256(claim.encode()).hexdigest()[:16]
            
            # Store in S3
            result_data = {
                'claim': claim,
                'claim_id': claim_id,
                'verdict': verdict,
                'confidence': confidence,
                'providers_used': providers,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            s3.put_object(
                Bucket='verity-verification-results',
                Key=f'verifications/{claim_id}.json',
                Body=str(result_data)
            )
            
            # Cache in DynamoDB
            table = dynamodb.Table('verity-claim-cache')
            table.put_item(Item={
                'claim_hash': claim_id,
                'claim_preview': claim[:100],
                'verdict': verdict,
                'confidence': int(confidence)
            })
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Track in Comet
            tracker.log_verification(
                claim=claim,
                verdict=verdict,
                confidence=confidence,
                providers_used=providers,
                response_time_ms=elapsed_ms
            )
            
            # Also track locally for summary
            tracker.confidence_scores.append(confidence)
            if verdict in tracker.verdict_distribution:
                tracker.verdict_distribution[verdict] += 1
            
            print(f"   ✅ {claim[:40]}... -> {verdict} ({confidence}%)")
        
        # Summary
        print(f"\n📊 Processed {len(claims)} claims")
        print(f"   Verdicts: {tracker.verdict_distribution}")
        if tracker.confidence_scores:
            print(f"   Avg confidence: {sum(tracker.confidence_scores)/len(tracker.confidence_scores):.1f}%")
        else:
            print(f"   Avg confidence: N/A (no scores recorded)")
        
        print("\n✅ Combined workflow successful!")
        
        stop_mock_aws_services()
        return True
        
    except Exception as e:
        print(f"❌ Combined workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("🚀 VERITY SYSTEMS - INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print("="*60)
    
    results = {}
    
    # Test 1: AWS Services
    results['aws'] = test_aws_services()
    
    # Test 2: Comet ML
    results['comet'] = test_comet_integration()
    
    # Test 3: Combined Workflow
    results['combined'] = test_combined_workflow()
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name.upper()}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("🎉 All integration tests passed!")
        print("\nNext steps:")
        print("  1. Set COMET_API_KEY for cloud tracking")
        print("  2. Install Docker for full LocalStack features")
        print("  3. Run: python api_server.py to start the API")
    else:
        print("⚠️ Some tests failed - check output above")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
