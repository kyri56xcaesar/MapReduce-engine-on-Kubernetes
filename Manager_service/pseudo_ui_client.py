import requests

route = "setup"
url = "http://localhost:5000/" + route

# response = requests.get(url)


# Paths to files
MAPPER = './mapper_example.py'
REDUCER = './reducer_example.py'

FILENAME = "./word_count_data.txt"

files = {
    'mapper' : (MAPPER, open(MAPPER), 'rb'),
    'reducer' : (REDUCER, open(REDUCER), 'rb')
    
}

data = {
    'filename' : FILENAME
}

cookie = {'jid': '0'}
# send the post request
response = requests.post(url, files=files, data=data, cookies=cookie)

print('Status code:', response.status_code)
print('Response text:', response.text)
