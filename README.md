🚚 RuralDeliver – AI-Based Rural Delivery Management System

An AI-powered smart logistics platform designed to improve delivery operations in rural areas through intelligent route optimization, automated delivery assignment, real-time tracking, and secure authentication.

This project combines FastAPI, Machine Learning, and modern web technologies to build a scalable and efficient delivery ecosystem focused on solving real-world rural logistics challenges.

🌐 Live Demo
🔗 Frontend

🌍 https://ai-based-rural-delivery-management.netlify.app

🔗 Backend API

🌍 https://ruraldeliver-backend.onrender.com

📘 API Documentation

🌍 https://ruraldeliver-backend.onrender.com/docs

🚀 Key Features
🔐 Secure Authentication System
User Registration & Login
JWT-Based Authentication
Email Verification Workflow
Forgot Password with OTP Verification
Password Hashing using bcrypt
Protected API Routes

📦 Smart Order Management
Create and Manage Delivery Orders
Real-Time Order Tracking
Order Status Updates
User Order History
Delivery Agent Assignment

🧠 AI & Machine Learning Features
AI-Based Route Optimization
Automated Delivery Assignment
Delivery Demand Prediction
Smart Logistics Planning
Rural Route Intelligence

🚚 Delivery Management
Delivery Agent Dashboard
Order Pickup & Delivery Workflow
Mark Orders as Delivered
Live Delivery Tracking
Delivery Workflow Automation

📍 Hub Management
Add & Manage Delivery Hubs
Hub-Based Delivery Coordination
Intelligent Order Distribution
Multi-Hub Logistics Support

🛠 Tech Stack
**Backend**
Python
FastAPI
SQLAlchemy ORM
JWT Authentication
MYSQL
**Frontend**
HTML
CSS
JavaScript

Deployment
Render (Backend Deployment)
Netlify (Frontend Deployment)

📂 Project Structure
RuralDeliver/
│
├── backend/
│   ├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── ml_models/
│   ├── database/
│   └── main.py
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── assets/
│   └── index.html
│
├── requirements.txt
├── README.md
└── netlify.toml

**⚙️ Installation & Setup**
1️⃣ Clone Repository
git clone https://github.com/Saurabhkushwaha21/RuralDeliver.git
cd RuralDeliver
2️⃣ Create Virtual Environment
python -m venv venv
Activate Virtual Environment
Windows
venv\Scripts\activate
Linux / Mac
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run Backend Server
uvicorn app.main:app --reload

Backend will run on:

http://127.0.0.1:8000
5️⃣ Access API Docs
http://127.0.0.1:8000/docs

🤖 AI Modules Used
Route Optimization Algorithm
Delivery Prediction Model
Smart Assignment Logic
Logistics Decision Engine

🔒 Security Features
JWT Token Authentication
Password Hashing
Secure API Endpoints
OTP Verification
Email Validation

📸 Project Screenshot
<img width="1917" height="960" alt="RuralDeliver Screenshot" src="https://github.com/user-attachments/assets/264ab19b-e26e-41e1-a3f6-d6488e233b3d" />
<img width="1897" height="937" alt="Screenshot 2026-05-26 003050" src="https://github.com/user-attachments/assets/6d338be6-b446-4d9d-b0af-0e3f13b698cf" />
<img width="1867" height="908" alt="Screenshot 2026-05-26 003118" src="https://github.com/user-attachments/assets/5e175086-4b09-4d2b-8191-22a9cd922d19" />

📈 Future Enhancements
Real-Time GPS Tracking
AI-Based Traffic Prediction
Mobile Application
Multi-Language Support
Advanced Analytics Dashboard
IoT-Based Rural Delivery Monitoring

👨‍💻 Author
Saurabh Kushwaha
Full Stack Developer
AI/ML Enthusiast
FastAPI Developer
