import subprocess
import time
import re
from kubernetes import config, client, utils
from kubernetes.client.rest import ApiException

def docker_ize_templated(dockerfile_name, image_name, py_skeleton_path, curr_path):
    
    DOCKERFILE_TEMPLATE_PATH = "Manager_service/kube/templates/Dockerfile.py.template"

    dockerfile_template = DOCKERFILE_TEMPLATE_PATH
    
    with open(dockerfile_template, 'r') as template:
        
        script = py_skeleton_path.split("/")[-1]
        
        content = template.read()
        
        formatted_content = content.format(skeleton_script_path=py_skeleton_path, skeleton_script=script)
        
        with open(dockerfile_name, 'w') as f_out:
            f_out.write(formatted_content)

    subprocess.run(["docker", "build", "-t", image_name, "-f", dockerfile_name, curr_path])
    
def start_minikube():

    subprocess.run(["minikube", "start", "--vm-driver=docker"])
    time.sleep(5)

def build_images():
    # Manager Jobs images
    docker_ize_templated("Manager_service/Dockerfile.mapper", "mapper", "Manager_service/kube/skeletons/mapper_skeleton.py", ".")
    docker_ize_templated("Manager_service/Dockerfile.reducer", "reducer", "Manager_service/kube/skeletons/reducer_skeleton.py", ".")
    
    # Manager himself
    subprocess.run(["docker", "build", "-t", "manager", "-f", "Manager_service/Dockerfile.manager", "Manager_service/"])

    # UI
    subprocess.run(["docker", "build", "-t", "uiservice:v1", "-f", "UI_service/Dockerfile", "UI_service/"])
    
    # Auth
    subprocess.run(["docker", "build", "-t", "authservice:v1", "-f", "Auth_service/Dockerfile", "Auth_service/"])
    
    time.sleep(10)

def load_all_images_to_minikube():
    load_image_to_minikube("mapper", 3)
    
    load_image_to_minikube("reducer", 3)
    
    load_image_to_minikube("uiservice:v1", 5)
    
    load_image_to_minikube("authservice:v1", 5)
    
    load_image_to_minikube("manager", 10)

def load_image_to_minikube(image_name, time_to_sleep):
    # Load the images to the minikube node
    # optional if running out of minikube environment
    subprocess.run(["minikube", "image", "load", image_name])

    time.sleep(time_to_sleep)

def delete_many_manifessts(manifest_list):
    for manifest in manifest_list:
        subprocess.run(["kubectl", "delete", "-f", manifest])

def apply_many_manifests(k8s_client, manifest_list):
    for manifest in manifest_list:
        apply_manifest(k8s_client, manifest)
        
def apply_manifest(k8s_client, yaml_file):
    # manager manifest
    utils.create_from_yaml(k8s_client=k8s_client, yaml_file=yaml_file, verbose=True)

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
    
    #start_minikube()
    
    
    config.load_kube_config()
    k8s_client = client.ApiClient()
    core_v1 = client.CoreV1Api()
    namespace = 'default'
    
    manifests = ['manifests/etcd-manifest.yaml', 'manifests/manager-manifest.yaml', 'manifests/ui-auth-manifest.yaml']
    manager_pod_name = 'manager'


    #delete_many_manifessts(manifest_list=manifests)

    # perhaps switch to minikube environment?
    build_images()
    #load_images_to_minikube()
    apply_many_manifests(k8s_client, manifests)
    #apply_manifest(k8s_client, "manifests/ui-auth-manifest.yaml")
    
    time.sleep(4)
   
    pattern = r'^manager-\d+$'
    pods = get_matching_pods(core_v1, namespace, pattern)
    
    print(pods)
    
    for pod in pods:
        pod_ip = get_pod_ip(core_v1, namespace, pod)
        print(pod_ip)