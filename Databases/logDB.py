from Databases.logBase import Base, engine
from Models.logModel import User

def create_table():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_table()