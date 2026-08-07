## 🌐 Live Demo

- **Website:** https://blooddonormanage.netlify.app
- **Backend API:** https://blood-donor-management-ypz2.onrender.com

> Note: The backend is hosted on Render's free tier, which sleeps after ~15 minutes of inactivity. The first request may take 20–50 seconds to wake it up — subsequent requests are fast.

**Test accounts:**
| Role | Email / Username | Password |
|------|-------------------|----------|
| Admin | `admin` | `admin1234` |

---
# 🩸 Blood Donor Management System

A full-stack web application that connects blood donors with hospitals in need, built as a cloud computing course project. The system supports donor and hospital registration, blood request posting and matching by blood group, donation tracking, and an admin dashboard.

## Tech Stack

- **Backend:** Python (Flask)
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Authentication:** JWT (JSON Web Tokens) + bcrypt password hashing
- **Cloud Platform (designed for):** AWS — RDS (database), EC2 (backend hosting), S3 (frontend hosting)

## Features

- **Donor:** register, log in, search/view matching open blood requests by blood group
- **Hospital:** register, log in, create blood requests with urgency levels
- **Donations:** record a donation against a request — automatically updates donor availability and marks the request as fulfilled once enough units are collected
- **Admin:** log in, view all donors/hospitals/requests, delete requests

## Project Structure

```
blood-donor-management/
├── backend/
│   ├── app.py                  # Flask app entry point, registers all blueprints
│   ├── config.py                # Loads DB config from environment variables
│   ├── extensions.py            # Shared MySQL extension instance
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Template for environment variables
│   └── routes/
│       ├── donor_routes.py      # Donor register/login/search
│       ├── hospital_routes.py   # Hospital register/login
│       ├── request_routes.py    # Create/view/match blood requests
│       ├── donation_routes.py   # Record donations
│       └── admin_routes.py      # Admin register/login/view-all/delete
├── frontend/
│   ├── index.html               # Landing page
│   ├── register.html            # Donor/Hospital registration
│   ├── login.html               # Donor/Hospital login
│   ├── dashboard.html           # Donor dashboard (profile + matching requests)
│   ├── admin.html                # Admin panel
│   └── style.css
└── database/
    └── schema.sql               # (see Database Schema section below)
```

## Database Schema

5 tables in MySQL: `donors`, `hospitals`, `blood_requests`, `donations`, `admins`.

```sql
CREATE DATABASE IF NOT EXISTS blood_donor_db;
USE blood_donor_db;

CREATE TABLE donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    city VARCHAR(50),
    last_donation_date DATE,
    available BOOLEAN DEFAULT TRUE
);

CREATE TABLE hospitals (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    contact VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255)
);

CREATE TABLE blood_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT,
    blood_group VARCHAR(5) NOT NULL,
    units_needed INT NOT NULL,
    urgency ENUM('Low','Medium','High') DEFAULT 'Medium',
    status ENUM('Open','Fulfilled','Cancelled') DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
);

CREATE TABLE donations (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    request_id INT,
    donation_date DATE,
    units INT,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id),
    FOREIGN KEY (request_id) REFERENCES blood_requests(request_id)
);

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255)
);
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/donors/register` | Register a new donor |
| POST | `/api/donors/login` | Donor login (returns JWT) |
| GET | `/api/donors/search/<blood_group>` | Search available donors by blood group |
| POST | `/api/hospitals/register` | Register a new hospital |
| POST | `/api/hospitals/login` | Hospital login (returns JWT) |
| POST | `/api/requests/create` | Create a new blood request |
| GET | `/api/requests/all` | View all open blood requests |
| GET | `/api/requests/match/<blood_group>` | View open requests matching a blood group |
| POST | `/api/donations/record` | Record a donation against a request |
| POST | `/api/admin/register` | Register an admin |
| POST | `/api/admin/login` | Admin login (returns JWT) |
| GET | `/api/admin/donors` | View all donors |
| GET | `/api/admin/hospitals` | View all hospitals |
| GET | `/api/admin/requests` | View all requests (any status) |
| DELETE | `/api/admin/requests/<id>` | Delete a request |

## Setup & Run Locally

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat      # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file in `backend/` (copy `.env.example`) and fill in your local MySQL credentials:
```
MYSQL_HOST=127.0.0.1
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=blood_donor_db
MYSQL_PORT=3306
SECRET_KEY=your_secret_key
```

Create the database and tables in MySQL using the schema above, then run:
```bash
python app.py
```
Backend runs at `http://127.0.0.1:5000`.

### 2. Frontend

Just open `frontend/index.html` in your browser (no build step needed — plain HTML/CSS/JS). Make sure the backend is running first, since the frontend calls it directly.

## Cloud Deployment Architecture (AWS)

Designed to deploy as follows:
- **Amazon RDS (MySQL)** — hosts the production database
- **Amazon EC2** — hosts the Flask backend (via `pm2` or `gunicorn`)
- **Amazon S3 (+ CloudFront)** — hosts the static frontend files
- **IAM** — least-privilege access control for deployment resources
- **CloudWatch** — logging/monitoring for the EC2 instance

## Security Notes

- Passwords are hashed with **bcrypt** before storage — never stored in plain text
- Authentication uses **JWT tokens** with 24-hour expiry
- `.env` file (containing real credentials) is excluded from version control via `.gitignore`

## Author

Built by [nvn1707](https://github.com/nvn1707) as a cloud computing course project.
