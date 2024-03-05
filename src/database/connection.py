from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

DATABASE_URI = 'postgresql+psycopg2://postgres:B2dDD3CCcG-2EBbEbcF4cg563553Ed16@monorail.proxy.rlwy.net:38138/railway'

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
