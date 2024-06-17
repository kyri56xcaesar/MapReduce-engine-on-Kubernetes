import yaml
from kube_utils import *
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from kubernetes import client, config
from kubernetes.client import V1EnvVar, V1ObjectMeta, V1PodSpec, V1PodTemplateSpec, V1VolumeMount, V1Volume, V1PersistentVolumeClaimVolumeSource
from kubernetes.client import V1Container, V1JobSpec, V1Job



def init_images():
  docker_ize("Dockerfile.mapper", "mapper", "skeletons/mapper_skeleton.py", ".")
  docker_ize("Dockerfile.reducer", "reducer", "skeletons/reducer_skeleton.py", ".")
  docker_ize("Dockerfile.shuffler", "shuffler", "skeletons/shuffler.py", ".")

  load_images_to_minikube()


def create_and_apply_mapper_Job_manifest(myfunc, no_mappers):
    # Load kube config
    config.load_kube_config()

    #if no_mappers < 0 or no_mappers > 10:
    #    return

   # Create the Job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name="mapper-job"),
        spec=client.V1JobSpec(
            completions=no_mappers,  # Total number of mapper jobs to complete
            parallelism=no_mappers,  # Number of mapper jobs to run in parallel
            completion_mode="Indexed",
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "mappers"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="mapreduce",
                            image="mapper:latest",
                            image_pull_policy="IfNotPresent",
                            command=[
                                "sh", "-c",
                                'echo "${MYFUNC}" > /mapper_input.py && python3 /mapper_skeleton.py -i /mnt/data/mapper/in/mapper-${JOB_INDEX}.in -o /mnt/data/shuffler/in/mapper-${JOB_INDEX}.out'
                            ],
                            ports=[client.V1ContainerPort(container_port=8080, name="mapper")],
                            volume_mounts=[
                                client.V1VolumeMount(
                                    mount_path="/mnt/data/",
                                    name="mapper-storage"
                                )
                            ],
                            env=[
                                V1EnvVar(
                                    name="JOB_INDEX",
                                    value_from=client.V1EnvVarSource(
                                        field_ref=client.V1ObjectFieldSelector(field_path='metadata.annotations["batch.kubernetes.io/job-completion-index"]')
                                    )
                                ),
                                V1EnvVar(
                                    name="MYFUNC",
                                    value=myfunc
                                )
                            ]
                        )
                    ],
                    restart_policy="OnFailure",
                    volumes=[
                        client.V1Volume(
                            name="mapper-storage",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name="keep-alive-pod-pvc"
                            )
                        )
                    ]
                )
            )
        )
    )

    # Create the job in the Kubernetes cluster
    api_instance = client.BatchV1Api()
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default"
    )
    print("Job created. status='%s'" % str(api_response.status))


def create_and_apply_reducer_Job_manifest(myfunc, no_mapper):
    
    config.load_kube_config()
    
    # Create the Job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name="reducer-job"),
        spec=client.V1JobSpec(
            completions=no_mapper,  # Total number of reducer jobs to complete
            parallelism=no_mapper,  # Number of reducer jobs to run in parallel
            completion_mode="Indexed",
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "reducers"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="mapreduce",
                            image="reducer:latest",
                            image_pull_policy="IfNotPresent",
                            command=[
                                "sh", "-c",
                                'echo "${MYFUNC}" > /reducer_input.py && python3 /reducer_skeleton.py -i /mnt/data/reducer/in/mapper-${JOB_INDEX}.out -o /mnt/data/reducer/out/reducer-${JOB_INDEX}.out'
                            ],
                            ports=[client.V1ContainerPort(container_port=8081, name="reducer")],
                            volume_mounts=[
                                client.V1VolumeMount(
                                    mount_path="/mnt/data/",
                                    name="reducer-storage"
                                )
                            ],
                            env=[
                                V1EnvVar(
                                    name="JOB_INDEX",
                                    value_from=client.V1EnvVarSource(
                                        field_ref=client.V1ObjectFieldSelector(field_path='metadata.annotations["batch.kubernetes.io/job-completion-index"]')
                                    )
                                ),
                                V1EnvVar(
                                    name="MYFUNC",
                                    value=myfunc
                                )
                            ]
                        )
                    ],
                    restart_policy="OnFailure",
                    volumes=[
                        client.V1Volume(
                            name="reducer-storage",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name="keep-alive-pod-pvc"
                            )
                        )
                    ]
                )
            )
        )
    )

    # Create the job in the Kubernetes cluster
    api_instance = client.BatchV1Api()
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default"
    )




def main():
    
    filepath = "examples/word_count_data.txt"
    fsize = get_file_size(filepath)
    no_workers = estimate_num_mappers(fsize)
  
    print(f'File size: {fsize}')
    print(f'# workers: {no_workers}')
  
    
    # This should split the files in the /mnt path
    split_datafile(filepath)
      
    mapper_func = """
    def reducer(entries):
      accumulator = dict()
      for key, value in entries.items():
          if key in accumulator:
              accumulator[key] += sum(value)
          else:
              accumulator[key] = sum(value)
      return accumulator
    """
    reducer_func = """
      def mapper(arr):
          return [(word, 1) for word in arr]
    """
  
    # USE KUBERNETES PY CLIENT for manifest setup and application
    create_and_apply_mapper_Job_manifest(mapper_func, no_workers)
    create_and_apply_reducer_Job_manifest(reducer_func, 1)
    
    return 0
  

main()


