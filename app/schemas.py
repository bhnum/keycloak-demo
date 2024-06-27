from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic_partial import create_partial_model


class BookRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    author: str
    creator_user_id: str
    modifier_user_id: str
    created: datetime
    modified: datetime


class BookSummaryRes(BookRes):
    pass


class BookDetailsRes(BookRes):
    content: str


class BookReq(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    author: str
    content: str


BookReqPartial = create_partial_model(BookReq)
