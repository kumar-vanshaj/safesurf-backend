from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask import send_from_directory

from auth import auth
from db import get_db, get_lock,init_db
from nlp.analyzer import analyze_text
from flask_cors import CORS

import threading

db_lock = threading.Lock()
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "safesurf-secret"
CORS(app)
jwt = JWTManager(app)
app.register_blueprint(auth)

init_db()

@app.route("/activity", methods=["POST"])
@jwt_required()
def activity():
    
    user_id = int(get_jwt_identity())
    data = request.get_json(force=True)

    url = data["url"]
    text = data["text"]

    result = analyze_text(text)

    conn = get_db()
    lock = get_lock()

    with lock:
        conn.execute(
            """
            INSERT INTO activities (user_id, url, text, risk_score)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, url, text, result["final_score"])
        )

    return jsonify(result)





@app.route("/activities", methods=["GET"])
@jwt_required()
def get_activities():
    user_id = int(get_jwt_identity())
    conn = get_db()
    lock = get_lock()

    with lock:
        rows = conn.execute(
            "SELECT url, risk_score, timestamp FROM activities WHERE user_id=?",
            (user_id,)
        ).fetchall()

    return jsonify(rows)


    
@app.route("/parent/activities", methods=["GET"])
@jwt_required()
def parent_activities():
    user_id = int(get_jwt_identity())
    conn = get_db()

    rows = conn.execute("""
        SELECT url, risk_score, timestamp
        FROM activities
        WHERE user_id=?
        ORDER BY timestamp DESC
        LIMIT 100
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([
        {
            "url": r[0],
            "risk": r[1],
            "time": r[2]
        } for r in rows
    ])
@app.route("/")
def parent_login():
    return send_from_directory(".", "index.html")
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = data["password"]

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = get_db()
    conn.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)",
        (email, hashed)
    )
    conn.commit()

    return jsonify({"msg": "user created"}), 201
    from flask import send_from_directory

@app.route("/register-page")
def register_page():
    return send_from_directory(".", "register.html")
from flask import send_from_directory

@app.route("/dashboard/<path:path>")
def dashboard_files(path):
    return send_from_directory("dashboard", path)

from flask import render_template

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")



if __name__ == "__main__":
    app.run()

