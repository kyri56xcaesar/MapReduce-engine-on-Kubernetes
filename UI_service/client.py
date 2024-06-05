import requests
from getpass import getpass

session = requests.Session()

def menu():
    print("1. jobs")
    print("2. admin")
    print("3. exit")

def login(url):
    print("Login:")
    username = input("Username: ")
    password = getpass()
    url += '/login'
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    if response.status_code == 200:
        print('Login successful!')
    else:
        print('Login failed.')

def console(url):
    url += '/console'
    response = session.get(url)
    if response.status_code == 200:
        print(response.text)
        while True:
            menu()
            option = input("> ")
            data = {
                "option": option
            }
            response = session.post(url, data=data)
            print(response.text)

            if int(option) == 3:
                break

def logout(url):
    url += '/logout'
    response = session.get(url)
    # if response.status_code == 405:
    #     print('Logout successful.')

if __name__ == '__main__':
    url = "http://localhost:1337"

    login(url)
    console(url)
    logout(url)
