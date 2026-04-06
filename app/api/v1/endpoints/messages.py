import uuid
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Idea, Message, User
from app.schemas import MessageCreate, MessageOut
from app.core.dependencies import get_current_user
from app.services.ai_service import stream_ai_response

router = APIRouter(tags=["Messages"])


async def save_assistant_message(idea_id: uuid.UUID, content: str):
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        message = Message(idea_id=idea_id, role="assistant", content=content)
        db.add(message)
        await db.commit()


@router.get("/ideas/{idea_id}/messages", response_model=list[MessageOut])
async def list_messages(
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

    result = await db.execute(
        select(Message)
        .where(Message.idea_id == idea_id)
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()


@router.post("/ideas/{idea_id}/messages")
async def create_message(
    idea_id: uuid.UUID,
    payload: MessageCreate,
    background_tasks: BackgroundTasks,
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

    user_message = Message(idea_id=idea_id, role="user", content=payload.content)
    db.add(user_message)
    await db.commit()

    history_result = await db.execute(
        select(Message)
        .where(Message.idea_id == idea_id)
        .order_by(Message.created_at.asc())
    )
    history = [
        {"role": m.role, "content": m.content} for m in history_result.scalars().all()
    ]

    full_response = []

    async def generate():
        async for chunk in stream_ai_response(idea.title, idea.description, history):
            import json as _json

            try:
                data = _json.loads(chunk.replace("data: ", "").strip())
                if "token" in data:
                    full_response.append(data["token"])
            except Exception:
                pass
            yield chunk

        if full_response:
            background_tasks.add_task(
                save_assistant_message,
                idea_id,
                "".join(full_response),
            )

    return StreamingResponse(generate(), media_type="text/event-stream")
