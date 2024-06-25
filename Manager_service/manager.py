import os
import logging
from dotenv import load_dotenv
from flask import *
from kubernetes import client, config

from kube.kube_client import *
from kube.kube_utils import *
from service_utils import *
import etcd_api
# This service should provide an REST api in order to setup an execution of a JOB
#
# And handle the execution of the job
#


# API 
# /health if service is running
# /  idk yet
# /setup, recieve map/reduce functions, filename, maybe return job id?
# provide seperate functions for check?
#
# /submit-job, submit the job to K8S
# /check/id  -> check job id status
#
#
load_dotenv()

PORT = os.environ['MANAGER_PORT']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    
    app = Flask(__name__)
    app.config.from_prefixed_env()
    
    # subprocess.run(["python3", "kube_client.py"]) # reschedule any unfinished jobs
    rescedule_unfinished_jobs()

    return app

app = create_app()

# This path could be used for frontend demo
@app.route("/")
def main():
    return {"status" : "hello world"}

@app.route("/healthz", methods=["GET"])
def health():
    
    return {'mngr_status':'I am alive'}

@app.route("/submit-job", methods=["POST"])
def submit_job():
     
    ## guard statements, check if everything is here
    # check all inputs 
    # validate inputs
    if not request.files or ('mapper' not in request.files and 'reducer' not in request.files):
        return jid_json_formatted_message('-1', "mngr_message", "must provide map/reduce files", 400)
        
    filename = request.form.get('filename')
       
    if not filename:
        return jsonify({"mngr_message":"must provide the filename"}), 400
    
    # if all good..
    # create a new "job" placeholder, job holds a job conf as well.
    try:

        map_file = request.files['mapper']
        reduce_file = request.files['reducer']
        
        logger.info(f'map_file received: {map_file}')
        logger.info(f'reduce_file received: {reduce_file}')
        
        
        # Setup Job conf
        mapper_content = map_file.read().decode("utf-8")
        reducer_content = reduce_file.read().decode("utf-8")
        
        logger.info(f'mapper_content received:\n {mapper_content}')
        logger.info(f'reducer_content received:\n {reducer_content}')
        logger.info(f'filename: {filename}')
        

        phase = "mapping"

        manager_jobs = etcd_api.get_with_lock("manager-0")
        if manager_jobs is not None:
            job_count = int(manager_jobs)
            jid = job_count + 1
        else:
            jid=1
        etcd_api.put(f'{jid}-0',str(filename))
        etcd_api.put(f'{jid}-1',str(mapper_content))
        etcd_api.put(f'{jid}-2',str(reducer_content))
        etcd_api.put(f'{jid}-3',str(phase))
        etcd_api.put_with_lock("manager-0",str(jid))       
        logger.info(f'current JID: {jid}')
        
        # Schedule an actual job in the K8S
        job_status = schedule_job(str(jid), filename, mapper_content, reducer_content,phase)
        logger.info(f'jid: {jid}, status: {job_status}')
        
        # submit the job
        return jid_json_formatted_message(str(jid), "mngr_message", f"Job submitted successfully: {job_status}", 200)
    
    except Exception as e:
        logger.error(f'Exception: {e}')
        return jid_json_formatted_message("-1", "error", f"an error occured, details: {str(e)}", 500)

# Under construction...
@app.route("/check", methods=["GET"])
def check_all():
    
    # need to get all jids from etcd.
    jids = []
    logger.info(f'existing jids: {jids}')
    
    if jids:
        print('sending jids')
        return jsonify(jids)
    else:
        print('sending empty message')
        return jsonify({"mngr_message" : "empty"})

@app.route("/check/<jid>", methods=["GET"])
def check_jid(jid):
    
    logger.info(f'JOB id: {jid}')
    
    
    mapper_job_status = check_job_status("mapper-job"+jid, 'dpyravlos')
    reducer_job_status = check_job_status("reducer-job"+jid, 'dpyravlos')
    
    return jid_json_formatted_message(jid, "mngr_message", f"mapper_job_status: {mapper_job_status}\nreducer_job_status: {reducer_job_status}", 200)

@app.route("/get-job-result/<jid>", methods=["GET"])
def retrieve_results(jid):
    
    # Guard statements
    logger.info(f'about to retrieve reducer out data.')
    
    output_path = f"/mnt/data/{jid}/results{jid}.out"
    try:
    # prepare the result data.
        res = gather_output_chunks(jid, output_path, logger)
    except Exception as e:
        logger.error(f'Exception: {e}')
        return jid_json_formatted_message("-1", "error", f"an error occured, details: {str(e)}", 500)
            # Send the results in json format
    # Decide if FTP or http or sth else # This is too complated prob
    
    return jid_json_formatted_message(jid, "mngr_message", f"results gathered {res}", 200)

if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
