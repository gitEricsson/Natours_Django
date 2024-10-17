import os
import threading

from django.core.mail import EmailMessage, EmailMultiAlternatives
from dotenv import load_dotenv
from rest_framework.exceptions import APIException

load_dotenv()

class AppError(APIException):
    def __init__(self, detail, status_code):
        self.status_code = status_code
        super().__init__(detail)

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email_gmail(data):
        email=EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
            
        email.send()
        
    def send_email_brevo(data):
        msg = EmailMultiAlternatives(data['email_subject'], data['email_body'], "hello@ericsson.io", [data['to_email']])
        msg.attach_alternative(data['email_html'], "text/html")
        EmailThread(msg).start()