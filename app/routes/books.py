from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.auth import User, get_current_user
from app.database import SessionDep
from app.models import Book
from app.schemas import BookDetailsRes, BookReq, BookReqPartial, BookSummaryRes

router = APIRouter(prefix="/books", tags=["Book"])


@router.get("/", response_model=list[BookSummaryRes])
async def get_books(session: SessionDep):
    stmt = select(Book)
    return (await session.execute(stmt)).scalars().all()


@router.get("/{id}", response_model=BookDetailsRes)
async def get_book(id: int, session: SessionDep):
    return await session.get(Book, id)


@router.post("/", response_model=BookDetailsRes, status_code=status.HTTP_201_CREATED)
async def create_book(
    req: BookReq,
    session: SessionDep,
    user: Annotated[User, Depends(get_current_user)],
):
    book = Book(**req.model_dump())
    book.creator_user_id = book.modifier_user_id = user.id
    session.add(book)
    await session.commit()
    return book


@router.put("/{id}", response_model=BookDetailsRes)
async def update_book(
    id: int,
    req: BookReq,
    session: SessionDep,
    user: Annotated[User, Depends(get_current_user)],
):
    book = await session.get(Book, id)
    book.patch(**req.model_dump(), modifier_user_id=user.id)
    await session.commit()
    return book


@router.patch("/{id}", response_model=BookDetailsRes)
async def partial_update_book(
    id: int,
    req: BookReqPartial,
    session: SessionDep,
    user: Annotated[User, Depends(get_current_user)],
):
    book = await session.get(Book, id)
    book.patch(**req.model_dump(exclude_unset=True), modifier_user_id=user.id)
    await session.commit()
    return book


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    id: int,
    session: SessionDep,
    user: Annotated[User, Depends(get_current_user)],
):
    contact = await session.get(Book, id)
    await session.delete(contact)
    await session.commit()
