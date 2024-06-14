from flask import Flask, redirect, request, session, jsonify
from base64 import b64decode
import requests
import json
import jwt
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

def get_pubkey():
    response = requests.get("http://localhost:1337/pubkey")
    data = json.loads(response.text)
    public_key = b64decode(data["message"]).decode()
    return public_key


def verify_user(token):
    public_key = get_pubkey()

    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload
    except jwt.InvalidSignatureError as err:
        print(str(err))
        return None


@app.route("/cmd", methods=["POST"])
def cmd():
    data = request.get_json()
    headers = request.headers

    token = headers["Cookie"][6:]
    if not token:
        return jsonify({"message": "No token was provided."})

    payload = verify_user(token)
    if not payload:
        return jsonify({"message": "Token verification failed."})

    # role = payload["role"] # TODO
    username = payload["username"]

    cmd = data["cmd"]
    if cmd == "create-user":
        if username == "admin":
            rdata = data["data"]
            print(rdata)
            data = requests.post(f"http://localhost:1337/admin/create-user", json=rdata)
            return data.text
        else:
            return jsonify({"message": "Only admin is allowed to run that command."})
    elif cmd == "delete-user":
        if username == "admin":
            rdata = data["data"]
            data = requests.post(f"http://localhost:1337/admin/delete-user", json=rdata)
            return data.text
        else:
            return jsonify({"message": "Only admin is allowed to run that command."})
    elif cmd == "list-users":
        if username == "admin":
            data = requests.get(f"http://localhost:1337/admin/list-users")
            return data.text
        else:
            return jsonify({"message": "Only admin is allowed to run that command."})
    elif cmd == "submit-job":
        return jsonify({"message": "Not implemented yet."})
    elif cmd == "view-jobs":
        return jsonify({"message": "Not implemented yet."})
    else:
        return jsonify({"message": "Invalid command."})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1338, debug=True) # TODO: disable
