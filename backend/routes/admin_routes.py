from flask import Blueprint, request, jsonify, current_app
from extensions import mysql
import bcrypt
import jwt
import datetime

admin_bp = Blueprint("admin_bp", __name__)

# ---------- ADMIN REGISTRATION (only needed once, to create the first admin) ----------
@admin_bp.route("/register", methods=["POST"])
def register_admin():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400

    username = data["username"]
    password = data["password"]

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admins WHERE username = %s", (username,))
    if cur.fetchone():
        cur.close()
        return jsonify({"error": "Username already exists"}), 409

    cur.execute(
        "INSERT INTO admins (username, password_hash) VALUES (%s, %s)",
        (username, password_hash.decode("utf-8"))
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Admin registered successfully"}), 201


# ---------- ADMIN LOGIN ----------
@admin_bp.route("/login", methods=["POST"])
def login_admin():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400

    username = data["username"]
    password = data["password"]

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admins WHERE username = %s", (username,))
    admin = cur.fetchone()
    cur.close()

    if not admin:
        return jsonify({"error": "Invalid username or password"}), 401

    stored_hash = admin["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return jsonify({"error": "Invalid username or password"}), 401

    token = jwt.encode(
        {
            "admin_id": admin["admin_id"],
            "username": admin["username"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"message": "Login successful", "token": token}), 200


# ---------- VIEW ALL DONORS ----------
@admin_bp.route("/donors", methods=["GET"])
def get_all_donors():
    cur = mysql.connection.cursor()
    cur.execute("SELECT donor_id, name, blood_group, phone, email, city, last_donation_date, available FROM donors")
    donors = cur.fetchall()
    cur.close()
    return jsonify(donors), 200


# ---------- VIEW ALL HOSPITALS ----------
@admin_bp.route("/hospitals", methods=["GET"])
def get_all_hospitals():
    cur = mysql.connection.cursor()
    cur.execute("SELECT hospital_id, name, city, contact, email FROM hospitals")
    hospitals = cur.fetchall()
    cur.close()
    return jsonify(hospitals), 200


# ---------- VIEW ALL BLOOD REQUESTS (any status) ----------
@admin_bp.route("/requests", methods=["GET"])
def get_all_requests_admin():
    cur = mysql.connection.cursor()
    cur.execute(
        """SELECT br.request_id, br.blood_group, br.units_needed, br.urgency,
                  br.status, br.created_at, h.name AS hospital_name, h.city
           FROM blood_requests br
           JOIN hospitals h ON br.hospital_id = h.hospital_id
           ORDER BY br.created_at DESC"""
    )
    requests_list = cur.fetchall()
    cur.close()
    return jsonify(requests_list), 200


# ---------- DELETE A BLOOD REQUEST ----------
@admin_bp.route("/requests/<int:request_id>", methods=["DELETE"])
def delete_request(request_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM blood_requests WHERE request_id = %s", (request_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Request deleted successfully"}), 200