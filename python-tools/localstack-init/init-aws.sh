#!/bin/bash
# Verity Systems - LocalStack Initialization Script
# This script runs when LocalStack starts and creates all required resources

echo "🚀 Initializing Verity Systems LocalStack resources..."

# Wait for LocalStack to be ready
until curl -s http://localhost:4566/_localstack/health | grep -q '"s3": "available"'; do
    echo "Waiting for LocalStack..."
    sleep 2
done

# ===========================================
# S3 BUCKETS
# ===========================================
echo "📦 Creating S3 buckets..."

awslocal s3 mb s3://verity-verification-results 2>/dev/null || true
awslocal s3 mb s3://verity-reports 2>/dev/null || true
awslocal s3 mb s3://verity-exports 2>/dev/null || true
awslocal s3 mb s3://verity-backups 2>/dev/null || true

# Enable versioning for results bucket
awslocal s3api put-bucket-versioning \
    --bucket verity-verification-results \
    --versioning-configuration Status=Enabled

# Set lifecycle policy for old verifications
awslocal s3api put-bucket-lifecycle-configuration \
    --bucket verity-verification-results \
    --lifecycle-configuration '{
        "Rules": [
            {
                "ID": "ExpireOldVerifications",
                "Status": "Enabled",
                "Filter": {"Prefix": "verifications/"},
                "Expiration": {"Days": 90}
            }
        ]
    }'

echo "✅ S3 buckets created"

# ===========================================
# DYNAMODB TABLES
# ===========================================
echo "📊 Creating DynamoDB tables..."

# Claim cache table
awslocal dynamodb create-table \
    --table-name verity-claim-cache \
    --attribute-definitions \
        AttributeName=claim_hash,AttributeType=S \
    --key-schema \
        AttributeName=claim_hash,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Environment,Value=development 2>/dev/null || true

# User sessions table
awslocal dynamodb create-table \
    --table-name verity-user-sessions \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=session_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=session_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST 2>/dev/null || true

# Verification history table
awslocal dynamodb create-table \
    --table-name verity-verification-history \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST 2>/dev/null || true

# Enable TTL on cache table
awslocal dynamodb update-time-to-live \
    --table-name verity-claim-cache \
    --time-to-live-specification Enabled=true,AttributeName=ttl 2>/dev/null || true

echo "✅ DynamoDB tables created"

# ===========================================
# SQS QUEUES
# ===========================================
echo "📬 Creating SQS queues..."

# Main verification queue
awslocal sqs create-queue \
    --queue-name verity-verification-queue \
    --attributes '{
        "VisibilityTimeout": "300",
        "MessageRetentionPeriod": "86400",
        "ReceiveMessageWaitTimeSeconds": "20"
    }' 2>/dev/null || true

# Dead letter queue for failed verifications
awslocal sqs create-queue \
    --queue-name verity-verification-dlq \
    --attributes '{
        "MessageRetentionPeriod": "604800"
    }' 2>/dev/null || true

# Batch processing queue
awslocal sqs create-queue \
    --queue-name verity-batch-queue \
    --attributes '{
        "VisibilityTimeout": "600",
        "MessageRetentionPeriod": "172800"
    }' 2>/dev/null || true

# Priority verification queue (for premium users)
awslocal sqs create-queue \
    --queue-name verity-priority-queue \
    --attributes '{
        "VisibilityTimeout": "120",
        "MessageRetentionPeriod": "43200"
    }' 2>/dev/null || true

echo "✅ SQS queues created"

# ===========================================
# SECRETS MANAGER
# ===========================================
echo "🔐 Creating secrets (placeholders)..."

# API keys secret (placeholder - replace with real values)
awslocal secretsmanager create-secret \
    --name verity/api-keys \
    --description "Verity Systems API Keys" \
    --secret-string '{
        "anthropic_api_key": "placeholder",
        "openai_api_key": "placeholder",
        "groq_api_key": "placeholder",
        "comet_api_key": "placeholder"
    }' 2>/dev/null || true

# Database credentials
awslocal secretsmanager create-secret \
    --name verity/database \
    --description "Database credentials" \
    --secret-string '{
        "host": "localhost",
        "port": 5432,
        "database": "verity",
        "username": "verity_user",
        "password": "placeholder"
    }' 2>/dev/null || true

echo "✅ Secrets created"

# ===========================================
# CLOUDWATCH LOG GROUPS
# ===========================================
echo "📈 Creating CloudWatch log groups..."

awslocal logs create-log-group --log-group-name /verity/api-server 2>/dev/null || true
awslocal logs create-log-group --log-group-name /verity/verification-engine 2>/dev/null || true
awslocal logs create-log-group --log-group-name /verity/batch-processor 2>/dev/null || true

# Set retention
awslocal logs put-retention-policy --log-group-name /verity/api-server --retention-in-days 30
awslocal logs put-retention-policy --log-group-name /verity/verification-engine --retention-in-days 30
awslocal logs put-retention-policy --log-group-name /verity/batch-processor --retention-in-days 14

echo "✅ CloudWatch log groups created"

# ===========================================
# SUMMARY
# ===========================================
echo ""
echo "=========================================="
echo "✅ LocalStack initialization complete!"
echo "=========================================="
echo ""
echo "Resources created:"
echo "  S3 Buckets: 4"
echo "  DynamoDB Tables: 3"
echo "  SQS Queues: 4"
echo "  Secrets: 2"
echo "  CloudWatch Log Groups: 3"
echo ""
echo "LocalStack endpoint: http://localhost:4566"
echo ""
