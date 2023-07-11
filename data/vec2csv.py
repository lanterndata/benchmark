import sys
import numpy as np
import csv

def vec_to_csv(input_file, output_file):
    # Read the dimension from the first 4 bytes of the file
    dimension = None
    with open(input_file, 'rb') as f:
        dimension = np.frombuffer(f.read(4), dtype=np.int32)[0]

    elem_type = None
    filesuffix = input_file.split(".")[-1]
    if filesuffix == "fvecs":
        elem_type = np.float32
        vector_size = dimension * 4
    elif filesuffix == "ivecs":
        elem_type = np.int32
        vector_size = dimension * 4
    elif filesuffix == "bvecs":
        elem_type = np.uint8
        vector_size = dimension
    else:
        raise Exception("unknown file format %s in %s" % (filesuffix, input_file))

    with open(input_file, 'rb') as f:
        with open(output_file, 'w', newline='') as f_out:
            writer = csv.writer(f_out)            
            while True:
                header = f.read(4)
                if not header:
                    break  # End of file reached

                vector = np.frombuffer(f.read(vector_size), dtype=elem_type)
                row = str(vector.tolist())
                if elem_type == np.int32:
                    row = row.replace('[', '{').replace(']', '}')
                writer.writerow([row])

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python vec2csv.py input_file output_file')
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        vec_to_csv(input_file, output_file)
