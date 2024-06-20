import requests
import json
import sys
import getopt
from getpass import getpass
import subprocess

def login():
    username = input("Username: ")
    password = getpass()
    result_fetch_ip = subprocess.run(['minikube', 'ip'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    minikube_ip = result_fetch_ip.stdout.decode('utf-8').strip()
    url = f'http://{minikube_ip}:30001/login' 
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': username,
        'password': password
    }
    response = requests.post(url, headers=headers, json=data)
    
    print(response)

    #print(data["message"])
    data = json.loads(response.text)
    if response.status_code == 401:
        sys.exit()

    token = data["token"]

    if response.status_code == 401:
        sys.exit()
    else:
        return token

def admin_menu():
    print("1. create user")
    print("2. delete user")
    print("3. list users")
    print("4. list ips")
    print("5. exit")


def admin():
    result_fetch_ip = subprocess.run(['minikube', 'ip'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    minikube_ip = result_fetch_ip.stdout.decode('utf-8').strip()
    url = f"http://{minikube_ip}:30002/cmd"

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
            data = { 'cmd': 'view-ips' }
            make_request(url, headers, "POST", data)
        elif choice == '5':
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
def make_file_request(url, headers, method,files, data=['notset']):
    if method == "POST":
        response = requests.post(url, headers=headers,files=files,json=data)
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
        if not token:
                token = login()
        
        if len(args) == 4:
            if not token:
                token = login()
            
            input_file,mapper_file, reducer_file = args[1], args[2],args[3]
            print(f"Submitting a job with files: Input file:{input_file}, Mapper: {mapper_file}, Reducer: {reducer_file}")
            num_requests = 2

            files = {
            'mapper' : (mapper_file, open(mapper_file), 'r'),
            'reducer' : (reducer_file, open(reducer_file), 'rb')
            }
            data = {
            'filename' : "word_count_data.txt"
            }

            result_fetch_ip = subprocess.run(['minikube', 'ip'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            minikube_ip = result_fetch_ip.stdout.decode('utf-8').strip()
            print("minikube ip:",minikube_ip)
            
           
            try:
                # Open the files inside the loop to reset the file pointer
                with open(mapper_file, 'r') as mapper_file1, open(reducer_file, 'rb') as reducer_file1:
                    files = {
                        'mapper': (mapper_file, mapper_file1, 'text/x-python'),
                        'reducer': (reducer_file, reducer_file1, 'text/x-python')
                    }
                    headers = {'Content-Type': 'application/json', 'Cookie': f'token={token}'}
                    url = f"http://{minikube_ip}:30002/send-jobs"
                    responst=requests.post(url=url,headers=headers,files=files,data=data)

                    #print(f'Request {i + 1}: Status Code = {response.status_code}'
                    # Process the response as needed
                    # e.g., print(response.json())
            except requests.exceptions.RequestException as e:
                print(f'Request {1} failed: {e}')

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

