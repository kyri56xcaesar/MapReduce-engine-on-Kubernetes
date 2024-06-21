import os
import logging
from dotenv import load_dotenv
from flask import *
from kubernetes import client, config

from Jobs import *
from kube.kube_client import *
from kube.kube_utils import *
from service_utils import *
import db.database as db
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
    
    db.init_app(app, db_path=os.environ['FLASK_DATABASE'])

    return app

app = create_app()

# This path could be used for frontend demo
@app.route("/")
def main():
    return {"status" : "hello world"}


@app.route("/submit-job/", methods=["POST"])
@app.route("/submit-job", methods=["POST"])
def configure_job():
    
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
        
        # Save data in a db
        job: Job = Job()
        
        # Setup Job conf
        mapper_content = map_file.read().decode("utf-8")
        reducer_content = reduce_file.read().decode("utf-8")
        
        logger.info(f'mapper_content received:\n {mapper_content}')
        logger.info(f'reducer_content received:\n {reducer_content}')
        logger.info(f'filename: {filename}')
        
        job.setup_conf(mapper_content, reducer_content, filename)

        _, jid = db.insert_job(job.JobConfiguration)
        
        job.jid = jid
        logger.info(f'current JID: {jid}')
        #jid = 0
        
        # Schedule an actual job in the K8S
        job_status = kube_client_main(jid, filename, mapper_content, reducer_content)

        logger.info(f'jid: {jid}, status: {job_status}')
        
        # submit the job
        return jid_json_formatted_message(str(jid), "mngr_message", f"Job submitted successfully: {job_status}", 200)
    
    except Exception as e:
        logger.error(f'Exception: {e}')
        return jid_json_formatted_message("-1", "error", f"an error occured, details: {str(e)}", 500)
        
        
        



# Edit a specific jid mapper
@app.route("/setup/mapper/<jid>", methods=["POST"])
def setup_job_mapper(jid='-1'):

    if not request.files or 'mapper' not in request.files:
        return jid_json_formatted_message(jid=jid, type="mngr_message", content="must provide mapper file", code=400)

    mapper_file = request.files['mapper'].read().decode("utf-8")
    
    success = db.update_job_mapper_by_jid(jid, mapper_file)    
    
    if success:
        return jid_json_formatted_message(jid, "mngr_message", "mapper updated successfully", 200)
    
    
    return jid_json_formatted_message(jid, "mngr_message", "mapper not updated", 400)

    

    
# Edit a specific jid reducer
@app.route("/setup/reducer/<jid>", methods=["POST"])
def setup_job_reducer(jid='-1'):

    if not request.files or 'reducer' not in request.files:
        return jid_json_formatted_message(jid, "mngr_message", "must provide reducer file", 400)
    
    reducer_file = request.files['reducer'].read().decode("utf-8")
    
    success = db.update_job_reducer_by_jid(jid, reducer_file)    
    
    if success:
        return jid_json_formatted_message(jid, "mngr_message", "reducer updated successfully", 200)
    
    
    return jid_json_formatted_message(jid, "mngr_message", "reducer not updated", 400)

# Edit a specific jid filename
@app.route("/setup/filename/<jid>", methods=["POST"])
def setup_job_filename(jid='-1'):

    filename = request.form.get('filename')
    
    if not filename:
        return jid_json_formatted_message(jid, "mngr_message", "must provide filename", 400)
    
    success = db.update_job_filename_by_jid(jid, filename)    
    
    if success:
        return jid_json_formatted_message(jid, "mngr_message", "filename updated successfully", 200)
    
    
    return jid_json_formatted_message(jid, "mngr_message", "filename not updated", 400)


# 
@app.route("/healthz", methods=["GET"])
def health():
    
    (_, status) = (db.check_db())

    return {'status':status}


@app.route("/check", methods=["GET"])
@app.route("/check/", methods=["GET"])
def check_all():
    jids = db.get_all_jids()
    return jsonify(jids)


@app.route("/check/<jid>", methods=["GET"])
def check_jid(jid):
    
    logger.info(f'JOB id: {jid}')
    
    job: Job = db.get_job_by_id(jid)
    
    # if not job:
    #     return jsonify({"status":"does't exist"})
    
    mapper_job_status = check_job_status("mapper-job"+jid, 'default')
    reducer_job_status = check_job_status("reducer-job"+jid, 'default')
    
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