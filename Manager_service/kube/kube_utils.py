import os, subprocess, json


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
CHUNK_SIZE = 1024 * 128# 2048 bytes for testing


# return the size of a file in bytes
def get_file_size(file_path):
    return os.path.getsize(file_path)

# split a given file to chucks so that they can be used for different workers
def split_datafile(file_path, jid, chunk_size=CHUNK_SIZE):
    # check if the directory exists
    chunk_dir = os.path.join(os.getcwd(), 'mnt/data/'+str(jid)+'/mapper/in')
    reducer_in = os.path.join(os.getcwd(), 'mnt/data/'+str(jid)+'/reducer/in')
    reducer_out = os.path.join(os.getcwd(), 'mnt/data/'+str(jid)+'/reducer/out')
    shuffler_out = os.path.join(os.getcwd(), 'mnt/data/'+str(jid)+'/shuffler/in')
    os.makedirs(chunk_dir, exist_ok=True)
    os.makedirs(reducer_in, exist_ok=True)
    os.makedirs(reducer_out, exist_ok=True)
    os.makedirs(shuffler_out, exist_ok=True)

    
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
    
    return chunk_index


def cleanUp_pv(jid):
    
    subprocess.run(["rm", "-rf", "/mnt/data/"+str(jid)+"/mapper"])
    subprocess.run(["rm", "-rf", "/mnt/data/"+str(jid)+"/shuffler"])
    subprocess.run(["rm", "-rf", "/mnt/data/"+str(jid)+"/reducer/in"])
    


def concatenate_json_objects(input_file, output_file):
    combined_data = {}

    with open(input_file, 'r') as file:
        for line in output_file:
            # Strip leading/trailing whitespace and check if line is not empty
            line = line.strip()
            if line:
                # Parse the JSON object
                data = json.loads(line)
                # Update the combined dictionary with the current data
                combined_data.update(data)
    
    # Write the combined dictionary to the output file
    with open(output_file, 'w') as out_file:
        json.dump(combined_data, out_file, indent=4)








