from argparse import ArgumentParser
import logging
from flask import g
from sqlalchemy import create_engine, Column, ForeignKey, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

parser = ArgumentParser()
#parser.add_argument('--database', type=str, default='sqlite:////var/db/test.db')
parser.add_argument('--database', type=str, default='postgresql://postgres:example@db:5432/postgres')
(args, _) = parser.parse_known_args()


Base = declarative_base()
_engine = None
def engine():
    global _engine
    if _engine is None:
        logging.info('Loading database at %s', args.database)
        _engine = create_engine(args.database)
    return _engine

def session():
    if not 'session' in g:
        g.session = scoped_session(sessionmaker(bind=engine()))()
    return g.session

def migrate():
    global Base
    Base.metadata.create_all(engine())

class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, Sequence('photo_id_seq'), primary_key=True)
    device = Column(String) # Arbitrary string
    latest_operation = Column(Integer) # Incrementing integer, foreign key to Operations

    def __repr__(self):
        return f"<Photo(id={self.id}, " \
                       "device='{self.device}', " \
                       "created='{self.created}', " \
                       "latest_operation={self.latest_operation})>"

class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, Sequence('operation_id_seq'), primary_key=True)
    photo_id = Column(Integer, ForeignKey('photos.id'))
    previous_id = Column(Integer, ForeignKey('operations.id'))
    completed = Column(String)
    description = Column(String) # JSON of original command

    photo = relationship("Photo")
    previous = relationship("Operation")

    def __repr__(self):
        return f"<Operation photo='{self.photo_id}' description='{self.description}'>"
