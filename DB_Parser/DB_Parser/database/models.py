from sqlalchemy import create_engine, Column, Integer, String(50), DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import DB_Parser.settings


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
    title = Column(String(50))
    name = Column(String(50))
    image = Column(String(50))
    card_desc = Column(String(300))
    yugioh_cid = Column(Integer)
    card_type_id = Column(Integer, ForeignKey('card_type.id'))
    attribute_id = Column(Integer, ForeignKey('card_attribute.id'))

    card_type = relationship("card_type", back_populates="card")
    card_attribute = relationship("card_attribute", back_populates="card")
    card_meta_data = relationship("meta_data", back_populates="card")
	monster = relationship("monster", back_populates="card")


class CardAtrribute(DeclarativeBase):
	__tablename__ = "card_attribute"

	id = Column(Integer, primary_key=True)
    attribute = Column(String(50))
	card = relationship("card", back_populates="card_attribute")

class CardType(DeclarativeBase):
    __tablename__ = "card_type"

    id = Column(Integer, primary_key=True)
    type = Column(String(50))
	card = relationship("card", back_populates="card_type")


class CardMetaData(DeclarativeBase):
	__tablename__ = "meta_data"

	id = Column(Integer, primary_key=True)
	print_date = Column(DateTime, primary_key=True)
	card_id = Column(Integer, ForeignKey('card.id'))
	rarity_id = Column(Integer, ForeignKey('rarity.id'))
	card = relationship("card", back_populates="card_meta_data")
	rarity = relationship("rarity", back_populates="meta_data")

class Rarity(DeclarativeBase):
	__tablename__ = "card_attribute"
	
	id = Column(Integer, primary_key=True)
    rarity = Column(String(50))
	meta_data = relationship("meta_data", back_populates="rarity")


class Monster(DeclarativeBase):
    __tablename__ = "monster"

    id = Column(Integer, primary_key=True)
    level_rank = Column(Integer)
    attack = Column(Integer)
    defence = Column(Integer)
    pendulum_scale = Column(Integer)
    pendulum_effect = Column(String(300))

    card_id = Column(Integer, ForeignKey('card.id'))
    attribute_id = Column(Integer, ForeignKey('monster_attribute.id'))
    monster_card_type_id = Column(Integer, ForeignKey('monster_card_type.id'))
	card = relationship("card", back_populates="monster")
	attribute = relationship("monster_attribute", back_populates="monster")
	monster_card_type = relationship("monster_card_type", back_populates="monster")



class MonsterTypeGroup(DeclarativeBase):
	__tablename__ = "monster_type_group"
	
    monster_id = Column(Integer, ForeignKey('monster.id'), primary_key=True)
    monster_type_id = Column(Integer, ForeignKey('monster_type.id'), primary_key=True)

class MonsterType(DeclarativeBase):
	__tablename__ = "monster_type"
	
	id = Column(Integer, primary_key=True)
	type = Column(String(50))


class MonsterAttribute(DeclarativeBase):
    __tablename__ = "monster_attribute"

    id = Column(Integer, primary_key=True)
    attribute = Column(String(50))
	monster = relationship("monster", back_populates="attribute")


class MonsterCardType(DeclarativeBase):
	__tablename__ = "monster_card_type"

	id = Column(Integer, primary_key=True)
	type = Column(String(50))
	monster = relationship("monster", back_populates="attribute")
