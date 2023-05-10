from sqlalchemy import Column, TEXT, INT, BIGINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Test(Base):
    __tablename__ = "User"
    
    id = Column(BIGINT, nullable=False,autoincrement=True, primary_key=True)
    title = Column(TEXT, nullable=False)
    genres = Column(TEXT, nullable=False)
    vote_average = Column(TEXT, nullable=False)
    vote_count = Column(TEXT, nullable=False)
    popularity = Column(TEXT, nullable=False)
    keywords = Column(TEXT, nullable=False)
    overview = Column(TEXT, nullable=False)
 