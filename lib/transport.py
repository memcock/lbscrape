import requests
from config import getLogger

_log = getLogger(__name__)

# Downloads a specified url, to the specified file_name 
# in the configured download path or to directory if specified
def get(self, url, filename, dir = None):
        # NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
            return True
        return False