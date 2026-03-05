from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS

import bcrypt

from auth import auth
from db import get_db, get_lock, init_db
from nlp.analyzer import analyze_text

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "safesurf-secret"

CORS(app)
jwt = JWTManager(app)

app.register_blueprint(auth)

init_db()


# ------------------ ACTIVITY ------------------

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

        conn.execute(
            "UPDATE stats SET pages_analyzed = pages_analyzed + 1 WHERE id=1"
        )

        if result["risk_level"] == "FLAGGED":
            conn.execute(
                "UPDATE stats SET blocked_pages = blocked_pages + 1 WHERE id=1"
            )

        conn.commit()

    return jsonify(result)


# ------------------ USER ACTIVITIES ------------------

@app.route("/activities", methods=["GET"])
@jwt_required()
def get_activities():

    user_id = int(get_jwt_identity())
    conn = get_db()

    rows = conn.execute(
        "SELECT url, risk_score, timestamp FROM activities WHERE user_id=?",
        (user_id,)
    ).fetchall()

    return jsonify(rows)


# ------------------ PARENT VIEW ------------------

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

    return jsonify([
        {
            "url": r[0],
            "risk": r[1],
            "time": r[2]
        } for r in rows
    ])


# ------------------ REGISTER ------------------

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


# ------------------ PAGES ------------------

@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/register-page")
def register_page():
    return send_from_directory(".", "register.html")


@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@app.route("/dashboard/<path:path>")
def dashboard_files(path):
    return send_from_directory("dashboard", path)


# ------------------ STATS ------------------

@app.route("/stats")
def stats():

    conn = get_db()

    row = conn.execute(
        "SELECT pages_analyzed, blocked_pages FROM stats WHERE id=1"
    ).fetchone()

    users = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    return jsonify({
        "pages_analyzed": row[0],
        "blocked_pages": row[1],
        "registered_users": users
    })


if __name__ == "__main__":
    app.run()
