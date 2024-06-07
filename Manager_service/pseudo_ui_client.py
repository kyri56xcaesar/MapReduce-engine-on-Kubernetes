import requests


# response = requests.get(url)


# Paths to files
MAPPER = 'examples/mapper_example.py'
REDUCER = 'examples/reducer_example.py'

FILENAME = "examples/word_count_data.txt"

files = {
    'mapper' : (MAPPER, open(MAPPER), 'r'),
    'reducer' : (REDUCER, open(REDUCER), 'rb')
    
}

data = {
    'filename' : FILENAME
}

# send the post request
r = requests.get("http://localhost:5000/check/5")
print(r.text)


# response = requests.post("http://localhost:5000/setup", files=files, data=data)
# print('Status code:', response.status_code)
# print('Response text:', response.text)
