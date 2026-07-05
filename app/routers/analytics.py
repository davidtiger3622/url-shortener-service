from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Click, Link, User
from app.schemas import LinkAnalytics

router = APIRouter(prefix="/links", tags=["analytics"])


@router.get("/{short_code}/analytics", response_model=LinkAnalytics)
def get_link_analytics(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = db.query(Link).filter(
        Link.short_code == short_code, Link.owner_id == current_user.id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    total_clicks = db.query(Click).filter(Click.link_id == link.id).count()

    return {
        "short_code": link.short_code,
        "original_url": link.original_url,
        "total_clicks": total_clicks,
        "created_at": link.created_at,
        "expires_at": link.expires_at,
    }
