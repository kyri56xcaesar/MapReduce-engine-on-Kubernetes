import json
from math import ceil
from .kube_utils import *
import logging
from time import sleep
from kubernetes import client, config
from kubernetes import client, config, watch
from kubernetes.client import V1EnvVar

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mapper_image = "mapper:latest"
reducer_image = "reducer:latest"
namespace='default'

def create_and_apply_mapper_Job_manifest(api_instance, jid, mymapfunc, myreducefunc , no_mappers):

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
    metadata=client.V1ObjectMeta(name="mapper-job"+jid),
    spec=client.V1JobSpec(
        completions=no_mappers,  # Total number of mapper jobs to complete
        parallelism=no_mappers,  # Number of mapper jobs to run in parallel
        completion_mode="Indexed",
        backoff_limit_per_index=3,
        template=client.V1PodTemplateSpec(          
            metadata=client.V1ObjectMeta(labels={"app": "mappers", "job-name": "mapper-job"+jid}),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="mapreduce",
                        image=mapper_image,
                        image_pull_policy="IfNotPresent",
                        command=[
                            "sh", "-c",
                            #'echo ${MYREDUCEFUNC} > /reducer_input.py',
                            'echo ${MYMAPFUNC} > /mapper_input.py && python3 /mapper_skeleton.py -i /mnt/data/'+jid+'/mapper/in/mapper-${JOB_COMPLETION_INDEX}.in -o /mnt/data/'+jid+'/shuffler/in/mapper-${JOB_COMPLETION_INDEX}.out'
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
                                name="MYMAPFUNC",
                                value=mymapfunc                               
                            ),
                            client.V1EnvVar(
                                name="MYREDUCEFUNC",
                                value=myreducefunc                               
                            )
                        ]
                    )
                ],
                restart_policy="Never",
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
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace=namespace
    )
    return api_response

def create_and_apply_reducer_Job_manifest(api_instance, jid, myfunc, no_reducers):
    
    # Load kube config from outside
    #config.load_kube_config()
    # load kube config from within
    config.load_incluster_config()
    
    jid = str(jid)
    
    # Create the Job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name="reducer-job"+jid),
        spec=client.V1JobSpec(
            completions=no_reducers,  # Total number of reducer jobs to complete
            parallelism=no_reducers,  # Number of reducer jobs to run in parallel
            completion_mode="Indexed",
            backoff_limit_per_index=3,
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "reducers"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="mapreduce",
                            image=reducer_image,
                            image_pull_policy="IfNotPresent",
                            command=[
                                "sh", "-c",
                                'echo "${MYFUNC}" > /reducer_input.py && python3 /reducer_skeleton.py -i /mnt/data/'+jid+'/reducer/in/reducer-${JOB_COMPLETION_INDEX}.in -o /mnt/data/'+jid+'/reducer/out/reducer-${JOB_COMPLETION_INDEX}.out'
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
                    restart_policy="Never",
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
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace=namespace
    )
    return api_response

def wait_for_job_done(job_name, namespace):
    
    api_instance = client.BatchV1Api()

    w = watch.Watch()
    for event in w.stream(api_instance.list_namespaced_job, namespace=namespace, timeout_seconds=0):
        job = event['object']
        if job.metadata.name == job_name:
            if job.status.succeeded is not None and job.status.succeeded >= job.spec.completions:
                logger.info(f"Job {job.metadata.name} completed.")
                w.stop()
                return True               
            elif job.status.failed is not None and job.status.failed >= job.spec.backoff_limit_per_index:
                logger.info(f"Job {job.metadata.name} failed.")
                w.stop()
                return False
            
def check_job_status(job_name, namespace):
    
    api_instance = client.BatchV1Api()
    thread = api_instance.list_namespaced_job(namespace, async_req=True)
    joblist = thread.get()
    
    logger.info(joblist)
    
    for job in joblist.items:
        if job.metadata.name == job_name:
            job_status = job.status
            logger.info(f"Job {job_name} status: {job_status}")

            return job_status
    
    logger.info(f"Job {job_name} not found in namespace {namespace}.")
    return None
           
           
def delete_job(api_instance, job_name):
    api_response = api_instance.delete_namespaced_job(
        name=job_name,
        namespace=namespace,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    logger.info(f"Job deleted. status='{str(api_response.status)}'")             
                
def kube_client_main(jid, filepath, mapper, reducer):
    
    # Load kube config from outside
    #config.load_kube_config()
    # load kube config from within
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()


    jid = str(jid)
    #filepath = os.path.join(os.getcwd(), 'examples/', filepath)
    
    filepath = "kube/examples/" + filepath
    logger.info(f'FILEPATH: {filepath}')


    # this should split the files in the /mnt path
    # create directories in the PV for the given JID
    fsize = get_file_size(filepath)
    no_workers = split_datafile(filepath, jid) + 1

    logger.info(f'Chunks created')

    logger.info(f'File size: {fsize}')
    logger.info(f'# workers: {no_workers}')
  

    # apply THE MAPPERS job
    create_and_apply_mapper_Job_manifest(batch_v1, jid, mapper, reducer, no_workers)
    logger.info(f'Mapper job{jid} applied')
    
            
    logger.info('Waiting for mapper job'+jid+' to complete.')
    mapper_status = wait_for_job_done(job_name="mapper-job"+jid, namespace=namespace)
    logger.info(f"Status {mapper_status}")
 
    # apply SHUFFLE 
    if mapper_status:
        logger.info('About to shuffle.')

        input_path = "/mnt/data/"+jid+"/shuffler/in/"
        output_path = "/mnt/data/"+jid+"/reducer/in/"

        logger.info(f'Input_path: {input_path}')
        logger.info(f'Output_path: {output_path}')

        files = os.listdir(input_path)
        logger.info(f'files from listdir: {files}')
        
        shuffled_data = {}

        for file_path in files:
            file_name = os.path.basename(file_path)
            logger.info(f"Processing file: {file_name}")
            
            with open(input_path + file_path) as f:
                data = json.load(f)
                for key, value in data.items():
                    if key not in shuffled_data:
                        shuffled_data[key] = value
                    else:
                        shuffled_data[key].extend(value)
                
        # prepare and estimate reducers
        keys = list(shuffled_data.keys())
        
        keys_per_reducer = ceil(len(keys) / no_workers)
        
        no_reducers = ceil(len(keys) / keys_per_reducer)
               
        #logger.info(f'Keys: {keys}')
        logger.info(f'No_reducers: {no_reducers}')
        logger.info(f'Keys_per_reducer: {keys_per_reducer}')
        
        for i in range(no_reducers):
            reducer_data = {}
            start_index = i * keys_per_reducer
            end_index = min((i + 1) * keys_per_reducer, len(keys))
            
            for key in keys[start_index:end_index]:
                reducer_data[key] = shuffled_data[key]
                
            reducer_file_path = os.path.join(output_path, f"reducer-{i}.in")
            with open(reducer_file_path, 'w') as out:
                json.dump(reducer_data, out, indent=1, ensure_ascii=False)
            
        #logger.info(f'reducer_data: {reducer_data}')
        
            
        # apply the REDUCERS job
        logger.info(f'applying reducer job{jid}')
        create_and_apply_reducer_Job_manifest(batch_v1, jid, reducer, no_reducers)    
        
        logger.info(f'waiting for reducer-job{jid}')
        reducer_status = wait_for_job_done(job_name="reducer-job"+jid, namespace=namespace)
        logger.info(f'reducer_status: {reducer_status}')
    
    # save output only and cleanup.
    # cleanup pv with given jid
    logger.info(f'cleaning up')
    cleanUp_pv(jid)
    
    # delete jobs
    delete_job(batch_v1, "mapper-job"+jid)
    delete_job(batch_v1, "reducer-job"+jid)
     
    return {"jid": jid, "mapper-status": mapper_status, "reducer-status":reducer_status}
  