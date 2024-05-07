from django.conf import settings
from django.core.mail import send_mail

def send_email_to_user(otp,receiver,otp_type):
    subject="Reset Password Otp"
    message=f"You {otp_type} otp is :- {otp} "
    from_email=settings.EMAIL_HOST_USER
    send_mail(subject,message,from_email,receiver)
   