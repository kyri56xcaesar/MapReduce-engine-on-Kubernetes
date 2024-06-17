from time import sleep
from .kube_utils import *
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from kubernetes import client, config
from kubernetes.client import V1EnvVar, V1ObjectMeta, V1PodSpec, V1PodTemplateSpec, V1VolumeMount, V1Volume, V1PersistentVolumeClaimVolumeSource
from kubernetes.client import V1Container, V1JobSpec, V1Job



def init_images():
  docker_ize_templated("Dockerfile.mapper", "mapper", "skeletons/mapper_skeleton.py", ".")
  docker_ize_templated("Dockerfile.reducer", "reducer", "skeletons/reducer_skeleton.py", ".")

  load_images_to_minikube()


def create_and_apply_mapper_Job_manifest(jid, myfunc, no_mappers):
    # Load kube config from outside
    #config.load_kube_config()
    # load kube config from within
    config.load_incluster_config()

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
        backoff_limit_per_index=4,
        template=client.V1PodTemplateSpec(
            
            metadata=client.V1ObjectMeta(labels={"app": "mappers", "job-name": "mapper-job"}),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="mapreduce",
                        image="mapper:latest",
                        image_pull_policy="IfNotPresent",
                        command=[
                            "sh", "-c",
                            'echo ${MYFUNC} > /mapper_input.py && echo ${JOB_COMPLETION_INDEX} && python3 /mapper_skeleton.py -i /mnt/data/'+str(jid)+'/mapper/in/mapper-${JOB_COMPLETION_INDEX}.in -o /mnt/data/'+str(jid)+'/reducer/in/mapper-${JOB_COMPLETION_INDEX}.out'
                        ],
                        ports=[client.V1ContainerPort(container_port=8080, name="mapper")],
                        volume_mounts=[
                            client.V1VolumeMount(
                                mount_path="/mnt/data/",
                                name="manager-storage"
                            )
                        ],
                        env=[
                            client.V1EnvVar(
                                name="MYFUNC",
                                value=myfunc
                            )
                        ]
                    )
                ],
                restart_policy="OnFailure",
                volumes=[
                    client.V1Volume(
                        name="manager-storage",
                        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                            claim_name="keep-alive-pod-pvc"
                        )
                    )
                ]
            )
        )
    )
)
    
    #Create the job in the Kubernetes cluster
    api_instance = client.BatchV1Api()
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default"
    )
    print("Job created. status='%s'" % str(api_response.status))


def create_and_apply_reducer_Job_manifest(jid, myfunc, no_mapper):
    
    # Load kube config from outside
    #config.load_kube_config()
    # load kube config from within
    config.load_incluster_config()
    
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
                                'echo "${MYFUNC}" > /reducer_input.py && python3 /reducer_skeleton.py -i /mnt/data/'+str(jid)+'/reducer/in/mapper-${JOB_COMPLETION_INDEX}.out -o /mnt/data/'+str(jid)+'/reducer/out/reducer-${JOB_COMPLETION_INDEX}.out'
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


def get_job_status(JOB_NAME):
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()
    
    job_completed = False
    while not job_completed:
        api_response = batch_v1.read_namespaced_job_status(
            name=JOB_NAME,
            namespace="default")
        if api_response.status.succeeded is not None or \
                api_response.status.failed is not None:
            job_completed = True
        sleep(1)
        print(f"Job status='{str(api_response.status)}'")




def kube_client_main(jid, filepath, mapper, reducer):
    
    
    
    #relative_path = os.path.join('examples', filepath)
    filepath = "kube/examples/" + filepath

    fsize = get_file_size(filepath)
    no_workers = estimate_num_mappers(fsize)
  
    print(f'File size: {fsize}')
    print(f'# workers: {no_workers}')
  

    # This should split the files in the /mnt path
    split_datafile(filepath, jid)
      
      
    
  
    # USE KUBERNETES PY CLIENT for manifest setup and application
    create_and_apply_mapper_Job_manifest(jid, mapper, no_workers)
    
    
    # need to wait for map job to complete.    
    #get_job_status("mapper-job")
    
    #create_and_apply_reducer_Job_manifest(jid, reducer, 1)
    
    # Save output only and cleanup.
    
    return 0
  

