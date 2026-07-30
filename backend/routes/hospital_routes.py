from flask import Blueprint, request, jsonify, current_app
from extensions import mysql
import bcrypt
import jwt
import datetime

hospital_bp = Blueprint("hospital_bp", __name__)

# ---------- HOSPITAL REGISTRATION ----------
@hospital_bp.route("/register", methods=["POST"])
def register_hospital():
    data = request.get_json()

    required_fields = ["name", "email", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing field: {field}"}), 400

    name = data["name"]
    city = data.get("city", "")
    contact = data.get("contact", "")
    email = data["email"]
    password = data["password"]

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM hospitals WHERE email = %s", (email,))
    existing_hospital = cur.fetchone()
    if existing_hospital:
        cur.close()
        return jsonify({"error": "Email already registered"}), 409

    cur.execute(
        """INSERT INTO hospitals (name, city, contact, email, password_hash)
           VALUES (%s, %s, %s, %s, %s)""",
        (name, city, contact, email, password_hash.decode("utf-8"))
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Hospital registered successfully"}), 201


# ---------- HOSPITAL LOGIN ----------
@hospital_bp.route("/login", methods=["POST"])
def login_hospital():
    data = request.get_json()

    if "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM hospitals WHERE email = %s", (email,))
    hospital = cur.fetchone()
    cur.close()

    if not hospital:
        return jsonify({"error": "Invalid email or password"}), 401

    stored_hash = hospital["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return jsonify({"error": "Invalid email or password"}), 401

    token = jwt.encode(
        {
            "hospital_id": hospital["hospital_id"],
            "email": hospital["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "hospital": {
            "hospital_id": hospital["hospital_id"],
            "name": hospital["name"],
            "email": hospital["email"],
            "city": hospital["city"]
        }
    }), 200