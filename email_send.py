import os
from typing import Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import resend
from pydantic import BaseModel, EmailStr
import psycopg2

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(',')

# debugging
print(origins)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

class EmailAddr(BaseModel):
    email: EmailStr

@app.post("/signup")
def send_mail(target_email: EmailAddr) -> Dict:
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO email_list (email) VALUES (%s) ON CONFLICT (email) DO NOTHING", (target_email.email,))
        is_new = cursor.rowcount == 1

        should_send = is_new
        if not is_new:
            cursor.execute("SELECT sent FROM email_list WHERE email = %s", (target_email.email,))
            row = cursor.fetchone()
            should_send = not row[0] # send only if 'sent' is False

        if should_send:
            params: resend.Emails.SendParams = {
                "from": "SnagAI <noreply@snag-ai.app>",
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
            resend.Emails.send(params)
            cursor.execute("UPDATE email_list SET sent = TRUE WHERE email = %s", (target_email.email,))

        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

handler = Mangum(app, api_gateway_base_path="/prod")