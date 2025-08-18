# import os
# import mandrill
# from dotenv import load_dotenv

# load_dotenv()

# MANDRILL_API_KEY = os.getenv("MANDRILL_API_KEY")

# def send_otp_mail(to_email: str, subject: str, html: str):
#     try:
#         mandrill_client = mandrill.Mandrill(MANDRILL_API_KEY)
#         message = {
#             'from_email': 'madangle356@gmail.com',
#             'subject': subject,
#             'html': html,
#             'to': [{'email': to_email, 'type': 'to'}],
#         }
#         result = mandrill_client.messages.send(message=message)
#         print("Mail Sent:", result)
#         return True
#     except mandrill.Error as e:
#         print("Mandrill Error:", e)
#         return False
# import random

import random
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, body: str):
    """Send an email using Gmail SMTP"""
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())
        server.quit()
        print("✅ Email sent successfully")
        return True
    except Exception as e:
        print("❌ Error:", e)
        return False


def generate_otp(to_email: str):
    """Generate OTP and send via email"""
    otp = str(random.randint(100000, 999999))  # 6-digit OTP
    subject = "Your OTP Code"
    html = f"<h2>Your OTP is: {otp}</h2><p>It will expire in 10 minutes.</p>"

    success = send_email(to_email=to_email, subject=subject, body=html)
    return otp if success else None
