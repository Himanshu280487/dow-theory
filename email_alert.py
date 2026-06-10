import os
import smtplib
from email.mime.text import MIMEText


def send_email(subject, body):

    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    if not sender or not password or not receiver:
        print("Email credentials not configured")
        return

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:

        with smtplib.SMTP("smtp.gmail.com", 587) as server:

            server.starttls()
            server.login(sender, password)

            server.sendmail(
                sender,
                receiver,
                msg.as_string()
            )

        print("EMAIL SENT SUCCESSFULLY")

    except Exception as e:

        print("EMAIL ERROR:", str(e))
