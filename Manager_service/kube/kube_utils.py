import os

# Utils for determening how big the data is
# set a chuck size of a dataset file to be at 64 MB
#CHUNK_SIZE = 54 * 1024 * 1024 # 64 MB
CHUNK_SIZE = 128 # 128 bytes for testing


# return the size of a file in bytes
def get_file_size(file_path):
    return os.path.getsize(file_path)

# according to the default chuck size, estimate how many mappers should be used.
def estimate_num_mappers(file_size, chunk_size=CHUNK_SIZE):
    return file_size // chunk_size + (1 if file_size % chunk_size > 0 else 0)

# split a given file to chucks so that they can be used for different workers
def split_file(file_path, chunk_size=64*1024*1024):
    # check if the directory exists
    chunk_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(chunk_dir, exist_ok=True)
    
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
            chunk_file_path = os.path.join(chunk_dir, f'chunk_{chunk_index}.txt')
            with open(chunk_file_path, 'w') as chunk_file:
                chunk_file.writelines(chunk)
            chunk = []
            chunk_size_current = 0
            chunk_index += 1
    
    if chunk:
        chunk_file_path = os.path.join(chunk_dir, f'chunk_{chunk_index}.txt')
        with open(chunk_file_path, 'w') as chunk_file:
            chunk_file.writelines(chunk)



# Templates and formatting
# template paths
MAPPER_TEMPLATE_PATH = "templates/py_mappersource_extention.template"
REDUCER_TEMPLATE_PATH = "templates/py_reducersource_extention.template"
DOCKERFILE_TEMPLATE_PATH = "templates/Dockerfile.py.template"

def prepare_py_mapper(mapper_file_path="examples/mapper_example.py", input_data_path ="", output_data_path=""):
    
    
    mapper_additions_path = MAPPER_TEMPLATE_PATH
    mapper_additions = ""
    with open(mapper_additions_path, 'r') as f:
        mapper_additions = f.read()
        
        formatted_mapper = mapper_additions.format(input_data_path=input_data_path, output_data_path=output_data_path)
        
        with open(mapper_file_path, 'a') as mapper_file:
            mapper_file.write(formatted_mapper)

def prepare_py_reducer(reducer_file_path="examples/reducer_example.py", input_data_path ="", output_data_path=""):
    
    
    reducer_additions_path = REDUCER_TEMPLATE_PATH
    reducer_additions = ""
    with open(reducer_additions_path, 'r') as f:
        reducer_additions = f.read()
        
        formatted_reducer = reducer_additions.format(input_data_path=input_data_path, output_data_path=output_data_path)
        
        with open(reducer_file_path, 'a') as reducer_file:
            reducer_file.write(formatted_reducer)       

def prepare_dockerfile(dockerfile_name, py_source_path):
    
    dockerfile_template = DOCKERFILE_TEMPLATE_PATH
    script_file = py_source_path.split("/")[-1]
    
    with open(dockerfile_template, 'r') as template:
        
        content = template.read()
        
        formatted_content = content.format(script_path=py_source_path, script_name=script_file)
        
        with open(dockerfile_name, 'w') as f_out:
            f_out.write(formatted_content)
    


def create_dockerFile(source_name, docker_name):
    pass

def docker_ize(python_source_file, ):
    pass



# import os

# def create_dockerfile(script_name, script_content, dockerfile_name):
#     with open(script_name, 'w') as script_file:
#         script_file.write(script_content)
    
#     dockerfile_content = f"""
#     FROM python:3.9-slim
#     COPY {script_name} /{script_name}
#     ENTRYPOINT ["python", "/{script_name}"]
#     """
    
#     with open(dockerfile_name, 'w') as dockerfile:
#         dockerfile.write(dockerfile_content)
