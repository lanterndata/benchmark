import os

def validate_env_vars(keys):
    for key in keys:
        if key not in os.environ:
            raise Exception(f'Missing "{key}" environment variable')

