import os
from .pinecone_provider import Pinecone
from .constants import Cloud
from .validate_env_vars import validate_env_vars


def get_cloud_provider(provider_name):
    validate_env_vars(['PINECONE_API_KEY', 'PINECONE_ENV'])
    if provider_name == Cloud.PINECONE:
        return Pinecone(os.environ['PINECONE_API_KEY'], os.environ['PINECONE_ENV'])
    raise Exception(f'Invalid cloud provider {provider_name}')
    
