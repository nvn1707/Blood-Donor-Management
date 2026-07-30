from flask import Blueprint, request, jsonify
from extensions import mysql
import bcrypt

donor_bp = Blueprint("donor_bp", __name__)

# ---------- DONOR REGISTRATION ----------
@donor_bp.route("/register", methods=["POST"])
def register_donor():
    data = request.get_json()

    # Basic validation — make sure required fields are present
    required_fields = ["name", "blood_group", "email", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing field: {field}"}), 400

    name = data["name"]
    blood_group = data["blood_group"]
    phone = data.get("phone", "")
    email = data["email"]
    city = data.get("city", "")
    password = data["password"]

    # Hash the password before storing it — never store plain text passwords
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    cur = mysql.connection.cursor()

    # Check if email is already registered
    cur.execute("SELECT * FROM donors WHERE email = %s", (email,))
    existing_donor = cur.fetchone()
    if existing_donor:
        cur.close()
        return jsonify({"error": "Email already registered"}), 409

    # Insert the new donor
    cur.execute(
        """INSERT INTO donors (name, blood_group, phone, email, password_hash, city)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (name, blood_group, phone, email, password_hash.decode("utf-8"), city)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Donor registered successfully"}), 201
# ---------- DONOR LOGIN ----------
import jwt
import datetime
from flask import current_app

@donor_bp.route("/login", methods=["POST"])
def login_donor():
    data = request.get_json()

    if "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM donors WHERE email = %s", (email,))
    donor = cur.fetchone()
    cur.close()

    if not donor:
        return jsonify({"error": "Invalid email or password"}), 401

    # Check submitted password against the stored hash
    stored_hash = donor["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return jsonify({"error": "Invalid email or password"}), 401

    # Password correct — issue a JWT token valid for 24 hours
    token = jwt.encode(
        {
            "donor_id": donor["donor_id"],
            "email": donor["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "donor": {
            "donor_id": donor["donor_id"],
            "name": donor["name"],
            "email": donor["email"],
            "blood_group": donor["blood_group"]
        }
    }), 200
# ---------- SEARCH AVAILABLE DONORS BY BLOOD GROUP (optionally filter by city) ----------
@donor_bp.route("/search/<blood_group>", methods=["GET"])
def search_donors(blood_group):
    city = request.args.get("city")  # optional query param, e.g. ?city=Chennai

    cur = mysql.connection.cursor()

    if city:
        cur.execute(
            """SELECT donor_id, name, blood_group, phone, email, city, last_donation_date
               FROM donors
               WHERE blood_group = %s AND city = %s AND available = TRUE""",
            (blood_group, city)
        )
    else:
        cur.execute(
            """SELECT donor_id, name, blood_group, phone, email, city, last_donation_date
               FROM donors
               WHERE blood_group = %s AND available = TRUE""",
            (blood_group,)
        )

    donors = cur.fetchall()
    cur.close()

    return jsonify(donors), 200