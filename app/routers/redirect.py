from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Click, Link

router = APIRouter(tags=["redirect"])


@router.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link or not link.is_active:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Link has expired")

    click = Click(link_id=link.id)
    db.add(click)
    db.commit()

    return RedirectResponse(url=link.original_url)
