import boto3
import json
from pymongo import MongoClient
import ssl
import yaml

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


# Extract DocumentDB configuration
db_config = config['documentdb']
print('DB Config:', db_config)
docdb_host = db_config['host']
docdb_port = db_config['port']
docdb_username = db_config['username']
docdb_password = db_config['password']
docdb_database = db_config['database']
docdb_collection = db_config['collection']

# Initialize S3 client
print('initializing S3 client..')
s3 = boto3.client('s3')

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