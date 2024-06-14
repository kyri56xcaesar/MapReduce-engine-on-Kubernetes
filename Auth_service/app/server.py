from flask import Flask, redirect, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from Crypto.PublicKey import RSA
from base64 import b64encode
import jwt
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.getcwd() + "/db/users.db"

db = SQLAlchemy()
db.init_app(app)

key = RSA.generate(2048)
PRIVATE_KEY = key.export_key()
PUBLIC_KEY = key.publickey().export_key()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


def create_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"message":"User already exists."})

    user = User(username, password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"User created successfully."})


def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message":"User does not exist."})

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message":"User deleted successfully."})


def list_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "password": user.password
        }
        user_list.append(user_data)

    return jsonify(user_list)


def generate_token(username):
    payload = {
        'username': username,
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256')
    return token


@app.route("/login", methods=["GET", "POST"])
def login():
    if session:
        return jsonify({"message":"Please log out first."})

    if request.method == "GET":
        return jsonify({"message":"Please login."})

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        token = generate_token(username)
        session["token"] = token
        return jsonify({"message":f"Hello {username}.", "token":token})
    else:
        return jsonify({"message":"Login failed."}), 401


@app.route("/logout")
def logout():
    session.pop("token", None)
    return jsonify({"message":"Bye."})


@app.route("/pubkey")
def get_pubkey():
    return jsonify({"message":b64encode(PUBLIC_KEY).decode()})


@app.route("/admin/create-user", methods=["POST"])
def admin_create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    return create_user(username, password)


@app.route("/admin/delete-user", methods=["POST"])
def admin_delete_user():
    data = request.get_json()
    username = data.get('username')
    return delete_user(username)


@app.route("/admin/list-users", methods=["GET"])
def admin_list_users():
    return list_users()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_user("admin", "password")
        create_user("guest", "password")

    app.run(host='0.0.0.0', port=1337, debug=True) # TODO: disable
