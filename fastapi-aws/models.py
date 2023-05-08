from sqlalchemy import Column, TEXT, INT, BIGINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Test(Base):
    __tablename__ = "User"
    
    id = Column(BIGINT, nullable=False,autoincrement=True, primary_key=True)
    lastname = Column(TEXT, nullable=False)
    firstname = Column(TEXT, nullable=False)
    phoneNumber = Column(INT, nullable=False)
    email = Column(TEXT, nullable=False)
    Korean = Column(INT, nullable=False)
    Math = Column(INT, nullable=False)
    English = Column(INT, nullable=False)