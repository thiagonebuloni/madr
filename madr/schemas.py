from pydantic import BaseModel, Field


class ContaSchema(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=40)
    email: str | None = Field(default=None, min_length=3, max_length=40)
    password: str | None = Field(default=None, min_length=3, max_length=40)


class ContaPublic(BaseModel):
    id: int
    username: str
    email: str
