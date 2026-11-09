"""Pydantic request/response schemas."""

from pydantic import BaseModel, Field

from .. import config


class EmailInput(BaseModel):
    email_content: str = Field(..., min_length=1, max_length=config.MAX_EMAIL_LENGTH)


class BusinessInfo(BaseModel):
    name: str = ""
    title: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    website: str = ""
    other_info: str = ""
