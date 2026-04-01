import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Idea, User
from app.schemas import IdeaCreate, IdeaUpdate, IdeaOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/ideas", tags=["Ideas"])


@router.post("", response_model=IdeaOut, status_code=status.HTTP_201_CREATED)
async def create_idea(
    payload: IdeaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    idea = Idea(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
    )
    db.add(idea)
    await db.flush()
    await db.refresh(idea)
    return idea


@router.get("", response_model=list[IdeaOut])
async def list_ideas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Idea)
        .where(Idea.user_id == current_user.id)
        .order_by(Idea.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{idea_id}", response_model=IdeaOut)
async def get_idea(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.user_id == current_user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found"
        )
    return idea


@router.patch("/{idea_id}", response_model=IdeaOut)
async def update_idea(
    idea_id: uuid.UUID,
    payload: IdeaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.user_id == current_user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found"
        )
    if payload.title is not None:
        idea.title = payload.title
    if payload.description is not None:
        idea.description = payload.description
    await db.flush()
    await db.refresh(idea)
    return idea


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.user_id == current_user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found"
        )
    await db.delete(idea)
