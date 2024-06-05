import requests

route = "setup"
url = "http://localhost:5000/" + route

# response = requests.get(url)


MAPPER = 'mapper_example.py'
REDUCER = 'reducer_example.py'

files = {
    'mapper' : (MAPPER, open(''))
}


response = requests.post(url,
    headers = {"Content-Type" : "application/json"},
    data = {"key" : "value"}
                         
)


print(response)