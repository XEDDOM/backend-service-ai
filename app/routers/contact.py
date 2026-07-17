from fastapi import APIRouter, Request
from app.schemas.contact import ContactRequest, ContactResponse
from app.services.contact_service import process_contact_form
from app.utils.rate_limiter import check_rate_limit

router = APIRouter()

@router.post("/api/contact", response_model=ContactResponse, status_code=200)
async def submit_contact_form(data: ContactRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)
    
    result = await process_contact_form(
        name=data.name,
        phone=data.phone,
        email=data.email,
        comment=data.comment
    )
    
    return ContactResponse(
        status="success",
        message="Ваша заявка успешно отправлена!",
        ai_sentiment=result["ai_sentiment"],
        ai_generated_reply=result["ai_generated_reply"]
    )

@router.get("/api/health")
async def health_check():
    return {"status": "ok"}

@router.get("/api/metrics")
async def get_metrics():
    from app.repositories.file_repository import get_stats
    return get_stats()
