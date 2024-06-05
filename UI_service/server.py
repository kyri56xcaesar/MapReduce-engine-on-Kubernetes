from flask import Flask, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/users.db"

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
        print("User already exists.") # TODO: Show to user
        return

    user = User(username, password)
    db.session.add(user)
    db.session.commit()

def list_users():
    # TODO
    users = User.query.all()
    print(users)

def update_user(username, password):
    # TODO
    db.session.commit()

def delete_user(username):
    db.session.delete(username)
    db.session.commit()

@app.route("/")
def index():
    if "username" in session:
        redirect("/console")
    return redirect("/login")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    print(user)

    if user and user.password == password:
        session["username"] = username
        return redirect("/console")
    else:
        return redirect("/")

@app.route("/console", methods=["GET", "POST"])
def console():
    if "username" in session:
        username = session["username"]
        if request.method == 'POST':
            option = request.form.get('option')
            if option == None or option == "":
                return "Invalid option."
            else:
                option = int(option)
                if option == 1:
                    return "No active jobs yet."
                elif option == 2:
                    if username == "admin":
                        return redirect("/admin")
                    else:
                        return "Only admin is allowed."
                elif option == 3:
                    return "Bye."
                else:
                    return "Invalid option."
        else:
            return f"Hello {username}"
    else:
        return redirect("/")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect('/')

@app.route("/admin")
def admin():
    if "username" in session:
        username = session["username"]
        return "Adm1n p4n3l?? 0mg!"
    else:
        return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_user("admin", "password")

    app.run(host='0.0.0.0', port=1337)
