import json
import boto3

# --- 1. S3 Setup ---
s3 = boto3.client('s3', region_name='us-east-2') 
INPUT_S3_BUCKET = "aws-subscription-boxes"  
INPUT_S3_KEY = "meta_Subscription_Boxes.jsonl"  
OUTPUT_S3_BUCKET = "aws-subscription-boxes" 
OUTPUT_S3_KEY = "subscription_for_embedding.jsonl"  

def create_combined_text_jsonl_s3(input_bucket, input_key, output_bucket, output_key, text_fields):
    """Creates a new JSONL file with combined text from specified fields and stores it in S3."""
    try:
        obj = s3.get_object(Bucket=input_bucket, Key=input_key)
        lines = obj['Body'].read().decode('utf-8').splitlines()  # Read the file line by line

        combined_text_lines = [] # List to store the combined text lines

        print("Generating combined text")
        lines_processed = 0

        for line in lines:
            try:
                json_obj = json.loads(line)
                combined_text = " ".join([str(json_obj.get(field)) for field in text_fields if json_obj.get(field)])
                print(f"combined_text: {combined_text}")
                output_obj = {"combined_text": combined_text}
                combined_text_lines.append(json.dumps(output_obj) + "\n") # Append the line to the list
                lines_processed += 1
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON object: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

        print(f"Lines processed: {lines_processed}")

        print("Writing to S3...")
        # Write to S3 in chunks (important for large files)
        s3.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body=''.join(combined_text_lines), # Join all the lines into a string
            ContentType='application/jsonl' # Set the content type
        )

        print(f"Combined text stored in S3: s3://{output_bucket}/{output_key}")


    except s3.exceptions.NoSuchKey:
        print(f"Input file not found in S3: s3://{input_bucket}/{input_key}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
fields_to_combine = ["title", "main_category", "features"]  # Customize the fields you want to combine
create_combined_text_jsonl_s3(INPUT_S3_BUCKET, INPUT_S3_KEY, OUTPUT_S3_BUCKET, OUTPUT_S3_KEY, fields_to_combine)