from flask import Blueprint, request, jsonify
from extensions import mysql
import datetime

donation_bp = Blueprint("donation_bp", __name__)

# ---------- RECORD A DONATION (donor donates against a specific request) ----------
@donation_bp.route("/record", methods=["POST"])
def record_donation():
    data = request.get_json()

    required_fields = ["donor_id", "request_id", "units"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing field: {field}"}), 400

    donor_id = data["donor_id"]
    request_id = data["request_id"]
    units = data["units"]
    donation_date = data.get("donation_date", datetime.date.today().isoformat())

    cur = mysql.connection.cursor()

    # Confirm donor and request both exist
    cur.execute("SELECT * FROM donors WHERE donor_id = %s", (donor_id,))
    donor = cur.fetchone()
    cur.execute("SELECT * FROM blood_requests WHERE request_id = %s", (request_id,))
    blood_request = cur.fetchone()

    if not donor or not blood_request:
        cur.close()
        return jsonify({"error": "Donor or request not found"}), 404

    # Insert the donation record
    cur.execute(
        """INSERT INTO donations (donor_id, request_id, donation_date, units)
           VALUES (%s, %s, %s, %s)""",
        (donor_id, request_id, donation_date, units)
    )

    # Update donor's last donation date, and mark them briefly unavailable
    cur.execute(
        "UPDATE donors SET last_donation_date = %s, available = FALSE WHERE donor_id = %s",
        (donation_date, donor_id)
    )

    # Check total units donated so far against this request
    cur.execute(
        "SELECT SUM(units) AS total_units FROM donations WHERE request_id = %s",
        (request_id,)
    )
    total = cur.fetchone()
    total_units = total["total_units"] or 0

    # If enough units collected, mark the request as fulfilled
    if total_units >= blood_request["units_needed"]:
        cur.execute(
            "UPDATE blood_requests SET status = 'Fulfilled' WHERE request_id = %s",
            (request_id,)
        )

    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Donation recorded successfully"}), 201