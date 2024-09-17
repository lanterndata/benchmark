import os
import pinecone
from .pinecone_async_index import AsyncIndex
from .base_cloud_provider import BaseCloudProvider, chunks

class Pinecone(BaseCloudProvider):
    def __init__(self, api_key, environment):
        pinecone.init(api_key=api_key, environment=environment)
    
    def create_index(self, index_params, vectors):
        pinecone.create_index(name=index_params['name'], dimension=len(vectors[0][1]), metric=index_params['metric'], pods=index_params['pods'], replicas=index_params['replicas'], pod_type=index_params['pod_type'])
        return self.insert_data(index_params['name'], vectors)

    def delete_index(self, name):
        try:
            pinecone.delete_index(name)
        except pinecone.NotFoundException:
            pass

    def insert_data(self, index_name, vectors):
        with pinecone.Index(index_name, pool_threads=os.cpu_count()) as index:
            # Send requests in parallel
            async_results = [
                index.upsert(vectors=ids_vectors_chunk, async_req=True)
                for ids_vectors_chunk in chunks(vectors, batch_size=100)
            ]
            # Wait for and retrieve responses (this raises in case of error)
            [async_result.get() for async_result in async_results]

    def calculate_recall(self, index_name, vectors_to_query, expected_results, k):
        recall_sum = 0
        chunk_size = 100
        vector_chunks = chunks(vectors_to_query, chunk_size)

        with AsyncIndex(index_name, pool_threads=os.cpu_count()) as index:
            for (chunk_idx, chunk) in enumerate(vector_chunks):
                chunk_idx_offset = chunk_size * chunk_idx
                async_results = [
                    (chunk_idx_offset + idx, index.query(vector=vec, top_k=k, include_values=False, async_req=True))
                    for (idx, vec) in enumerate(chunk)
                ]
                responses = [(idx, async_result.get()) for (idx, async_result) in async_results]

                for (idx, res) in responses:
                    expected_id_set = set(expected_results[idx][:k])
                    recall_sum += len(expected_id_set.intersection(map(lambda x: int(x['id']), res['matches'])))

        return recall_sum / len(vectors_to_query)
