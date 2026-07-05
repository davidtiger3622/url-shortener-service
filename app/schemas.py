from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LinkCreate(BaseModel):
    original_url: str
    expires_at: Optional[datetime] = None


class LinkOut(BaseModel):
    id: int
    short_code: str
    original_url: str
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedLinks(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[LinkOut]


class LinkAnalytics(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    created_at: datetime
    expires_at: Optional[datetime]
