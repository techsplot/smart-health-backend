# utils/email.py

import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
RESET_LINK_BASE_URL = os.getenv("RESET_LINK_BASE_URL")  # e.g. https://yourfrontend.com/reset-password
EMAIL_FROM = os.getenv("EMAIL_FROM")  # e.g. YourApp <noreply@yourdomain.com>

def send_password_reset_email(to_email: str, token: str):
    """
    Sends a password reset email to the user using Resend.
    """
    reset_link = f"{RESET_LINK_BASE_URL}?token={token}"

    html_content = f"""
    <div style="font-family:sans-serif">
        <h2>Password Reset Request</h2>
        <p>You requested to reset your password. Click the link below to reset it:</p>
        <a href="{reset_link}" style="color:blue;">Reset Password</a>
        <p>This link will expire in 15 minutes. If you didn't request this, you can ignore this email.</p>
    </div>
    """

    try:
        resend.Emails.send({
            "from": EMAIL_FROM,
            "to": [to_email],
            "subject": "Reset Your Password",
            "html": html_content
        })
        print(f"Reset email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send reset email: {e}")
        raise
