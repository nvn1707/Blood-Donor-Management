from flask import Blueprint, request, jsonify
from extensions import mysql

request_bp = Blueprint("request_bp", __name__)

# ---------- CREATE A BLOOD REQUEST (hospital posts this) ----------
@request_bp.route("/create", methods=["POST"])
def create_request():
    data = request.get_json()

    required_fields = ["hospital_id", "blood_group", "units_needed"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing field: {field}"}), 400

    hospital_id = data["hospital_id"]
    blood_group = data["blood_group"]
    units_needed = data["units_needed"]
    urgency = data.get("urgency", "Medium")  # Low, Medium, High

    cur = mysql.connection.cursor()

    # Confirm the hospital actually exists before creating a request for it
    cur.execute("SELECT * FROM hospitals WHERE hospital_id = %s", (hospital_id,))
    hospital = cur.fetchone()
    if not hospital:
        cur.close()
        return jsonify({"error": "Hospital not found"}), 404

    cur.execute(
        """INSERT INTO blood_requests (hospital_id, blood_group, units_needed, urgency)
           VALUES (%s, %s, %s, %s)""",
        (hospital_id, blood_group, units_needed, urgency)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Blood request created successfully"}), 201


# ---------- VIEW ALL OPEN BLOOD REQUESTS ----------
@request_bp.route("/all", methods=["GET"])
def get_all_requests():
    cur = mysql.connection.cursor()
    cur.execute(
        """SELECT br.request_id, br.blood_group, br.units_needed, br.urgency,
                  br.status, br.created_at, h.name AS hospital_name, h.city
           FROM blood_requests br
           JOIN hospitals h ON br.hospital_id = h.hospital_id
           WHERE br.status = 'Open'
           ORDER BY br.created_at DESC"""
    )
    requests_list = cur.fetchall()
    cur.close()

    return jsonify(requests_list), 200


# ---------- FIND REQUESTS MATCHING A SPECIFIC BLOOD GROUP ----------
@request_bp.route("/match/<blood_group>", methods=["GET"])
def match_requests(blood_group):
    cur = mysql.connection.cursor()
    cur.execute(
        """SELECT br.request_id, br.blood_group, br.units_needed, br.urgency,
                  br.status, br.created_at, h.name AS hospital_name, h.city
           FROM blood_requests br
           JOIN hospitals h ON br.hospital_id = h.hospital_id
           WHERE br.blood_group = %s AND br.status = 'Open'
           ORDER BY br.urgency DESC, br.created_at DESC""",
        (blood_group,)
    )
    matches = cur.fetchall()
    cur.close()

    return jsonify(matches), 200