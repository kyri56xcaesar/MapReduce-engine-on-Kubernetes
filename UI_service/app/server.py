from flask import Flask, redirect, request, session, jsonify, Response
from base64 import b64decode
from dotenv import load_dotenv
import requests
import json
import jwt
import os
from kubernetes import client, config
import logging

app = Flask(__name__)
app.secret_key = os.urandom(32)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

PORT = os.environ['UI_PORT']
AUTH_PORT = os.environ['AUTH_PORT']
MANAGER_PORT = os.environ['MANAGER_PORT']
isLocal = os.environ['ISLOCAL']

namespace = 'default'


def get_service_endpoints(namespace, service_name):
    # Load the in-cluster configuration
    config.load_incluster_config()

    # Create an instance of the CoreV1Api
    v1 = client.CoreV1Api()

    # Retrieve the endpoints details
    endpoints = v1.read_namespaced_endpoints(name=service_name, namespace=namespace)

    # Extract the IP addresses and ports
    endpoint_addresses = []
    for subset in endpoints.subsets:
        addresses = subset.addresses
        ports = subset.ports
        for address in addresses:
            for port in ports:
                endpoint_addresses.append(f"{address.ip}:{port.port}")

    return endpoint_addresses

def get_pubkey():
    auth_endpoint_list=get_service_endpoints(namespace, 'authservice')
    auth_endpoint=auth_endpoint_list[0]
    #auth_endpoint = f"localhost:{AUTH_PORT}"
    response = requests.get(f"http://{auth_endpoint}/pubkey")
    
    data = json.loads(response.text)
    logger.info(f'data from response:\n {data}')
    public_key = b64decode(data['auth_message']).decode()
    
    return public_key

def verify_user(token):
    public_key = get_pubkey()

    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload
    except jwt.InvalidSignatureError as err:
        logger.info(str(err))
        return None




@app.route("/healthz", methods=["GET"])
def healthz():
    return {"ui_status":"I am alive."}



# Under construction....
@app.route("/view-jobs", methods=["GET"])
def view_jobs():
    manager_endpoint_list=get_service_endpoints(namespace, 'manager')
    manager_endpoint=manager_endpoint_list[0] 
    #manager_endpoint = "localhost:5000"  

    headers = request.headers
    url = f"http://{manager_endpoint}/check" 
    
    logger.info(url)
    
    response = requests.get(url=url, headers=headers)
    flask_response = Response(response.content, status=response.status_code, content_type=response.headers['Content-Type'])

    
    return flask_response


@app.route("/view-job/<jid>", methods=["GET"])
def view_job(jid):
    
    manager_endpoint=manager_endpoint_list[0]  
    manager_endpoint_list=get_service_endpoints(namespace, 'manager')
    #manager_endpoint = "localhost:5000" 
    
    url = f"http://{manager_endpoint}/check/{jid}"
    logger.info(url)
    response = requests.get(url)
    flask_response = Response(response.content, status=response.status_code, content_type=response.headers['Content-Type'])

    # Massage response
    
    return flask_response

@app.route("/send-jobs", methods=["POST"])
def send_jobs():

    headers = request.headers
    token = headers["Cookie"][6:]
    if not token:
        return jsonify({"ui_message": "No token was provided."})
    payload = verify_user(token)
    if not payload:
        return jsonify({"ui_message": "Token verification failed."})
    
    managerservice_endpoints = get_service_endpoints(namespace, 'manager')
    manager_endpoint = managerservice_endpoints[0]
    #manager_endpoint = "localhost:5000"  

    logger.info(f'Manager endpoints: {manager_endpoint}')

    mapper_file = request.files['mapper']
    reducer_file = request.files['reducer']
    filename = request.form.get('filename')
    
    logger.info(f'mapper_file: {mapper_file}')
    logger.info(f'reducer_file: {reducer_file}')
    logger.info(f'filename: {filename}')


    
    if mapper_file and reducer_file and filename:
        
        files = {
            'mapper': (mapper_file.filename, mapper_file.stream, 'text/x-python'),
            'reducer': (reducer_file.filename, reducer_file.stream, 'text/x-python')
        }
        data = {
            'filename': filename
        }
        
        url = f"http://{manager_endpoint}/submit-job"
        response = requests.post(url=url, files=files, data=data)
    
        if response.status_code == 200:
            return response.json(), 200
        else:
            return {'error' : 'Failed to forward request to the manager'}, response.status_code

    return {'error': 'Invalid input'}, 400

@app.route("/job-result/<jid>", methods=["GET"])
def get_jid_result(jid):
    manager_endpoint_list=get_service_endpoints(namespace, 'manager')
    manager_endpoint=manager_endpoint_list[0]
    #manager_endpoint = "localhost:5000"  

    logger.info("Get Job result reguest, forwarding to manager...")
    
    url = f"http://{manager_endpoint}/get-job-result/{jid}"
    
    response = requests.get(url=url)
    
    logger.info(f"response from manager: {response}")
    
    
    return response


@app.route("/cmd", methods=["POST"])
def cmd():
    
    auth_endpoint_list=get_service_endpoints(namespace, 'authservice')
    auth_endpoint=auth_endpoint_list[0]
    manager_endpoint_list=get_service_endpoints(namespace, 'authservice')
    manager_endpoint=manager_endpoint_list[0]
    ui_endpoint_list=get_service_endpoints(namespace,'uiservice')
    ui_endpoint=ui_endpoint_list[0]
    data = request.get_json()
    headers = request.headers

    token = headers["Cookie"][6:]
    if not token:
        return jsonify({"ui_message": "No token was provided."})

    payload = verify_user(token)
    if not payload:
        return jsonify({"ui_message": "Token verification failed."})

    # role = payload["role"] # TODO
    username = payload["username"]

    cmd = data["cmd"]
    if cmd == "create-user":
        if username == "admin":
            rdata = data["data"]
            logger.info(rdata)
            data = requests.post(f"http://{auth_endpoint}/admin/create-user", json=rdata)
            return data.text
        else:
            return jsonify({"ui_message": "Only admin is allowed to run that command."})
    elif cmd == "delete-user":
        if username == "admin":
            rdata = data["data"]
            data = requests.post(f"http://{auth_endpoint}/admin/delete-user", json=rdata)
            return data.text
        else:
            return jsonify({"ui_message": "Only admin is allowed to run that command."})
    elif cmd == "list-users":
        if username == "admin":
            data = requests.get(f"http://{auth_endpoint}/admin/list-users")
            return data.text
        else:
            return jsonify({"ui_message": "Only admin is allowed to run that command."})
    elif cmd == "submit-job":
        
        return jsonify({"ui_message": "Not implemented yet."})
    elif cmd == "view-jobs":
        return jsonify({"ui_message": "Not implemented yet."})
    elif cmd == "view-ips":      
        return jsonify({"message":f"AuthService - EndPoint : {auth_endpoint}\nUiService - EndPoint: {ui_endpoint}\nManagerService - Endpoint: {manager_endpoint}"})
    else:
        return jsonify({"ui_message": "Invalid command."})

if __name__ == "__main__":  
    app.run(host='0.0.0.0', port=PORT, debug=False) 
