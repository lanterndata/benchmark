from typing import Optional, List, Union, Dict, Tuple, Generic, Callable, TypeVar
from pinecone.index import Index, parse_query_response, fix_tuple_length, Iterable, _OPENAPI_ENDPOINT_PARAMS # type: ignore
from pinecone.core.client.models import QueryVector, QueryResponse, SparseValues, QueryRequest  # type: ignore
from pinecone.core.utils.error_handling import validate_and_convert_errors  # type: ignore


T = TypeVar('T')

# This class is an async wrapper for multiprocessing.AsyncResult functions that don't use regular async/await
# Pinecone is unfortunately one of those libraries.
class AsyncHandle(Generic[T]):
    _retrieval: Callable[..., T]
    _is_done: bool
    _result: T
    def __init__(self, retrieval: Callable[..., T]):
        self._retrieval = retrieval
        self._is_done = False
    def get(self):
        if not self._is_done:
            self._is_done = True
            self._result = self._retrieval()
        return self._result

###
## This works around bugs in Pinecone which doesn't support async properly. The underlying API does support async,
## so we need to modify the Pinecone client to support it by deriving from their existing index class.
## Note: This will be fragile if Pinecone updates their code, so we need to stay pinned to their client library version.

class AsyncIndex(Index):
    @validate_and_convert_errors
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def query(self,
              vector: Optional[List[float]] = None,
              id: Optional[str] = None,
              queries: Optional[Union[List[QueryVector], List[Tuple]]] = None,
              top_k: Optional[int] = None,
              namespace: Optional[str] = None,
              filter: Optional[Dict[str, Union[str, float, int, bool, List, dict]]] = None,
              include_values: Optional[bool] = None,
              include_metadata: Optional[bool] = None,
              sparse_vector: Optional[Union[SparseValues, Dict[str, Union[List[float], List[int]]]]] = None,
              **kwargs) -> AsyncHandle[QueryResponse]:
        """
        The Query operation searches a namespace, using a query vector.
        It retrieves the ids of the most similar items in a namespace, along with their similarity scores.

        API reference: https://docs.pinecone.io/reference/query

        Examples:
            >>> index.query(vector=[1, 2, 3], top_k=10, namespace='my_namespace')
            >>> index.query(id='id1', top_k=10, namespace='my_namespace')
            >>> index.query(vector=[1, 2, 3], top_k=10, namespace='my_namespace', filter={'key': 'value'})
            >>> index.query(id='id1', top_k=10, namespace='my_namespace', include_metadata=True, include_values=True)
            >>> index.query(vector=[1, 2, 3], sparse_vector={'indices': [1, 2], 'values': [0.2, 0.4]},
            >>>             top_k=10, namespace='my_namespace')
            >>> index.query(vector=[1, 2, 3], sparse_vector=SparseValues([1, 2], [0.2, 0.4]),
            >>>             top_k=10, namespace='my_namespace')

        Args:
            vector (List[float]): The query vector. This should be the same length as the dimension of the index
                                  being queried. Each `query()` request can contain only one of the parameters
                                  `queries`, `id` or `vector`.. [optional]
            id (str): The unique ID of the vector to be used as a query vector.
                      Each `query()` request can contain only one of the parameters
                      `queries`, `vector`, or  `id`.. [optional]
            queries ([QueryVector]): DEPRECATED. The query vectors.
                                     Each `query()` request can contain only one of the parameters
                                     `queries`, `vector`, or  `id`.. [optional]
            top_k (int): The number of results to return for each query. Must be an integer greater than 1.
            namespace (str): The namespace to fetch vectors from.
                             If not specified, the default namespace is used. [optional]
            filter (Dict[str, Union[str, float, int, bool, List, dict]):
                    The filter to apply. You can use vector metadata to limit your search.
                    See https://www.pinecone.io/docs/metadata-filtering/.. [optional]
            include_values (bool): Indicates whether vector values are included in the response.
                                   If omitted the server will use the default value of False [optional]
            include_metadata (bool): Indicates whether metadata is included in the response as well as the ids.
                                     If omitted the server will use the default value of False  [optional]
            sparse_vector: (Union[SparseValues, Dict[str, Union[List[float], List[int]]]]): sparse values of the query vector.
                            Expected to be either a SparseValues object or a dict of the form:
                             {'indices': List[int], 'values': List[float]}, where the lists each have the same length.
        Keyword Args:
            Supports OpenAPI client keyword arguments. See pinecone.core.client.models.QueryRequest for more details.

        Returns: QueryResponse object which contains the list of the closest vectors as ScoredVector objects,
                 and namespace name.
        """
        def _query_transform(item):
            if isinstance(item, QueryVector):
                return item
            if isinstance(item, tuple):
                values, filter = fix_tuple_length(item, 2)
                if filter is None:
                    return QueryVector(values=values, _check_type=_check_type)
                else:
                    return QueryVector(values=values, filter=filter, _check_type=_check_type)
            if isinstance(item, Iterable):
                return QueryVector(values=item, _check_type=_check_type)
            raise ValueError(f"Invalid query vector value passed: cannot interpret type {type(item)}")

        # force async
        kwargs['async_req'] = True

        _check_type = kwargs.pop('_check_type', False)
        queries = list(map(_query_transform, queries)) if queries is not None else None

        sparse_vector = self._parse_sparse_values_arg(sparse_vector)
        args_dict = self._parse_non_empty_args([('vector', vector),
                                                ('id', id),
                                                ('queries', queries),
                                                ('top_k', top_k),
                                                ('namespace', namespace),
                                                ('filter', filter),
                                                ('include_values', include_values),
                                                ('include_metadata', include_metadata),
                                                ('sparse_vector', sparse_vector)])
        response = self._vector_api.query(
            QueryRequest(
                **args_dict,
                _check_type=_check_type,
                **{k: v for k, v in kwargs.items() if k not in _OPENAPI_ENDPOINT_PARAMS}
            ),
            **{k: v for k, v in kwargs.items() if k in _OPENAPI_ENDPOINT_PARAMS}
        )
        def handler():
            return parse_query_response(response.get(), vector is not None or id)

        return AsyncHandle(handler)