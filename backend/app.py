from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import mysql
app = Flask(__name__)
app.config.from_object(Config)
app.config["MYSQL_HOST"] = Config.MYSQL_HOST
app.config["MYSQL_USER"] = Config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = Config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = Config.MYSQL_DB
app.config["MYSQL_PORT"] = Config.MYSQL_PORT
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql.init_app(app)
CORS(app)
@app.route("/")
def home():
    return {"status": "Blood Donor Management API is running"}
from routes.donor_routes import donor_bp
app.register_blueprint(donor_bp, url_prefix="/api/donors")
from routes.hospital_routes import hospital_bp
app.register_blueprint(hospital_bp, url_prefix="/api/hospitals")
from routes.request_routes import request_bp
app.register_blueprint(request_bp, url_prefix="/api/requests")
from routes.donation_routes import donation_bp
app.register_blueprint(donation_bp, url_prefix="/api/donations")
from routes.admin_routes import admin_bp
app.register_blueprint(admin_bp, url_prefix="/api/admin")
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)