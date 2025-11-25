from encodings.base64_codec import base64_encode
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pytest import Session
from db.database import Base, engine, sessionLocal
from sqlalchemy_utils import create_database, database_exists
from schemas.users import User_schema
from db.models import User
import os
import httpx
from passlib.context import CryptContext
import jwt
app= FastAPI()

def getdb():
    db=sessionLocal()
    try:
      yield db
    finally:
      db.close()


if not database_exists(engine.url):
    create_database(engine.url)
Base.metadata.create_all(bind= engine)


pwd_context = CryptContext(schemes=['argon2'], deprecated="auto")

def hashpassword(password:str):
    return pwd_context.hash(password)

def verify_password(inserted_password:str, hashed_password: str):
   return pwd_context.verify(inserted_password, hashed_password)


def verify_token(token:str):
    payload= jwt.decode(token,os.getenv('JWT_TOKEN'), algorithms= os.getenv('ALGORITHM'))
    if payload:
        return payload
    
# token = payload + secret key+ algorithm
#header.payload.signature
def create_token(user:User_schema):
    payload= {"username": user.username    }
    return jwt.encode(payload, os.getenv('JWT_TOKEN'), algorithm= os.getenv('ALGORITHM')) #> generate the header and signature and combine header+payload+signature

def verify_user_token_in_db(decoded_token:str, db):
   user_db= db.query(User).filter(User.username == decoded_token["username"]).first()
   if not user_db:
      raise HTTPException(status_code=400, detail="not found")
   return decoded_token['username']


@app.post('/login')
def login(user: User_schema, db:Session=Depends(getdb)):
     inserted_user= db.query(User).filter(User.username == user.username).first()
     if not inserted_user :
         raise HTTPException(status_code='400', detail="User not exist")
     if not verify_password(user.password, inserted_user.password):
         raise HTTPException(status_code='400', detail="Invalid password")
     token= create_token(user)
     return token

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


@app.post('/register')
def create_user(inserted_user:User_schema, db:Session =Depends(getdb)):
    if db.query(User).filter(User.username == inserted_user.username).first():
               raise HTTPException(status_code=409,detail="User already exist" )
    user_db= User(
       username = inserted_user.username,
       password = hashpassword(inserted_user.password)
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@app.post('/translate')
async def translate_txt(text:str,choice:str, token:str=Depends(oauth2_schema), db:Session= Depends(getdb)):
   print(text)
   print("hello")
   decoded_token= verify_token(token)
   print("uu")
   print(decoded_token)
   verified_token = verify_user_token_in_db(decoded_token, db)
   print(choice, decoded_token)
   
   if verified_token:
     if choice == "FR -> EN":
        API_URL = os.getenv('API_URL_FR_TO_ENG')
     else:
        API_URL = os.getenv('API_URL_EN_TO_FR')

     headers = {
     "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
     }

     def query(payload):
        response = httpx.post(API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 503:
          raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Huggin face model is not available now. try again later" )
        return response.json()

     output = query({
       "inputs": text,
      })
     return output


