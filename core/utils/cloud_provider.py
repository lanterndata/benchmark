import os
from .pinecone_provider import Pinecone
from .constants import Cloud


def get_cloud_provider(provider_name):
    if provider_name == Cloud.PINECONE:
        return Pinecone(os.environ['PINECONE_API_KEY'], os.environ['PINECONE_ENV'])
    raise Exception(f'Invalid cloud provider {provider_name}')
    
