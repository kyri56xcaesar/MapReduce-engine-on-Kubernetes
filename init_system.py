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

    docker_ize_templated("Manager_service/Dockerfile.mapper", "mapper", "Manager_service/kube/skeletons/mapper_skeleton.py", ".")
    docker_ize_templated("Manager_service/Dockerfile.reducer", "reducer", "Manager_service/kube/skeletons/reducer_skeleton.py", ".")
    
    subprocess.run(["docker", "build", "-t", "manager", "-f", "Manager_service/Dockerfile.manager", "Manager_service/"])

    time.sleep(10)

    # need to create image for Manager

def load_images_to_minikube():

    subprocess.run(["minikube", "image", "load", "mapper"])
    subprocess.run(["minikube", "image", "load", "reducer"])

    # need to load image for manager
    subprocess.run(["minikube", "image", "load", "manager"])

    time.sleep(15)




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
    
    
    
    # start_minikube()
    
    #apply manifests
    config.load_kube_config()
    k8s_client = client.ApiClient()
    yaml_file = 'manifests/manager-manifest.yaml'
    namespace = 'default'
    pattern = r'^manager-\d+$'
    manager_pod_name = 'manager'
    core_v1 = client.CoreV1Api()

    
    
    # build_images()
    # load_images_to_minikube()
    # apply_manifests(k8s_client, yaml_file)
    
    time.sleep(4)
    
    
    pods = get_matching_pods(core_v1, namespace, pattern)
    
    print(pods)
    
    for pod in pods:
        pod_ip = get_pod_ip(core_v1, namespace, pod)
        print(pod_ip)
    


    


