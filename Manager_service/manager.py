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

@app.route("/")
def main():
    return {"status" : "hello world"}



@app.route("/setup", methods=["POST"])
def configure_job():
    
    ## guard statements, check if everything is here
    # check all inputs 
    # validate inputs
    
    # if all good..
    # create a new job conf
    #new_job_conf : Jobs.JobConfiguration = Jobs.JobConfiguration    
    
    # create a new "job" placeholder
    request_data = request.get_json()

    print(request_data)
    
    # submit the job
    return {"whatever":"wh"}



@app.route("/submit-job")
def submit_job():
    pass



if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=PORT)