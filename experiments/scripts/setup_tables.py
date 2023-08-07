import os
import argparse
import urllib.request
import psycopg2

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--datapath", default="/tmp/lanterndb/vector_datasets", help="Path to data directory")
args = parser.parse_args()

data_dir = args.datapath
sift_dir = os.path.join(data_dir, "sift")
siftsmall_dir = os.path.join(data_dir, "siftsmall")

if not os.path.exists(sift_dir):
    print("SIFT directory does not exist. Creating... and downloading sift vectors...") 
    os.makedirs(sift_dir)
    os.makedirs(siftsmall_dir)

    siftsmall_fnames = ['siftsmall_base.csv', 'siftsmall_query.csv', 'siftsmall_truth.csv']
    sift_fnames = ['sift_base.csv', 'sift_query.csv', 'sift_truth.csv']

    for filename in siftsmall_fnames:
        print(f"Downloading SIFTSMALL {filename}")
        urllib.request.urlretrieve(f"https://storage.googleapis.com/lanterndata/siftsmall/{filename}", os.path.join(siftsmall_dir, filename))
    for filename in sift_fnames:
        print(f"Downloading SIFT {filename}")
        urllib.request.urlretrieve(f"https://storage.googleapis.com/lanterndata/sift/{filename}", os.path.join(sift_dir, filename))
else:
    print("SIFT directory exists. Skipping file download.")

print("Creating tables...")

conn = psycopg2.connect(os.environ["DATABASE_URL"]) 
cur = conn.cursor()

# with open("create_tables.sql", "r") as sqlfile:
#     cur.execute(sqlfile.read())

# with open("create_tables_recall.sql", "r") as sqlfile:
#     cur.execute(sqlfile.read())

#with open("../../db/init/init_results.sql", "r") as sqlfile:
#    cur.execute(sqlfile.read())
#with open("../../db/init/init_util.sql", "r") as sqlfile:
#    cur.execute(sqlfile.read())
with open("create_tables_derived.sql", "r") as sqlfile:
    cur.execute(sqlfile.read())

conn.commit()
cur.close()
conn.close()

print("Done!")