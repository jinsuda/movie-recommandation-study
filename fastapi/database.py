from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

DB_URL = 'mysql+pymysql://root:root@localhost:3306/tmdb'
                          #유저  pw                  db이름
                          
class engineconn:
    
    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle = 500)
        
    def sessionmaker(self):
        Session_ = sessionmaker(bind=self.engine)
        session = Session_()
        return session
    
    def connection(self):
        conn = self.engine.connect()
        return conn