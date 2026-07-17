from pydantic import BaseModel, EmailStr, Field

class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Имя пользователя")
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{10,14}$', description="Телефон в формате +1234567890")
    email: EmailStr = Field(..., description="Email пользователя")
    comment: str = Field(..., min_length=10, max_length=1000, description="Комментарий")

class ContactResponse(BaseModel):
    status: str
    message: str
    ai_sentiment: str | None = None
    ai_generated_reply: str | None = None
