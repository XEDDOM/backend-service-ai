import smtplib, logging
from email.mime.text import MIMEText
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_emails(name: str, email: str, comment: str, ai_reply: str):
    subject_owner = f"Новая заявка с лендинга от {name}"
    body_owner = f"Имя: {name}\nТелефон: {email}\nEmail: {email}\n\nКомментарий:\n{comment}\n\nAI Ответ:\n{ai_reply}"
    
    subject_user = "Мы получили ваше обращение"
    body_user = f"Здравствуйте, {name}!\n\n{ai_reply}\n\nС уважением, команда разработчиков."

    if settings.EMAIL_MODE == "MOCK":
        logger.info(f"MOCK EMAIL TO OWNER ({settings.OWNER_EMAIL}):\n{body_owner}")
        logger.info(f"MOCK EMAIL TO USER ({email}):\n{body_user}")
        return True

    try:
        msg_owner = MIMEText(body_owner)
        msg_owner['Subject'] = subject_owner
        msg_owner['From'] = settings.SMTP_USER
        msg_owner['To'] = settings.OWNER_EMAIL
        
        msg_user = MIMEText(body_user)
        msg_user['Subject'] = subject_user
        msg_user['From'] = settings.SMTP_USER
        msg_user['To'] = email

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg_owner)
            server.send_message(msg_user)
        return True
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False
