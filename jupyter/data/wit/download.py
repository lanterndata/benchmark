import urllib.request
import gzip
import shutil

url = 'https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-1percent_sample.tsv.gz'
filename = 'data.tsv'

# Download the data from the URL
with urllib.request.urlopen(url) as response:
  with open(filename + '.gz', 'wb') as f:
    f.write(response.read())

# Extract the data from the compressed file
with gzip.open(filename + '.gz', 'rb') as f_in:
  with open(filename, 'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)