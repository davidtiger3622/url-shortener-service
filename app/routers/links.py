from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

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
