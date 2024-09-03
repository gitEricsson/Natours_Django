import os

from django.core.mail import EmailMessage, EmailMultiAlternatives
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Util:
    @staticmethod
    def send_email_gmail(data):
        email=EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
            
        email.send()
        
    def send_email_brevo(data):
        msg = EmailMultiAlternatives(data['email_subject'], data['email_body'], "hello@ericsson.io", [data['to_email']])
        # msg.attach_alternative("<html>html body</html>", "text/html")"
        msg.send()