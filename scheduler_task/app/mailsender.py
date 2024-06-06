from email.message import EmailMessage
import ssl
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()

def sendEmailToNewUser(receiver,message):
    email_sender = "denememailsender325@gmail.com"
    email_password = os.getenv('APP_PASSWORD')
    subject = "MilesSmiles Account Created"
    email = EmailMessage()
    email['From'] = email_sender
    email['To'] = receiver
    email['Subject'] = subject
    email.set_content(message)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,receiver,email.as_string())