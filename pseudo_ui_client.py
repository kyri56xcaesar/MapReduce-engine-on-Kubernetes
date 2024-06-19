import requests
import time

# response = requests.get(url)


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

agsa = "3"
url = "http://10.244.0."+agsa+":5000/submit-job"
num_requests = 1
for i in range(num_requests):
    try:
        response = requests.post(url=url, files=files, data=data)
        print(f'Request {1}: Status Code = {response.status_code}')
        # Process the response as needed
        # e.g., print(response.json())
    except requests.exceptions.RequestException as e:
        print(f'Request {1} failed: {e}')



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

time.sleep(4)
response = requests.post("http://10.244.0.48:5000/submit-job", files=files, data=data)
print('Status code:', response.status_code)
print('Response text:', response.text)

#response = requests.post("http://localhost:5000/submit-job", files=files, data=data)

