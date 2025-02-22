import json
import boto3
import yaml
import logging

logger = logging.getLogger(__name__)

def read_yaml(file_path):
    logger.debug("In read_yaml")
    try:
        with open(file_path, 'r') as file:
            yml_config = yaml.safe_load(file)
            logger.debug(f"read yml_config: {yml_config}")
        return yml_config
    except FileNotFoundError:
        logger.error(f"Config file not found: {file_path}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        return None
    
def execute_RAG_query(query, prompt_type):
    logger.debug("In execute_RAG_query...")
    prompt_config = read_yaml(file_path='prompts.yml')
    if prompt_config == None:
        logger.error("Failed loading prompts.yml")
        return
    else:
        logger.debug(f"Config: {prompt_config}")
        
    config = read_yaml(file_path='config.yml')
    if config == None:
        logger.error("Failed loading config.yml")
    else:
        logger.debug(f"Config: {config}")

    # Initialize clients
    bedrock_agent_client = boto3.client('bedrock-agent-runtime')
    bedrock_runtime_client = boto3.client('bedrock-runtime')

    # Knowledge base retrieval
    bedrock_config = config['bedrock']
    logger.debug(f'Bedrock Config: {bedrock_config}')
    knowledge_base_id = bedrock_config['kb_id']
    logger.debug(f"KB ID: {knowledge_base_id}")
    model_id = bedrock_config['model_id']

    # Retrieve information from the knowledge base
    retrieve_response = bedrock_agent_client.retrieve(
        knowledgeBaseId=knowledge_base_id,
        retrievalQuery={'text': query},
        retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': prompt_config['settings']['max_results']}}
    )
    
    logger.info("--- Retrieved Information ---")
    logger.info(f"Number of retrieval results: {len(retrieve_response['retrievalResults'])}")

    if retrieve_response['retrievalResults']:
        logger.debug("Structure of first result: %s", json.dumps(retrieve_response['retrievalResults'][0], indent=2))
    else:
        logger.error("No results found")

    for ii, result in enumerate(retrieve_response['retrievalResults'], 1):
     if 'text' in result['content']:
        logger.debug("Match %d:", ii)
        logger.debug("Content: %s", result['content']['text'])

    # Process retrieved information
    retrieved_info = "\n".join(
     result['content']['text'] 
        for result in retrieve_response['retrievalResults'] 
        if 'content' in result and 'text' in result['content']
    )

    # Log the combined retrieved info
    logger.debug("Combined Retrieved Information:\n%s", retrieved_info)


    # Select the appropriate prompt template
    prompt_template = prompt_config['prompts'][prompt_type]['template']

    # Construct the augmented prompt
    augmented_prompt = prompt_template.format(query=query, retrieved_info=retrieved_info)
    logger.debug("Augmented prompt:\n%s", augmented_prompt)

    # Add global instructions
    augmented_prompt += "\n\n" + "\n".join(prompt_config['instructions'])
    logger.debug("Augmented prompt with Instructions:\n%s", augmented_prompt)

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
    logger.debug("Model generation: %s", model_response['generation'])
    return model_response['generation']


def lambda_handler(event, context):
    execute_RAG_query(query='clothing', prompt_type="product_search")


