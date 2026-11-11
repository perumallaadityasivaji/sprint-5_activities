# from sqlalchemy import Integer,String, Column ,Create_engine,DateTime
# from sqlalchemy.orm import declarative_base,Session
# from datetime import datetime


# DB_PATH = "warehouse.db"
# engine=Create_engine(f"sqlite:///{DB_PATH}")
# Base = declarative_base()

# class Packages(Base):
#     __tablename__ = "Packages"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     description = Column(String)
#     created_at = Column(DateTime, default=datetime.now)
    
# class Dispatches(Base):
#     __tablename__ = "Dispatches"
#     id = Column(Integer, primary_key=True)
#     package_id = Column(Integer)
#     dispatched_at = Column(DateTime, default=datetime.now)
    
# class 


