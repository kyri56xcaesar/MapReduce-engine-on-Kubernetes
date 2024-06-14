import requests
import json
import sys
import getopt
from getpass import getpass


def login():
    username = input("Username: ")
    password = getpass()
    
    url = 'http://localhost:1337/login'
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': username,
        'password': password
    }
    response = requests.post(url, headers=headers, json=data)
    
    data = json.loads(response.text)
    token = data["token"]

    print(data["message"])
    if response.status_code == 401:
        sys.exit()
    else:
        return token


def admin_menu():
    print("1. create user")
    print("2. delete user")
    print("3. list users")
    print("4. exit")


def admin():
    url = "http://localhost:1338/cmd"
    headers = {'Content-Type': 'application/json', 'Cookie': f'token={token}'}
    
    while True:
        admin_menu()
        choice = input("> ")
        if choice == '1':
            username = input("Username: ")
            password = getpass()
            data = { 'cmd': 'create-user', 'data': {'username': username, 'password': password} }
            make_request(url, headers, "POST", data)
        elif choice == '2':
            username = input("Username: ")
            data = { 'cmd': 'delete-user', 'data': {'username': username} }
            make_request(url, headers, "POST", data)
        elif choice == '3':
            data = { 'cmd': 'list-users' }
            make_request(url, headers, "POST", data)
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
        response = requests.post(url, headers=headers, json=data)
    else:
        response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    
    print_json_values(data)

    return response.status_code


def usage():
    print('''
Usage: python client.py [MODE]|[OPTION]
    jobs [mapper reducer],  submit a job
    jobs,                   view jobs
    admin,                  access admin interface
    -h,	display this help text and exit
    ''')


def main():
    try:
        _, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    for arg in args:
        if arg in ("-h", "--help"):
            usage()
            sys.exit(0)

    if len(args) == 0:
        usage()
        sys.exit(2)

    global token
    token = None

    mode = args[0]
    if mode == "jobs":
        if len(args) == 3:
            if not token:
                token = login()
            file1, file2 = args[1], args[2]
            print(f"Submitting a job with files: {file1} and {file2}")
            # TODO: Implement
        elif len(args) == 1:
            if not token:
                token = login()
            print("Viewing jobs...")
            # TODO: Implement
        else:
            usage()
            sys.exit(2)
    elif mode == "admin":
        if len(args) == 1:
            print("Accessing admin interface...")
            if not token:
                token = login()
            admin()
        else:
            usage()
            sys.exit(2)
    else:
        usage()
        sys.exit(2)


if __name__ == '__main__':
    main()
