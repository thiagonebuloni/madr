from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Message(BaseModel):
    message: str


class ContaSchema(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=40)
    email: str | None = Field(default=None, min_length=3, max_length=40)
    password: str | None = Field(default=None, min_length=3, max_length=40)


class ContaPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class ContaList(BaseModel):
    contas: list[ContaPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class LivroSchema(BaseModel):
    ano: int
    titulo: str
    romancista_id: int


class LivroPublic(LivroSchema):
    id: int
    ano: int
    titulo: str
    romancista_id: int


class LivroList(BaseModel):
    livros: list[LivroPublic]


class FilterPage(BaseModel):
    limit: int = Field(ge=0, default=0)
    offset: int = Field(ge=0, default=10)


class LivroFilter(FilterPage):
    titulo: str | None = Field(default=None, min_length=3, max_length=30)
    ano: int | None = None


class RomancistaSchema(BaseModel):
    nome: str


class RomancistaPublic(BaseModel):
    id: int
    nome: str


class RomancistaList(BaseModel):
    romancistas: list[RomancistaPublic]
