import resend
import os
from dotenv import load_dotenv
from resend.exceptions import ResendError

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

def send_mail(to: str, subject: str, html: str):
    try:
        response = resend.Emails.send({
            "from": "akhilappuyeroor@gmail.com",
            "to": to,
            "subject": subject,
            "html": html
        })
        print("Email sent successfully:", response)
        return response
    except ResendError as e:
        print("ResendError occurred:")
        print("Message:", str(e))
        print("Type:", getattr(e, 'type', 'N/A'))
        print("Code:", getattr(e, 'code', 'N/A'))
        return None
