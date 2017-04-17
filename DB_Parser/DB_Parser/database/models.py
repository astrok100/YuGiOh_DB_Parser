from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship

from DB_Parser import settings


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


def create_deals_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class Card(DeclarativeBase):
    __tablename__ = "card"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    image = Column(String(50), nullable=False)
    card_desc = Column(String(500), nullable=False)
    yugioh_cid = Column(Integer, nullable=False, unique=True)
    card_type_id = Column(Integer, ForeignKey('card_type.id'))
    attribute_id = Column(Integer, ForeignKey('card_attribute.id'))

    card_type = relationship("CardType", back_populates="card")
    card_attribute = relationship("CardAtrribute", back_populates="card")
    card_meta_data = relationship("CardMetaData", back_populates="card")
    monster = relationship("Monster", back_populates="card")


class CardAtrribute(DeclarativeBase):
    __tablename__ = "card_attribute"

    id = Column(Integer, primary_key=True)
    attribute = Column(String(50), nullable=False, unique=True)
    card = relationship("Card", back_populates="card_attribute")


class CardType(DeclarativeBase):
    __tablename__ = "card_type"

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False, unique=True)
    card = relationship("Card", back_populates="card_type")

    def __init__(self, type):
        self.type = type


class CardMetaData(DeclarativeBase):
    __tablename__ = "meta_data"

    print_id = Column(String(10), primary_key=True)
    print_date = Column(DateTime, primary_key=True)
    pack = Column(String(50), nullable=False)

    card_id = Column(Integer, ForeignKey('card.id'))
    rarity_id = Column(Integer, ForeignKey('rarity.id'), primary_key=True)

    card = relationship("Card", back_populates="card_meta_data")
    rarity = relationship("Rarity", back_populates="meta_data")


class Rarity(DeclarativeBase):
    __tablename__ = "rarity"

    id = Column(Integer, primary_key=True)
    rarity = Column(String(50), nullable=False, unique=True)
    meta_data = relationship("CardMetaData", back_populates="rarity")

    def __init__(self, rarity):
        self.rarity = rarity


class Monster(DeclarativeBase):
    __tablename__ = "monster"

    id = Column(Integer, primary_key=True)
    level_rank = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defence = Column(Integer, nullable=False)
    pendulum_scale = Column(Integer, nullable=True)
    pendulum_effect = Column(String(300), nullable=True)

    card_id = Column(Integer, ForeignKey('card.id'))
    monster_type_id = Column(
        Integer, ForeignKey('monster_type.id'))

    card = relationship("Card", back_populates="monster")
    monster_type = relationship(
        "MonsterType", back_populates="monster")
    monster_card_type_group = relationship(
        "MonsterCardTypeGroup", back_populates="monster")


class MonsterCardTypeGroup(DeclarativeBase):
    __tablename__ = "monster_card_type_group"

    monster_id = Column(
        Integer, ForeignKey('monster.id'), primary_key=True)
    monster_card_type_id = Column(
        Integer, ForeignKey('monster_card_type.id'), primary_key=True)

    monster = relationship(
        "Monster", back_populates="monster_card_type_group")
    monster_card_type = relationship(
        "MonsterCardType", back_populates="monster_card_type_group")


# xyz synchro fusion etc
class MonsterCardType(DeclarativeBase):
    __tablename__ = "monster_card_type"

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    monster_card_type_group = relationship(
        "MonsterCardTypeGroup", back_populates="monster_card_type")

    def __init__(self, type):
        self.type = type


# dragon, warrior, etc
class MonsterType(DeclarativeBase):
    __tablename__ = "monster_type"

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    monster = relationship("Monster", back_populates="monster_type")

    def __init__(self, type):
        self.type = type
