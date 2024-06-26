import requests
import json
import sys
import getopt
from getpass import getpass
import subprocess


#result_fetch_ip = subprocess.run(['minikube', 'ip'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#minikube_ip = result_fetch_ip.stdout.decode('utf-8').strip()
#ip = minikube_ip    

ip = "localhost"
AUTH_PORT = "30001"
UI_PORT = "30002"

# AUTH_PORT = "1337"
# UI_PORT = "1338"
MANAGER_PORT = "5000"

datasets = ["word_count_data.txt", "word_count_small.txt", "big_data.txt"]

# LOGGING IN FROM AUTH SERVICE
def login():
    username = input("Username: ")
    password = getpass()
    

    url = f'http://{ip}:{AUTH_PORT}/login' 
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': username,
        'password': password
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(response)

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
    # talking to UI 
    url = f"http://{ip}:{UI_PORT}/cmd"

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


def list_available_datasets():
    for index, dataset in enumerate(datasets):
        print(f'{index + 1}. dataset: {dataset}')

def usage():
    print('''
Usage: python client.py [MODE]|[OPTION]
    datafiles
    jobs [filename, mapper reducer],  submit a job
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
            
            input_file, mapper_file, reducer_file = args[1], args[2], args[3]
            print(f"Submitting a job with files: Input file:{input_file}, Mapper: {mapper_file}, Reducer: {reducer_file}")


            try:
                # Open the files inside the loop to reset the file pointer
                with open(mapper_file, 'r') as mapper_file1, open(reducer_file, 'rb') as reducer_file1:
                    files = {
                        'mapper': (mapper_file, mapper_file1, 'text/x-python'),
                        'reducer': (reducer_file, reducer_file1, 'text/x-python')
                    }
                    data = {
                        'filename' : input_file
                    }
                    
                    url = f"http://{ip}:{UI_PORT}/send-jobs"
                    response=requests.post(url=url, files=files, data=data, cookies={'token': token})
                    
                    print(f'Status Code = {response.status_code}')
                    print(response.json())
                    
            except requests.exceptions.RequestException as e:
                print(f'Request {1} failed: {e}')

            # TODO: Implement
            
        elif len(args) == 1:
            if not token:
                token = login()
            print("Viewing jobs...")
            # TODO: Implement
            while True:
                # print submenu
                print('''
    1. View job result.
    2. View job details.
    3. Exit.
                ''')
                choice = input("> ")
                if choice == '1':
                    jid = input('Enter jid: ')
                    url = f"http://{ip}:{UI_PORT}/job-result/{jid}"
                    print(url)
                    
                    response = requests.get(url)
                    
                    print(response.json())
                elif choice == '2':
                    jid = input("Job ID: ")
                    
                    url = f"http://{ip}:{UI_PORT}/view-job/{jid}"
                    print(url)
                    
                    response = requests.get(url)
                    
                    print(response.json())
                elif choice == '3':
                    print()
                    break
                else:
                    print("Invalid option.\n")
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
    elif mode == "datafiles":
        if not token:
            token = login()
        list_available_datasets()
    else:
        usage()
        sys.exit(2)


if __name__ == '__main__':
    main()

