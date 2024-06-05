import requests
import json
from getpass import getpass

session = requests.Session()

def login(url, headers):
    username = input("Username: ")
    password = getpass()
    
    url += '/login'
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, headers=headers, json=data)
    
    data = json.loads(response.text)
    print()
    print(data["message"])
    if response.status_code == 401:
        exit()
    else:
        session.cookies.update(response.cookies)

def user_menu():
    print("1. jobs")
    print("2. admin")
    print("3. exit")

def admin_menu():
    print("1. create user")
    print("2. delete user")
    print("3. list users")
    print("4. exit")

def admin():
    while True:
        admin_menu()
        choice = input("> ")
        if choice == '1':
            username = input("Username: ")
            password = getpass()
            data = { 'username': username, 'password': password }
            make_request(url+"/admin/create-user", headers, "POST", data)
        elif choice == '2':
            username = input("Username: ")
            data = { 'username': username }
            make_request(url+"/admin/delete-user", headers, "POST", data)
        elif choice == '3':
            make_request(url+"/admin/list-users", headers, "GET")
        elif choice == '4':
            print()
            break
        else:
            print("Invalid option.\n")

# TODO: I don't like this, but should be okay for now
def print_json_values(data):
    lines = []
    if isinstance(data, list):
        for item in data:
            line = ' '.join(str(value) for value in item.values())
            lines.append(line)
    elif isinstance(data, dict):
        line = ' '.join(str(value) for value in data.values())
        lines.append(line)
    print('\n'.join(lines) + '\n')

def make_request(url, headers, method, data=['notset']):
    if method == "POST":
        response = session.post(url, headers=headers, json=data)
    else:
        response = session.get(url, headers=headers)
    data = json.loads(response.text)
    
    print_json_values(data)

    return response.status_code

if __name__ == '__main__':
    url = "http://localhost:1337"
    headers = {'Content-Type': 'application/json'}
    
    login(url, headers)

    while True:
        user_menu()
        choice = input("> ")
        if choice == '1':
            make_request(url+"/jobs", headers, "GET")
        elif choice == '2':
            if (make_request(url+"/admin", headers, "GET")) == 200:
                admin()
        elif choice == '3':
            make_request(url+"/logout", headers, "GET")
            break
        else:
            print("Invalid option.\n")
