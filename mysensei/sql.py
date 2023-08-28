from sqlalchemy import SmallInteger, Integer, String, Column, Table
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from mysensei.io import get_conf_toml

Base = declarative_base()

secrets : dict = get_conf_toml('secrets.toml')
# TODO : create connector following https://chat.openai.com/c/92c6accb-2b95-4032-93c3-69d7da2b38e3

class ReadingAssiociations(Base):
    __tablename__ = "reading_associations_jp"
    user_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    sound = Column(String)
    concept = Column(String)
    descriptor = Column(String)


## Vocab jp notes
#user_vocabnotesjp_corr = Table(
#    name="user_vocabnotesjp",
#    metadata=Base.metadata,
#    # TODO: columns
#)
#
#class VocabNotesJp(Base):
#    __tablename__ = "vocab_notes_jp"
#    vocabnotesjp_id = Column(
#        Integer, 
#        primary_key=True, 
#        autoincrement=True,
#    )
#    lemma = Column(String)
#    count = Column(SmallInteger)
#    # TODO: add cols
#    meanings = Column(ARRAY(String))
#    # TODO: add cols
