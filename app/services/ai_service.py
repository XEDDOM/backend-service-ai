from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

PROMPT = """
Проанализируй тональность сообщения пользователя (positive, negative, neutral) 
и сгенерируй вежливый, профессиональный ответ на русском языке.
Верни результат СТРОГО в формате JSON: {"sentiment": "...", "reply": "..."}
Сообщение пользователя: "{comment}"
"""

async def analyze_and_generate_reply(comment: str) -> dict:
    fallback_response = {
        "sentiment": "neutral",
        "reply": "Спасибо за ваше обращение! Мы получили ваше сообщение и свяжемся с вами в ближайшее время.",
        "is_fallback": True
    }
    
    if not client:
        logger.warning("OpenAI client not initialized. Using fallback.")
        return fallback_response

    try:
        response = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[{"role": "user", "content": PROMPT.format(comment=comment)}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        import json
        parsed_result = json.loads(result)
        parsed_result["is_fallback"] = False
        return parsed_result
    except Exception as e:
        logger.error(f"AI Service failed: {e}. Triggering fallback.")
        return fallback_response
