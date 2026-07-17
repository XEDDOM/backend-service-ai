import logging
from app.services.ai_service import analyze_and_generate_reply
from app.services.email_service import send_emails
from app.repositories.file_repository import save_stats

logger = logging.getLogger(__name__)

async def process_contact_form(name: str, phone: str, email: str, comment: str) -> dict:
    ai_result = await analyze_and_generate_reply(comment)
    
    email_sent = await send_emails(name, email, comment, ai_result["reply"])
    
    save_stats(is_success=email_sent, used_fallback=ai_result.get("is_fallback", False))
    
    if not email_sent:
        logger.error(f"Failed to send emails for user {email}, but request processed.")

    return {
        "ai_sentiment": ai_result["sentiment"],
        "ai_generated_reply": ai_result["reply"],
        "email_sent": email_sent
    }
