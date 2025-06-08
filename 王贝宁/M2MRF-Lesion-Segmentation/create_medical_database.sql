-- Temporarily relax sql_mode to avoid strict mode errors
SET SESSION sql_mode = '';

-- Drop and recreate the database to start fresh
DROP DATABASE IF EXISTS MedicalDB;
CREATE DATABASE MedicalDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE MedicalDB;

-- Create User table
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor') NOT NULL
);

-- Create Patient table
CREATE TABLE Patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    gender ENUM('male', 'female'),
    date_of_birth DATE NOT NULL,
    contact_info VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- Create Doctor table
CREATE TABLE Doctor (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- Create Diagnose table
CREATE TABLE Diagnose (
    diagnosis_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    diagnosis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_path VARCHAR(255),
    confirmed BOOLEAN DEFAULT FALSE,
    diagnose_date DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id) ON DELETE CASCADE
);

-- Create Lesion table
CREATE TABLE Lesion (
    lesion_id INT PRIMARY KEY AUTO_INCREMENT,
    diagnosis_id INT NOT NULL,
    FOREIGN KEY (diagnosis_id) REFERENCES Diagnose(diagnosis_id) ON DELETE CASCADE
);