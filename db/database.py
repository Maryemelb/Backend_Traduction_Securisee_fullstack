from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_NAME= os.getenv('DATABASE_NAME')
DATABASE_PASSWORD= os.getenv('DATABASE_PASSWORD')
DATABASE_USER=os.getenv('DATABASE_USER')
DATABASE_HOST=os.getenv('DATABASE_HOST')
DATABASE_PORT=os.getenv('DATABASE_PORT')
DATABASE_URL=f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine= create_engine(DATABASE_URL)
sessionLocal= sessionmaker(autoflush=False, autocommit= False, bind=engine)
Base = declarative_base()