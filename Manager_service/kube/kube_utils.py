import os


# Bunch of utility functions and data for the kube_client
# # worker plurality estimation
# # template setup
# # # source files setup
# # # docker image setup
# # manifests
# # deployment


# Utils for determening how big the data is
# set a chuck size of a dataset file to be at 64 MB
#CHUNK_SIZE = 128 * 1024 * 1024 # 128 MB
CHUNK_SIZE = 128 # 128 bytes for testing


# return the size of a file in bytes
def get_file_size(file_path):
    return os.path.getsize(file_path)

# according to the default chuck size, estimate how many mappers should be used.
def estimate_num_mappers(file_size, chunk_size=CHUNK_SIZE):
    return file_size // chunk_size + (1 if file_size % chunk_size > 0 else 0)

# split a given file to chucks so that they can be used for different workers
def split_datafile(file_path, jid, chunk_size=CHUNK_SIZE):
    # check if the directory exists
    chunk_dir = os.path.join(os.getcwd(), 'mnt/data/'+str(jid)+'/mapper/in')
    reducer_in = os.path.join(os.getcwd(), 'mnt/data/'+str(jid)+'/reducer/in')
    reducer_out = os.path.join(os.getcwd(), 'mnt/data/'+str(jid)+'/reducer/out')
    os.makedirs(chunk_dir, exist_ok=True)
    os.makedirs(reducer_in, exist_ok=True)
    os.makedirs(reducer_out, exist_ok=True)

    
    # read the entire file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    chunk = []
    chunk_index = 0
    chunk_size_current = 0
    
    for line in lines:
        chunk.append(line)
        chunk_size_current += len(line.encode('utf-8'))
        if chunk_size_current >= chunk_size:
            chunk_file_path = os.path.join(chunk_dir, f'mapper-{chunk_index}.in')
            with open(chunk_file_path, 'w') as chunk_file:
                chunk_file.writelines(chunk)
            chunk = []
            chunk_size_current = 0
            chunk_index += 1
    
    if chunk:
        chunk_file_path = os.path.join(chunk_dir, f'mapper-{chunk_index}.in')
        with open(chunk_file_path, 'w') as chunk_file:
            chunk_file.writelines(chunk)


def prepare_shuffling_data(jid):
    pass

def cleanUp_pv(jid, path):
    
    for root, d_names, f_names in os.walk(path):
        print(root, d_names, f_names)











