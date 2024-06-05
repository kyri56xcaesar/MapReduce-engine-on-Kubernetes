import requests

route = "setup"
url = "http://localhost:5000/" + route

# response = requests.get(url)


response = requests.post(url,
    headers = {"Content-Type" : "application/json"},
    data = {"key" : "value"}
                         
)


print(response)