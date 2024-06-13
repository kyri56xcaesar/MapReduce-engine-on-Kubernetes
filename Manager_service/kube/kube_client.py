import subprocess
from kube_utils import *



def apply_manifest(manifest_path):
  subprocess.run(["kubectl", "apply", "-f", manifest_path])



def main():
  filepath = "../examples/word_count_data.txt"
  fsize = get_file_size(filepath)
  no_mappers = estimate_num_mappers(fsize)
  
  print(f'File size: {fsize}')
  print(f'# workers: {no_mappers}')
  
  #split_file("word_count_data.txt", 128)
  
  #prepare_py_mapper(mapper_file_path="../examples/mapper_example.py", input_data_path="../examples/word_count_data.txt", output_data_path="test.out")
  prepare_py_reducer("../examples/reducer_example.py", "test.out", "out.out")
  # check if chunks are created
  # for ch in range(no_mappers):
  #   print(os.path.exists(f"data/chunk_{ch}.txt"))
  
 
  
  

main()





