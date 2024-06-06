import sys, os
import json
from Jobs import *
from utils import *
from flask import *
from kubernetes import client, config



# This service should provide an REST api in order to setup an execution of a JOB
#
# And handle the execution of the job
#
#
#
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

app = Flask(__name__)
PORT = 5000


# 

# Jobs
jobs : dict[str, Job]= dict()


@app.route("/health", methods=["GET"])
def health():
    return {'status':'g u c c i'}


@app.route("/check", methods=["GET"])
def check():
    pass


# This path could be used for frontend demo
@app.route("/")
def main():
    return {"status" : "hello world"}


# Edit a specific jid
@app.route("/setup/mapper/<jid>", methods=["POST"])
def setup_job_mapper(jid='-1'):
    if jid not in jobs.keys:
        return jid_json_formatted_message(jid, "message", "jid doesn't exist", 400)

    if not request.files or 'mapper' not in request.files:
        return jid_json_formatted_message(jid=jid, type="message", content="must provide mapper file", code=400)

    mapper_file = request.files['mapper']
    
    job = jobs[jid]
    
    
    try:
        job.set_mapper_func(mapper_file.read())
    except Exception as e:
        return jid_json_formatted_message(jid, "error", f"an error occured, details: {str(e)}", 500)

    
    return jid_json_formatted_message(jid, "message", "mapper function set", 200)

    

@app.route("/setup/reducer/<jid>", methods=["POST"])
def setup_job_reducer(jid='-1'):
    if jid not in jobs.keys:
        return jid_json_formatted_message(jid, "message", "jid doesn't exist", 400)
    
    if not request.files or 'reducer' not in request.files:
        return jid_json_formatted_message(jid, "message", "must provide reducer file", 400)
    
    reduce_file = request.files['reducer']
    
    job = jobs[jid]
    
    try:
        job.set_reducer_func(reduce_file.read())
    except Exception as e:
        return jid_json_formatted_message(jid, "error", f"an error occured, details: {str(e)}", 500)

    
    return jid_json_formatted_message(jid, "message", "reducer function set", 200)
    
@app.route("/setup/filename/<jid>", methods=["POST"])
def setup_job_filename(jid='-1'):
    if jid not in jobs.keys:
        return jid_json_formatted_message(jid, "message", "jid doesn't exist", 400) 
    
    filename = request.form.get('filename')
    
    if not filename:
        return jid_json_formatted_message(jid, "message", "must provide filename", 400)
    
    job = jobs[jid]
    
    job.set_filename(filename=filename)
    
    return jid_json_formatted_message(jid, "message", "filename set", 200)

@app.route("/setup", methods=["POST"])
def configure_job():
    
    ## guard statements, check if everything is here
    # check all inputs 
    # validate inputs
    if not request.files or ('mapper' not in request.files and 'reducer' not in request.files):
        return jid_json_formatted_message('-1', "message", "must provide map/reduce files", 400)
        
    filename = request.form.get('filename')
       
    if not filename:
        return jsonify({"message":"must provide the filename"}), 400
    
    # if all good..
    # create a new "job" placeholder, job holds a job conf as well.
    

    job = Job()
    jid = job.job_id
    jobs[job.job_id] = job

    try:

        map_file = request.files['mapper']
        reduce_file = request.files['reducer']
        
    
        # Setup Job conf
        job.setup_conf(map_file.read(), reduce_file.read(), filename)

        print(job)
        # submit the job
        return jid_json_formatted_message(jid, "message", "files received!", 200)
    
    except Exception as e:
        print(f'Exception: {e}')
    finally:
        del job
        return jid_json_formatted_message(jid, "error", f"an error occured, details: {str(e)}", 500)
        
        


@app.route("/submit-job")
def submit_job():
    pass



if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=PORT)