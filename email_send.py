import os
from typing import Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import resend
from pydantic import BaseModel, EmailStr


load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

app = FastAPI()

class EmailAddr(BaseModel):
    email: EmailStr

@app.post("/")
def send_mail(target_email: EmailAddr) -> Dict:
    try:
        params: resend.Emails.SendParams = {
            "from": "SnagAI <onboarding@resend.dev>",
            "to": [target_email.email],
            "subject": "You're on the list — thanks for signing up for SnagAI",
            "html": """
                <p>Hi there,</p>
                <p>Thank you for signing up for early access to SnagAI! We're thrilled to have you on board.</p>
                <p>SnagAI uses AI to automatically hunt down the best deals on the internet for items on your wishlist — so you never have to overpay again. We're working hard to get the app ready, and you'll be among the first to know when it's live on the App Store.</p>
                <p>We'll reach out as soon as your spot is ready. In the meantime, feel free to reply to this email if you have any questions or just want to say hi.</p>
                <p>Thanks again for your support — it means a lot.</p>
                <p>The SnagAI Team</p>
            """,
        }
        email: resend.Emails.SendResponse = resend.Emails.send(params)
        return email
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))