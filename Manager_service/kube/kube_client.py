import yaml
import time
from kube_utils import *
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

# load config
config.load_kube_config()


def init_images():
  docker_ize("Dockerfile.mapper", "mapper", "skeletons/mapper_skeleton.py", ".")
  docker_ize("Dockerfile.reducer", "reducer", "skeletons/reducer_skeleton.py", ".")
  docker_ize("Dockerfile.shuffler", "shuffler", "skeletons/shuffler.py", ".")

  load_images_to_minikube()


def apply_sfs_manifest(yaml_file):
    # Load in-cluster config
    config.load_incluster_config()
    # Use this if running outside of the cluster
    # config.load_kube_config()

    # Read the YAML file
    with open(yaml_file, 'r') as f:
        manifest = list(yaml.safe_load_all(f))

    # Apply each resource in the manifest
    for resource in manifest:
        kind = resource.get('kind')
        if kind == 'PersistentVolume':
            try:
                client.CoreV1Api().create_persistent_volume(body=resource)
                print("PersistentVolume created successfully.")
            except ApiException as e:
                if e.status == 409:
                    print("PersistentVolume already exists. Skipping creation.")
                else:
                    print("Exception when creating PersistentVolume: %s\n" % e)

        elif kind == 'PersistentVolumeClaim':
            try:
                client.CoreV1Api().create_namespaced_persistent_volume_claim(namespace='default', body=resource)
                print("PersistentVolumeClaim created successfully.")
            except ApiException as e:
                if e.status == 409:
                    print("PersistentVolumeClaim already exists. Skipping creation.")
                else:
                    print("Exception when creating PersistentVolumeClaim: %s\n" % e)

        elif kind == 'Pod':
            try:
                client.CoreV1Api().create_namespaced_pod(namespace='default', body=resource)
                print("Pod created successfully.")
            except ApiException as e:
                if e.status == 409:
                    print("Pod already exists. Skipping creation.")
                else:
                    print("Exception when creating Pod: %s\n" % e)


def apply_k8s_worker_manifest(manifest: str):
    # Load Kubernetes configuration
    config.load_kube_config()

    # Parse the manifest
    k8s_objects = yaml.safe_load_all(manifest)

    # Initialize the API clients
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    # Apply each object in the manifest
    for obj in k8s_objects:
        kind = obj.get('kind')
        if kind == 'Service':
            try:
                v1.create_namespaced_service(namespace='default', body=obj)
                print(f"Service '{obj['metadata']['name']}' created successfully.")
            except ApiException as e:
                if e.status == 409:
                    v1.replace_namespaced_service(name=obj['metadata']['name'], namespace='default', body=obj)
                    print(f"Service '{obj['metadata']['name']}' updated successfully.")
                else:
                    print(f"Failed to create or update Service: {e}")

        elif kind == 'StatefulSet':
            try:
                apps_v1.create_namespaced_stateful_set(namespace='default', body=obj)
                print(f"StatefulSet '{obj['metadata']['name']}' created successfully.")
            except ApiException as e:
                if e.status == 409:
                    apps_v1.replace_namespaced_stateful_set(name=obj['metadata']['name'], namespace='default', body=obj)
                    print(f"StatefulSet '{obj['metadata']['name']}' updated successfully.")
                else:
                    print(f"Failed to create or update StatefulSet: {e}")


def wait_for_pod(pod_name, namespace='default', timeout=300):
    v1 = client.CoreV1Api()
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            if pod.status.phase == 'Running':
                print(f"Pod {pod_name} is running.")
                return True
        except ApiException as e:
            print(f"Exception when reading pod status: {e}")
        time.sleep(5)
    print(f"Timeout waiting for pod {pod_name} to be running.")
    return False

def setup_data():
  
  # need to copy data to the persistent volume
  # insert the user functions
  pass
  
  


def main():
  filepath = "examples/word_count_data.txt"
  fsize = get_file_size(filepath)
  no_workers = estimate_num_mappers(fsize)
  
  print(f'File size: {fsize}')
  print(f'# workers: {no_workers}')
  
  
  
  
  
  
  #split_datafile("examples/word_count_data.txt", 128)
  
  # check if chunks are created
  # for ch in range(no_mappers):
  #   print(os.path.exists(f"data/chunk_{ch}.txt"))
  
  #prepare_py_mapper(mapper_file_path="examples/mapper_skeleton.py", input_data_path="examples/word_count_data.txt", output_data_path="mapper.out")
  #prepare_dockerfile("Dockerfile.mapper", "examples/mapper_skeleton.py")
  
  #prepare_py_reducer("/examples/reducer_example.py", "test.out", "out.out")
  
  
  # USE KUBERNETES PY CLIENT for manifest setup and application
  
  
  return 0
  
 
  
  

main()





