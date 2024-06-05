from flask import Flask, redirect, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.getcwd() + "/db/users.db"

db = SQLAlchemy()
db.init_app(app)

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

# TODO: Prevent a user from deleting themselves
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

@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
        return jsonify({"message":f"Hello {username}."})
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return jsonify({"message":"Please log out first."})

    if request.method == "GET":
        return jsonify({"message":"Please login."})

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        session["username"] = username
        return jsonify({"message":f"Hello {username}."})
    else:
        return jsonify({"message":"Login failed."}), 401

# TODO: Invalidate session token
@app.route("/logout")
def logout():
    session.pop("username", None)
    return jsonify({"message":"Bye."})

@app.route("/jobs", methods=["GET"])
def jobs():
    if "username" not in session:
        return redirect("/login")

    return jsonify({"message":"No active jobs yet."})

@app.route("/admin", methods=["GET"])
def is_admin():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    if username != "admin":
        return jsonify({"message":"Only admin is allowed."}), 401
    else:
        return jsonify({"message":"Hello admin."}), 200

@app.route("/admin/create-user", methods=["POST"])
def admin_create_user():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    if username != "admin":
        return jsonify({"message":"Only admin is allowed."})

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    return create_user(username, password)

@app.route("/admin/delete-user", methods=["POST"])
def admin_delete_user():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    if username != "admin":
        return jsonify({"message":"Only admin is allowed."})

    data = request.get_json()
    username = data.get('username')
    return delete_user(username)

@app.route("/admin/list-users", methods=["GET"])
def admin_list_users():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    if username != "admin":
        return jsonify({"message":"Only admin is allowed."})

    return list_users()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_user("admin", "password")
        create_user("guest", "password")

    app.run(host='0.0.0.0', port=1337, debug=True) # TODO: disable
