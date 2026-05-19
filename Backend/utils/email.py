import os
import smtplib
from email.mime.text import MIMEText

def send_verification_email(to_email, token):

    link = f"http://127.0.0.1:5500/pages/verify.html?token={token}"
    
    msg = MIMEText(f"""
    Welcome to RuralDeliver 🚴

    Click below to verify your email:

    {link}
    """)

    msg["Subject"] = "Verify your email"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")

        print("EMAIL USER:", email_user)
        print("EMAIL PASS LOADED:", bool(email_pass))

        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email failed:", str(e))