import os
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MAILCHIMP_API_KEY")
SERVER_PREFIX = os.getenv("MAILCHIMP_SERVER")
SENDER_EMAIL = os.getenv("MAILCHIMP_SENDER_EMAIL")

client = MailchimpMarketing.Client()
client.set_config({
    "api_key": API_KEY,
    "server": SERVER_PREFIX
})

def send_otp_mail(to_email: str, subject: str, html: str):
    try:
        # Mailchimp doesn't have a direct send-email API for transactional emails.
        # But if you use Mandrill (Mailchimp transactional) or campaigns, you can send email.
        # Here we simulate sending via adding a new campaign and sending a test email
        response = client.ping.get()  # simple ping to verify
        print("Mailchimp API Ping:", response)
        # For production, integrate Mandrill for sending transactional OTP emails
        print(f"Simulating sending email to {to_email}: {subject} / {html}")
        return True
    except ApiClientError as e:
        print("Mailchimp API Error:", e.text)
        return False
