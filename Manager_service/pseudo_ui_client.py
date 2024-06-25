from threading import Thread
from venv import logger
import requests
import time
from kubernetes import config, client


def get_endpoints():
    namespace = 'default'
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    service_name = 'manager'

    try:
        endpoints = v1.read_namespaced_endpoints(name=service_name, namespace=namespace)
        pod_ips = [addr.ip for subset in endpoints.subsets for addr in subset.addresses]
        return pod_ips
    except Exception as e:
        logger.info(f"Error retrieving endpoints: {e}")
        return []
# response = requests.get(url)

def send_req():
    # url1 = f"http://{get_endpoints()[1]}:5000/submit-job"
    url0 = f"http://{get_endpoints()[0]}:5000/submit-job"
    print(url0)
    try:
        # Open the files inside the loop to reset the file pointer
        with open(MAPPER, 'r') as mapper_file, open(REDUCER, 'rb') as reducer_file:
            files = {
                'mapper': (MAPPER, mapper_file, 'text/x-python'),
                'reducer': (REDUCER, reducer_file, 'text/x-python')
            }
            response = requests.post(url=url0, files=files, data=data)
            print(f'Request {i + 1}: Status Code = {response.status_code}')
            # Process the response as needed
            # e.g., print(response.json())
    except requests.exceptions.RequestException as e:
        print(f'Request {i + 1} failed: {e}')  
    t.join

# Paths to files
MAPPER = 'mapper_input.py'
REDUCER = 'reducer_input.py'

FILENAME = "word_count_data.txt"

files = {
    'mapper' : (MAPPER, open(MAPPER), 'r'),
    'reducer' : (REDUCER, open(REDUCER), 'rb')
    
}

data = {
    'filename' : FILENAME
}

for i in range(3):
    # time.sleep(1)
    t = Thread(target=send_req)
    t.daemon = True
    t.start()

time.sleep(5)
exit