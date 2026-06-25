from datetime import datetime, timedelta, timezone
import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from Databases.logBase import get_db, Base, engine
from Models.logModel import User
from Schemas.login import LoginBody
from Schemas.signup import SignupBody

load_dotenv()
app = FastAPI()
Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGO = os.getenv("ALGORITHM")

@app.post("/signup")
def signup(body: SignupBody, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username = body.username,
        password_hash = pwd_context.hash(body.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return JSONResponse(status_code=200, content={"id": user.id, "username": user.username})

@app.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode(
        {
            "sub": user.username,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=1)
        },
        SECRET_KEY,
        algorithm=ALGO
    )
    return JSONResponse(status_code=200, content={"access_token": token, "token_type": "bearer"})

@app.post("/logout")
def logout(auth: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if auth:
        try:
            jwt.decode(auth.credentials, SECRET_KEY, algorithms=[ALGO])
        except JWTError:
            raise HTTPException(status_code=401, detail="Timeout")
    return JSONResponse(status_code=200, content={"message": "Logged out"})
    

