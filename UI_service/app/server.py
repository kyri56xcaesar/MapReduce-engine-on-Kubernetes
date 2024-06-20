from flask import Flask, redirect, request, session, jsonify
from base64 import b64decode
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

def get_pubkey():
    namespace = 'default'
    authservice_name = 'authservice'
    authservice_endpoints = get_service_endpoints(namespace, authservice_name)
    auth_endpoint=authservice_endpoints[0]
    response = requests.get(f"http://{auth_endpoint}/pubkey")
    
    data = json.loads(response.text)
    public_key = b64decode(data["message"]).decode()
    
    return public_key


def verify_user(token):
    public_key = get_pubkey()

    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload
    except jwt.InvalidSignatureError as err:
        print(str(err))
        return None

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
@app.route("/send-jobs", methods=["POST"])
def send_jobs():
    #data = request.get_json()
    headers = request.headers
    token = headers["Cookie"][6:]
    if not token:
        return jsonify({"message": "No token was provided."})
    payload = verify_user(token)
    if not payload:
        return jsonify({"message": "Token verification failed."})
    
    namespace = 'default'
    managerservice_name='manager'    
    managerservice_endpoints=get_service_endpoints(namespace, managerservice_name)
    manager_endpoint=managerservice_endpoints[0]
    logger.info(request.files)
    logger.info(request.data.decode('utf-8'))
    logger.info(request.headers)

    #logger.info(f'reduce_file received: {request.files['reducer']}')
    #logger.info(f'mapper received: {request.files['mapper']}')
    logger.info(f'data file : {request.form.get('mapper')}')
    logger.info(f'data file : {request.form.get('reducer')}')

    #redirect(f"http://{manager_endpoint}/submit-job",302)
    response=requests.post(url=f"http://{manager_endpoint}/submit-job", files=request.files, data=request.data)
    

    return jsonify({"message": "ui response"})



@app.route("/cmd", methods=["POST"])
def cmd():
    namespace = 'default'
    authservice_name = 'authservice'
    managerservice_name='manager'
    uiservice_name = 'uiservice'
    authservice_endpoints = get_service_endpoints(namespace, authservice_name)
    managerservice_endpoints=get_service_endpoints(namespace, managerservice_name)
    uiservice_endpoints = get_service_endpoints(namespace, uiservice_name)
    
    ui_endpoint=uiservice_endpoints[0]
    manager_endpoint=managerservice_endpoints[0]
    auth_endpoint=authservice_endpoints[0] #authservice_endpoints is list

    data = request.get_json()
    headers = request.headers

    token = headers["Cookie"][6:]
    if not token:
        return jsonify({"message": "No token was provided."})

    payload = verify_user(token)
    if not payload:
        return jsonify({"message": "Token verification failed."})

    # role = payload["role"] # TODO
    username = payload["username"]

    cmd = data["cmd"]
    if cmd == "create-user":
        if username == "admin":
            rdata = data["data"]
            print(rdata)
            data = requests.post(f"http://localhost:1337/admin/create-user", json=rdata)
            return data.text
        else:
            return jsonify({"message": "Only admin is allowed to run that command."})
    elif cmd == "delete-user":
        if username == "admin":
            rdata = data["data"]
            data = requests.post(f"http://localhost:1337/admin/delete-user", json=rdata)
            return data.text
        else:
            return jsonify({"message": "Only admin is allowed to run that command."})
    elif cmd == "list-users":
        if username == "admin":
            data = requests.get(f"http://localhost:1337/admin/list-users")
            return data.text
        else:
            return jsonify({"message": "Only admin is allowed to run that command."})
    elif cmd == "submit-job":
        
        return jsonify({"message": "Not implemented yet."})
    elif cmd == "view-jobs":
        return jsonify({"message": "Not implemented yet."})
    else:
        return jsonify({"message": "Invalid command."})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1338, debug=True) # TODO: disable
