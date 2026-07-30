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