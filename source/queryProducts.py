
import json
import boto3

def lambda_handler(event, context):
    print("Started...")
    # Initialize clients
    bedrock_agent_client = boto3.client('bedrock-agent-runtime')
    bedrock_runtime_client = boto3.client('bedrock-runtime')

    # Knowledge base retrieval
    knowledge_base_id = 'FWZRNX4EJM'
    query = 'other products similar to SnackNation - Ultra-Premium Healthy Snack Box . '

    retrieve_response = bedrock_agent_client.retrieve(
        knowledgeBaseId=knowledge_base_id,
        retrievalQuery={'text': query},
        retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 3}}
    )

    print("\n--- Retrieved Information ---")
    print("Number of retrieval results:", len(retrieve_response['retrievalResults']))

    if retrieve_response['retrievalResults']:
        print("Structure of first result:", json.dumps(retrieve_response['retrievalResults'][0], indent=2))
    else:
        print("No results found")


    for i, result in enumerate(retrieve_response['retrievalResults'], 1):
     if 'text' in result['content']:
            print(f"Match {i}:")
            print(result['content']['text'])
            print("---")

    # Process retrieved information
    retrieved_info = "\n".join([result['content']['text'] for result in retrieve_response['retrievalResults'] if 'text' in result['content']])

    # Print the combined retrieved info
    print("\nCombined Retrieved Information:")
    print(retrieved_info)


    # Augment the prompt
    augmented_prompt = f"""
    Using only the following information, provide a concise list of similar products: "{query} without adding any extra commentary or assumptions. You also do not need dissimilar products."

    Retrieved information:
    {retrieved_info}

    Answer:
    """
    print(f"Augmented prompt:**** {augmented_prompt}")

    # Invoke Llama 3 model
    model_id = 'meta.llama3-3-70b-instruct-v1:0'
    response = bedrock_runtime_client.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "prompt": augmented_prompt,
            "max_gen_len": 300,
            "temperature": 0.7,
            "top_p": 0.9
        })
    )

    # Process and print the response
    model_response = json.loads(response['body'].read())
    print(model_response['generation'])
