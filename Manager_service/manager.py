import os
from dotenv import load_dotenv
from flask import *
from kubernetes import client, config

from Jobs import *
from Utils import *
import db.Database as db
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

load_dotenv()

def create_app():
    

    app = Flask(__name__)
    app.config.from_prefixed_env()
    
    db.init_app(app, db_path=os.environ['FLASK_DATABASE'])

    return app

app = create_app()

# 
@app.route("/health", methods=["GET"])
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
    
    print(jid)
    
    job: Job = db.get_job_by_id(jid)
    
    if not job:
        return jsonify({"status":"does't exist"})
    
    return job.to_json()


# This path could be used for frontend demo
@app.route("/")
def main():
    return {"status" : "hello world"}

@app.route("/setup/", methods=["POST"])
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

    try:

        map_file = request.files['mapper']
        reduce_file = request.files['reducer']
        
        job: Job = Job()
        
        # Setup Job conf
        job.setup_conf(map_file.read().decode("utf-8"), reduce_file.read().decode("utf-8"), filename)


        _, jid = db.insert_job(job.JobConfiguration)
        
        job.jid = jid

        # submit the job
        return jid_json_formatted_message(str(jid), "message", "files received!", 200)
    
    except Exception as e:
        print(f'Exception: {e}')
        return jid_json_formatted_message("-1", "error", f"an error occured, details: {str(e)}", 500)
        
        
        


@app.route("/submit-job")
def submit_job():
    pass


# Edit a specific jid mapper
@app.route("/setup/mapper/<jid>", methods=["POST"])
def setup_job_mapper(jid='-1'):

    if not request.files or 'mapper' not in request.files:
        return jid_json_formatted_message(jid=jid, type="message", content="must provide mapper file", code=400)

    mapper_file = request.files['mapper'].read().decode("utf-8")
    
    success = db.update_job_mapper_by_jid(jid, mapper_file)    
    
    if success:
        return jid_json_formatted_message(jid, "message", "mapper updated successfully", 200)
    
    
    return jid_json_formatted_message(jid, "message", "mapper not updated", 400)

    

    
# Edit a specific jid reducer
@app.route("/setup/reducer/<jid>", methods=["POST"])
def setup_job_reducer(jid='-1'):

    if not request.files or 'reducer' not in request.files:
        return jid_json_formatted_message(jid, "message", "must provide reducer file", 400)
    
    reducer_file = request.files['reducer'].read().decode("utf-8")
    
    success = db.update_job_reducer_by_jid(jid, reducer_file)    
    
    if success:
        return jid_json_formatted_message(jid, "message", "reducer updated successfully", 200)
    
    
    return jid_json_formatted_message(jid, "message", "reducer not updated", 400)

# Edit a specific jid filename
@app.route("/setup/filename/<jid>", methods=["POST"])
def setup_job_filename(jid='-1'):

    filename = request.form.get('filename')
    
    if not filename:
        return jid_json_formatted_message(jid, "message", "must provide filename", 400)
    
    success = db.update_job_filename_by_jid(jid, filename)    
    
    if success:
        return jid_json_formatted_message(jid, "message", "filename updated successfully", 200)
    
    
    return jid_json_formatted_message(jid, "message", "filename not updated", 400)




PORT = os.environ['SERVICE_PORT']
if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=PORT, debug=False)