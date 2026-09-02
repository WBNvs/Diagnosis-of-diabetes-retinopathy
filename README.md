# AI-Assisted Diabetic Retinopathy Diagnosis System

A full-stack web application for AI-assisted diabetic retinopathy diagnosis built with Flask, Vue3 and PyTorch.

> Developed as a software engineering and AI course research project at Tongji University.

---

## Overview

This project provides an AI-assisted diagnosis platform for diabetic retinopathy (DR). It combines deep learning segmentation models with a complete web application, allowing users to upload retinal images and receive automated diagnostic results.

This project mainly integrates:

- Deep learning model inference
- Flask backend services
- Vue3 frontend
- RESTful APIs
- MySQL database
- Full-stack deployment

---

## Features

- Upload retinal fundus images
- Automatic lesion segmentation
- AI-assisted diabetic retinopathy diagnosis
- User-friendly web interface
- Database management
- RESTful API communication
- Backend–frontend integration

---

## Tech Stack

### Backend

- Python
- Flask
- PyTorch
- MySQL

### Frontend

- Vue3
- JavaScript
- Vite

### AI

- PyTorch
- MMSegmentation
- Transformer-based feature interaction
- Medical image segmentation

---

## Contributions

This project was completed by a four-member team as part of a software engineering course.

As the project leader, my primary responsibilities included:

- Coordinated system integration as project leader
- Developed Flask backend services
- Designed RESTful APIs
- Built frontend using Vue3
- Integrated deep learning models into a deployable system
- Implemented backend–database communication
- Improved segmentation performance by incorporating Transformer-based feature interaction modules
- Conducted model training and evaluation

---

## Experimental Results

The improved segmentation model was evaluated on public retinal datasets, including:

- IDRiD
- FGADR
- DDR
- TJDR

Performance improvements were achieved compared with the baseline implementation.

*(More experimental details can be found in the project report.)*

---

## Acknowledgements

This project incorporates and extends the following open-source works:

- HACDR-Net
- M2MRF-Lesion-Segmentation

The original repositories belong to their respective authors. We sincerely thank the original authors for making their work publicly available.

Our work focuses on model improvement, system integration, deployment, and AI-assisted diagnosis.

---

## Screenshots

### Doctor's Dashboard

Overview of patient number and To-Do list.

![doctor_dashboard](images/doctor_dashboard.png)

### Doctor's Patient List Page

Overview of patient records and diagnosis history related to the doctor.

![doctor_patient_lists](images/doctor_patient_lists.png)

### Doctor's Diagnosis Page

Details reported by each patient

![doctor_report](images/doctor_report.png)

### Patient's Dashboard

Overview of patient's own records and diagnosis history.

![patient_dashboard](images/patient_dashboard.png)

### Patient's Segmentation Result

Details of each patient report and AI suggestions.

![patient_report](images/patient_report.png)
