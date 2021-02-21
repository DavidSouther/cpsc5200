from argparse import ArgumentParser
from datetime import datetime
import logging
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

parser = ArgumentParser()
parser.add_argument('--database', type=str, default='sqlite:////var/db/test.db')
(args, _) = parser.parse_known_args()


Base = declarative_base()
_engine = None
_session = None
def engine():
    global _engine
    if _engine is None:
        logging.info('Loading database at %s', args.database)
        _engine = create_engine(args.database, echo=True)
    return _engine

def session():
    global _session
    if _session is None:
        _session = sessionmaker(bind=engine())()
    return _session

def migrate():
    global Base
    Base.metadata.create_all(engine())

class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    device = Column(String) # Arbitrary string
    latest_operation = Column(Integer) # Incrementing integer, foreign key to Operations

    def __repr__(self):
        return f"<Photo(id={self.id}, " \
                       "device='{self.device}', " \
                       "created='{self.created}', " \
                       "latest_operation={self.latest_operation})>"

class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer, ForeignKey('photos.id'))
    previous_id = Column(Integer, ForeignKey('operations.id'))
    completed = Column(String)
    description = Column(String) # JSON of original command

    photo = relationship("Photo")
    previous = relationship("Operation")

    def __repr__(self):
        return f"<Operation photo='{self.photo_id}' description='{self.description}'>"
