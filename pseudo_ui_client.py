from threading import Thread
import requests
import time

# response = requests.get(url)

def send_req():
    try:
        # Open the files inside the loop to reset the file pointer
        with open(MAPPER, 'r') as mapper_file, open(REDUCER, 'rb') as reducer_file:
            files = {
                'mapper': (MAPPER, mapper_file, 'text/x-python'),
                'reducer': (REDUCER, reducer_file, 'text/x-python')
            }
            response = requests.post(url=url, files=files, data=data)
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

agsa = "277"
url = "http://10.244.2."+agsa+":5000/submit-job"
num_requests = 2

for i in range(num_requests):
    t = Thread(target=send_req)
    t.daemon = True
    t.start()

time.sleep(20)
exit


# send the post request
# r = requests.get("http://localhost:5000/check/5")
# print(r.text)

# response = requests.post("http://10.244.0.48:5000/submit-job", files=files, data=data)
# print('Status code:', response.status_code)
# print('Response text:', response.text)

# time.sleep(4)
# response = requests.post("http://10.244.0.48:5000/submit-job", files=files, data=data)
# print('Status code:', response.status_code)
# print('Response text:', response.text)

# time.sleep(4)
# response = requests.post("http://10.244.0.48:5000/submit-job", files=files, data=data)
# print('Status code:', response.status_code)
# print('Response text:', response.text)

# time.sleep(4)
# response = requests.post("http://10.244.0.48:5000/submit-job", files=files, data=data)
# print('Status code:', response.status_code)
# print('Response text:', response.text)

#response = requests.post("http://localhost:5000/submit-job", files=files, data=data)
