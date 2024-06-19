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


def apply_manifests(k8s_client, yaml_file):
    # manager manifest
    utils.create_from_yaml(k8s_client, yaml_file,verbose=True)


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

    
    build_images()
    apply_manifests(k8s_client, yaml_file)


    


