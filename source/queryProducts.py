import json
import boto3
import yaml

def read_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            yml_config = yaml.safe_load(file)
            print(f"read yml_config: {yml_config}")
        return yml_config
    except FileNotFoundError:
        print(f"Config file not found: {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None
    
def execute_RAG_query(query, prompt_type):
    print("Started...")
    prompt_config = read_yaml(file_path='prompts.yml')
    if prompt_config == None:
        return "Failed loading prompts.yml"
    else:
        print(f"Config: {prompt_config}")
        
    config = read_yaml(file_path='config.yml')
    if config == None:
        return "Failed loading config.yml"
    else:
        print(f"Config: {config}")

    # Initialize clients
    bedrock_agent_client = boto3.client('bedrock-agent-runtime')
    bedrock_runtime_client = boto3.client('bedrock-runtime')

    # Knowledge base retrieval
    bedrock_config = config['bedrock']
    print('Bedrock Config: ', bedrock_config)
    knowledge_base_id = bedrock_config['kb_id']
    print(f"KB ID: {knowledge_base_id}")
    model_id = bedrock_config['model_id']

    # Retrieve information from the knowledge base
    retrieve_response = bedrock_agent_client.retrieve(
        knowledgeBaseId=knowledge_base_id,
        retrievalQuery={'text': query},
        retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': prompt_config['settings']['max_results']}}
    )
    
    print("\n--- Retrieved Information ---")
    print("Number of retrieval results:", len(retrieve_response['retrievalResults']))

    if retrieve_response['retrievalResults']:
        print("Structure of first result:", json.dumps(retrieve_response['retrievalResults'][0], indent=2))
    else:
        print("No results found")

    for ii, result in enumerate(retrieve_response['retrievalResults'], 1):
     if 'text' in result['content']:
            print(f"Match {ii}:")
            print(result['content']['text'])
            print("---")
    
    # Process retrieved information
    retrieved_info = "\n".join([result['content']['text'] for result in retrieve_response['retrievalResults'] if 'text' in result['content']])

    # Print the combined retrieved info
    print("\nCombined Retrieved Information:")
    print(retrieved_info)

    # Select the appropriate prompt template
    prompt_template = prompt_config['prompts'][prompt_type]['template']

    # Construct the augmented prompt
    augmented_prompt = prompt_template.format(query=query, retrieved_info=retrieved_info)
    print(f"Augmented prompt:**** {augmented_prompt}")

    # Add global instructions
    augmented_prompt += "\n\n" + "\n".join(prompt_config['instructions'])
    print(f"Augmented prompt with Instructions:**** {augmented_prompt}")

        # Invoke the LLM model
    response = bedrock_runtime_client.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "prompt": augmented_prompt,
            "max_gen_len": prompt_config['settings']['max_tokens'],
            "temperature": prompt_config['settings']['temperature'],
            "top_p": prompt_config['settings']['top_p']
        })
    )
    
     # Process and print the response
    model_response = json.loads(response['body'].read())
    print(model_response['generation'])
    return model_response['generation']



def lambda_handler(event, context):
    execute_RAG_query(query='clothing', prompt_type="product_search")


