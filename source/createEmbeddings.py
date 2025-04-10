import boto3
import json

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-agent', region_name='us-east-2')

# Define the knowledge base configuration
kb_config = {
    "name": "MyCustomKnowledgeBase",
    "description": "Knowledge base with selected JSON fields",
    "roleArn": "arn:aws:iam::111122223333:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_123",
    "knowledgeBaseConfiguration": {
        "type": "VECTOR",
        "vectorKnowledgeBaseConfiguration": {
            "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0",
            "embeddingModelConfiguration": {
                "bedrockEmbeddingModelConfiguration": {
                    "dimensions": 1024
                }
            }
        }
    },
    "storageConfiguration": {
        "opensearchServerlessConfiguration": {
            "collectionArn": "arn:aws:aoss:us-east-1:111122223333:collection/abcdefghij1234567890",
            "fieldMapping": {
                "metadataField": "metadata",
                "textField": "text",
                "vectorField": "vector"
            },
            "vectorIndexName": "MyVectorIndex"
        }
    },
    "dataSource": {
        "name": "MyS3DataSource",
        "dataSourceConfiguration": {
            "s3Configuration": {
                "bucketArn": "arn:aws:s3:::MyBucket",
                "inclusionPrefixes": ["path/to/your/file.json"]
            }
        }
    }
}

# Create the knowledge base
response = bedrock_client.create_knowledge_base(**kb_config)

print(f"Knowledge base created with ID: {response['knowledgeBaseId']}")

# Define a function to process and select specific JSON fields
def process_json(json_data):
    selected_fields = {
        "main_category": json_data.get("main_category"),
        "title": json_data.get("title"),
        "average_rating": json_data.get("average_rating"),
        "features": json_data.get("features")
    }
    return json.dumps(selected_fields)

# Process the S3 file and ingest selected data
s3_client = boto3.client('s3')
bucket_name = "MyBucket"
file_key = "path/to/your/file.json"

response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
file_content = response['Body'].read().decode('utf-8')
json_data = json.loads(file_content)

processed_data = process_json(json_data)

# Ingest the processed data into the knowledge base
ingestion_job_config = {
    "knowledgeBaseId": response['knowledgeBaseId'],
    "dataSource": {
        "name": "ProcessedDataSource",
        "dataSourceConfiguration": {
            "inlineData": {
                "data": processed_data
            }
        }
    }
}

ingestion_response = bedrock_client.start_ingestion_job(**ingestion_job_config)

print(f"Ingestion job started with ID: {ingestion_response['ingestionJobId']}")
