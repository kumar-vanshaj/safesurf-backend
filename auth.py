from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from db import get_db

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = generate_password_hash(data["password"])

    try:
        conn = get_db()
        conn.execute("INSERT INTO users (email, password) VALUES (?,?)",
                     (email, password))
        conn.commit()
        return jsonify({"msg": "User registered"}), 201
    except:
        return jsonify({"msg": "User already exists"}), 400


@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    if user and check_password_hash(user[2], password):
        token = create_access_token(identity=str(user[0]))
        return jsonify(access_token=token)

    return jsonify({"msg": "Invalid credentials"}), 401
