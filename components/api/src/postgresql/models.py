from postgresql.database import Base
from sqlalchemy import Column, Integer, String


class Law(Base):
    __tablename__ = "law"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    url = Column(String)


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String)


class SelectieLijsten(Base):
    __tablename__ = "selectielijsten"

    id = Column(Integer, primary_key=True, autoincrement=True)
    selectielijsten = Column(String)
    functie = Column(String)
    categorie = Column(String)
    onderwerp = Column(String)
    omschrijving = Column(String)
    waardering = Column(String)
    voorbeeldstukken = Column(String)
