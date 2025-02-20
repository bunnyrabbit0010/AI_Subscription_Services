import boto3
import json
from pymongo import MongoClient
import ssl
import yaml
import json
from decimal import Decimal

def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(item) for item in obj]
    return obj




# Read the YAML configuration file
print('Loading config file')
with open('config.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
print('Finished Loading Config File..')

# Extract S3 configuration
s3_config = config['s3']
print('S3 Config: ', s3_config)
s3_bucket = s3_config['bucket']
s3_key = s3_config['key']

# Initialize S3 client
print('initializing S3 client..')
s3 = boto3.client('s3')

# Initialize DDB
dynamodb = boto3.resource('dynamodb')
ddb_table_name = "subscription_table"
ddb_table = dynamodb.Table(ddb_table_name)

# Read JSONL file from S3
response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
content = response['Body'].read().decode('utf-8')

# Process each line (JSON object) in the file
print('Processing JSON data..')
insert_count = 0
for line in content.splitlines():
    try:
        json_object = json.loads(line)
        print("Converting flots to Decimal")
        json_object = float_to_decimal(json_object)
        # Insert the JSON object into DocumentDB
        print(f"Inserting: {json_object}")
        ddb_table.put_item(Item=json_object)
        print(f"Successfully added item to DynamoDB table {ddb_table_name}")
        insert_count += 1
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        continue
    except Exception as e:
        print(f"Error inserting document: {e}")
        continue


print(f"Inserted Objects: {insert_count }")
print("Data insertion complete.")


"""
# Extract DocumentDB configuration
db_config = config['documentdb']
print('DB Config:', db_config)
docdb_host = db_config['host']
docdb_port = db_config['port']
docdb_username = db_config['username']
docdb_password = db_config['password']
docdb_database = db_config['database']
docdb_collection = db_config['collection']



# Initialize DocumentDB client
print('initializing DocumentDB client..')
client = MongoClient(
    host=docdb_host,
    port=docdb_port,
    username=docdb_username,
    password=docdb_password,
    tls=True,
    tlsAllowInvalidCertificates=True
)

print('Connecting to DB..')
db = client[docdb_database]
print('Connecting to Collection..')
collection = db[docdb_collection]

# Print the number of documents
document_count = collection.count_documents({})
print(f"Number of documents in the collection: {document_count}")

# Print the contents of each document
print("\nDocuments in the collection:")
for document in collection.find():
    print(document)


# Read JSONL file from S3
response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
content = response['Body'].read().decode('utf-8')

# Process each line (JSON object) in the file
print('Processing JSON data..')
for line in content.splitlines():
    try:
        json_object = json.loads(line)
        # Insert the JSON object into DocumentDB
        print(f"Inserting: {json_object}")
        collection.insert_one(json_object)
        print(f"Inserted...")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error inserting document: {e}")

print("Data insertion complete.")



print('Closing connection to DB..')
client.close()

"""