from app.service import send_otp_mail   # import your function if in send_mail.py

# Test email details
to_email = "akhilappuyeroor@gmail.com"
subject = "OTP Verification Test"
html = "<h1>Your OTP is 123456</h1>"

if send_otp_mail(to_email, subject, html):
    print("✅ Test email sent successfully!")
else:
    print("❌ Failed to send email.")
