from pydantic import BaseModel


class LawInfo(BaseModel):
    id: int
    title: str
    description: str
    url: str


class LawArticle(BaseModel):
    id: int
    law_name: str
    article_id: str
    article_number: str
    title: str
    body: str
    url: str
    date: str


class LawChapter(BaseModel):
    id: int
    law_name: str
    chapter_id: str
    title: str
    body: str
    url: str
    date: str
