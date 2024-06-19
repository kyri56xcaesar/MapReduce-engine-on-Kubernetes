import subprocess
import time
import re
from kubernetes import config, client, utils
from kubernetes.client.rest import ApiException


def build_images():

    subprocess.run(["docker", "rmi", "manager"])

    subprocess.run(["docker", "build", "-t", "manager", "-f", "Manager_service/Dockerfile.manager", "Manager_service/"])

    time.sleep(10)

    # need to create image for Manager

def delete_manager(yaml):
    subprocess.run(["kubectl", "delete", "-f", yaml])


def apply_manifests(k8s_client, yaml_file):
    # manager manifest
    utils.create_from_yaml(k8s_client, yaml_file,verbose=True)


def get_matching_pods(core_v1, namespace, pattern):
    try:
        # List all the pods in the specified namespace
        pods = core_v1.list_namespaced_pod(namespace)
        matching_pods = []
        for pod in pods.items:
            pod_name = pod.metadata.name
            # Check if the pod name matches the pattern
            if re.match(pattern, pod_name):
                matching_pods.append(pod_name)
        return matching_pods
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")
        return None    
    
def get_pod_ip(core_v1, namespace, pod_name):
    try:
        # Get the details of the specified pod
        pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        # Extract the pod's IP address
        pod_ip = pod.status.pod_ip
        return pod_ip
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->read_namespaced_pod: {e}")
        return None



# This main should boot up everything

if __name__ == "__main__":

    
    #apply manifests
    config.load_kube_config()
    k8s_client = client.ApiClient()
    yaml_file = 'manifests/manager-manifest.yaml'
    namespace = 'default'
    pattern = r'^manager-\d+$'
    manager_pod_name = 'manager'
    core_v1 = client.CoreV1Api()

    
    delete_manager(yaml_file)
    build_images()
    apply_manifests(k8s_client, yaml_file)

    time.sleep(4)
    
    
    pods = get_matching_pods(core_v1, namespace, pattern)
    
    print(pods)
    
    for pod in pods:
        pod_ip = get_pod_ip(core_v1, namespace, pod)
        print(pod_ip)
    

    


