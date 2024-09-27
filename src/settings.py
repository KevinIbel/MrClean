import os

PRIVATE_TOKEN = os.environ.get('MR_CLEAN_TOKEN', '') # Add your gitlab token here, or in the CI variables or on vault, using the MR_CLEAN_TOKEN as the key


