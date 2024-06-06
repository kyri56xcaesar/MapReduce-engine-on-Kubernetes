import sys, os
import Jobs
import json
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
jobs : Jobs.Job = list()


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



@app.route("/setup", methods=["POST"])
def configure_job():
    
        
    # if no cookie
    if not request.cookies:
        # we should return a jid
        print('we dont have cookies')
        jid = Jobs.job_id_counter
    else:
        jid = request.cookies.get('jid')    
    
    
    try:
        
        ## guard statements, check if everything is here
        # check all inputs 
        # validate inputs

        if 'mapper' not in request.files and 'reducer' not in request.files:
            return jsonify({"message":"must provide files", 'jid': str(jid)}), 400

        
        filename = request.form.get('filename')
        
        if not filename:
            return jsonify({"message":"must provide the filename"}), 400

        # if all good..
        # create a new job conf
        #new_job_conf : Jobs.JobConfiguration = Jobs.JobConfiguration    

        # create a new "job" placeholder

        map_file = request.files['mapper']
        reduce_file = request.files['reducer']
        
        
        # lets preview the files
        print(f'mapper: {map_file.filename}, Content-Type: {map_file.content_type}')
        print(f'reducer: {reduce_file.filename}, Content-Type: {reduce_file.content_type}')

        # should handle according to content-type
        print(map_file.read())
        

        # submit the job
        return jsonify({"message":"files recieved!"})
    except Exception as e:
        print(f'Exception: {e}')
        return jsonify({"error": "An error occured", "detauls": str(e)}), 500



@app.route("/submit-job")
def submit_job():
    pass



if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=PORT)