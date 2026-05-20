import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_verification_email(to_email, token):

    link = f"https://ai-based-rural-delivery-management-system.onrender.com/api/auth/verify-email?token={token}"
    
    msg = MIMEText(f"""
Welcome to RuralDeliver 🚴

Click below to verify your email:

{link}
""")

    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    msg["Subject"] = "Verify your email"
    msg["From"] = email_user
    msg["To"] = to_email

    if not email_user or not email_pass:
        print("❌ EMAIL ENV NOT LOADED")
        return

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email failed:", e)