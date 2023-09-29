import itertools

def chunks(iterable, batch_size=100):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))
        

class BaseCloudProvider:
    def create_index(self):
        raise Exception("Not implemented")

    def delete_index(self):
        raise Exception("Not implemented")
        
    def insert_data(self):
        raise Exception("Not implemented")

    def search(self):
        raise Exception("Not implemented")

