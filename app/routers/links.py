from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi.responses import RedirectResponse
from app.models import Click
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Link, User
from app.schemas import LinkCreate, LinkOut, PaginatedLinks
from app.utils import generate_short_code

router = APIRouter(prefix="/links", tags=["links"])


@router.post("", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
def create_link(
    link_in: LinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    code = generate_short_code()
    while db.query(Link).filter(Link.short_code == code).first():
        code = generate_short_code()

    new_link = Link(
        short_code=code,
        original_url=link_in.original_url,
        owner_id=current_user.id,
        expires_at=link_in.expires_at,
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

@router.get("", response_model=PaginatedLinks)
def list_links(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Link).filter(Link.owner_id == current_user.id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/{short_code}", include_in_schema=True)
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
