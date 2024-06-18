import glob, json
from math import ceil
from time import sleep
from .kube_utils import *
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from kubernetes import client, config
from kubernetes.client import V1EnvVar, V1ObjectMeta, V1PodSpec, V1PodTemplateSpec, V1VolumeMount, V1Volume, V1PersistentVolumeClaimVolumeSource
from kubernetes.client import V1Container, V1JobSpec, V1Job

batch_v1 = client.BatchV1Api()
namespace = 'default'


def create_and_apply_mapper_Job_manifest(jid, myfunc, no_mappers):

    # Load kube config from outside
    #config.load_kube_config()
    # load kube config from within
    config.load_incluster_config()
    
    jid = str(jid)
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
                            'echo ${MYFUNC} > /mapper_input.py && echo ${JOB_COMPLETION_INDEX} && python3 /mapper_skeleton.py -i /mnt/data/'+jid+'/mapper/in/mapper-${JOB_COMPLETION_INDEX}.in -o /mnt/data/'+jid+'/shuffler/in/mapper-${JOB_COMPLETION_INDEX}.out'
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
    return api_response


def create_and_apply_reducer_Job_manifest(jid, myfunc, no_reducers):
    
    # Load kube config from outside
    #config.load_kube_config()
    # load kube config from within
    config.load_incluster_config()
    
    jid = str(jid)
    
    # Create the Job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name="reducer-job"),
        spec=client.V1JobSpec(
            completions=no_reducers,  # Total number of reducer jobs to complete
            parallelism=no_reducers,  # Number of reducer jobs to run in parallel
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
                                'echo "${MYFUNC}" > /reducer_input.py && python3 /reducer_skeleton.py -i /mnt/data/'+jid+'/reducer/in/shuffler-${JOB_COMPLETION_INDEX}.out -o /mnt/data/'+jid+'/reducer/out/reducer-${JOB_COMPLETION_INDEX}.out'
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
    return api_response


def check_job_status(jid, namespace):
    try:
        # List all the jobs in the specified namespace
        jobs = batch_v1.list_namespaced_job(namespace)
        for job in jobs.items:
            job_name = job.metadata.name
            # Check if the job name ends with the specified jid
            if job_name.startswith(f"{jid}-"):
                status = job.status
                if status.succeeded:
                    print(f"Job '{job_name}' has completed successfully.")
                elif status.failed:
                    print(f"Job '{job_name}' has failed.")
                else:
                    print(f"Job '{job_name}' is still running.")
                return
        print(f"No job found with jid '-{jid}' in namespace '{namespace}'")
    except ApiException as e:
        print(f"Exception when calling BatchV1Api->list_namespaced_job: {e}")



def wait_for_mapper_jobs(namespace, jid, no_workers):
    for _ in range(300):  # Try for a reasonable number of times, e.g., 5 minutes if checking every second
        all_completed = True
        for i in range(no_workers):
            job_name = f"mapper-{jid}-{i}"
            if not check_job_status(namespace, job_name):
                all_completed = False
                break
        if all_completed:
            return True
        sleep(1)  # Sleep for a second before the next check
    return False


def kube_client_main(jid, filepath, mapper, reducer):
    
    # Load kube config from outside
    #config.load_kube_config()
    # load kube config from within
    config.load_incluster_config()

    jid = str(jid)
    #relative_path = os.path.join('examples', filepath)
    filepath = "kube/examples/" + filepath

    fsize = get_file_size(filepath)
    no_workers = estimate_num_mappers(fsize)
  
    print(f'File size: {fsize}')
    print(f'# workers: {no_workers}')
  

    # this should split the files in the /mnt path
    # create directories in the PV for the given JID
    split_datafile(filepath, jid)
      
    # apply THE MAPPERS job
    create_and_apply_mapper_Job_manifest(jid, mapper, no_workers)
    
    
    # need to wait for map job to complete.    
    all_mappers_completed = wait_for_mapper_jobs(namespace, jid, no_workers)
    if not all_mappers_completed:
        print("One or more mapper jobs failed. Exiting.")
        return 1
    
    # preprocess the mapped data to prepare shuffling
    # apply SHUFFLE 
    input_path = "/mnt/data/"+jid+"/shuffler/in/mapper-*.out"
    output_path = "mnt/data/"+jid+"/reducer/in/"

    mapped_files = glob.glob(input_path)

    shuffled_data = {}

    for file_path in mapped_files:
        file_name = os.path.basename(file_path)
        print(file_name)
        
        with open(file_path) as f:
            data = json.load(f)
            for key, value in data.items():
                if key not in shuffled_data:
                    shuffled_data[key] = value
                else:
                    shuffled_data[key].extend(value)
            
    # prepare and estimate reducers
    keys = list(shuffled_data.keys())
    no_reducers = ceil(len(keys) / no_workers)
    
    keys_per_reducer = ceil(len(keys) / no_reducers)
    
    for i in range(no_reducers):
        reducer_data = {}
        start_index = i * keys_per_reducer
        end_index = min((i + 1) * keys_per_reducer, len(keys))
        
        for key in keys[start_index:end_index]:
            reducer_data[key] = shuffled_data[key]
            
        reducer_file_path = os.path.join(output_path, f"reducer-{i}.in")
        with open(reducer_file_path, 'w') as out:
            json.dump(reducer_data, out, indent=1, ensure_ascii=False)
        

    
            
            
    # apply the SHUFFLE job
    
    # apply the SHUFFLE job
    
    # apply the REDUCERS job
    create_and_apply_reducer_Job_manifest(jid, reducer, no_reducers)    
    
    
    # save output only and cleanup.
    # cleanup pv with given jid
    #cleanUp_pv(jid)
     
    return 0
  

