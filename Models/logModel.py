from Databases.logBase import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "Logins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)