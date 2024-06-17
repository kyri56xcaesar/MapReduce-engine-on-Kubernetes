import subprocess
import time
from kubernetes import config, client, utils

subprocess.run(["minikube", "start", "--vm-driver=docker"])
time.sleep(5)

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


subprocess.run(["docker", "build", "-t", "manager", "-f", "Manager_service/Dockerfile.manager", "Manager_service/"])

docker_ize_templated("Dockerfile.mapper", "mapper", "Manager_service/kube/skeletons/mapper_skeleton.py", ".")
docker_ize_templated("Dockerfile.reducer", "reducer", "Manager_service/kube/skeletons/reducer_skeleton.py", ".")

# need to create image for Manager

time.sleep(10)

subprocess.run(["minikube", "image", "load", "mapper"])
subprocess.run(["minikube", "image", "load", "reducer"])

# need to load image for manager
subprocess.run(["minikube", "image", "load", "manager"])



time.sleep(15)


# apply manifests
config.load_kube_config()
k8s_client = client.ApiClient()
yaml_file = './manager-manifest.yaml'
utils.create_from_yaml(k8s_client,yaml_file,verbose=True)


