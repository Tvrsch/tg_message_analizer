from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, String, Integer, TIMESTAMP, text, JSON

Base = declarative_base()
metadata = Base.metadata


class TgUser(Base):
    __tablename__ = "tg_user"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False)
    tg_username = Column(String)
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class WordsStat(Base):
    __tablename__ = "words_stat"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("tg_user.id"))
    chat_id = Column(Integer)
    words_number = Column(Integer)
    sentence = Column(String)
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
