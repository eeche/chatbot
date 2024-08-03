from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from sqlalchemy.orm import Session
from database import db
from schema import UserSchema, AccessResponse, IoCSchema
import crud

app = FastAPI()
app.mount("/static", StaticFiles(directory="/app/src/chatbot/static"), name="static")

@app.get("/")
async def root():
    logging.info("Hello World")
    return {"message": "Hello World"}

@app.get("/hi")
async def hi():
    logging.info("hi")
    # index_file = Path("index.html")
    index_file = Path("/app/src/chatbot/index.html")
    with index_file.open() as file:
        content = file.read()
    return HTMLResponse(content=content)

@app.post("/access", response_model=AccessResponse)
async def access(user_input: UserSchema, db: Session = Depends(db.get_session)):

    user = crud.get_user(db, user_input)
    if not user:
        raise HTTPException(status_code=404, detail="Sorry, user not found")
    
    if user.email != user_input.email:
        crud.create_ioc(db, user, user_input, crud.IoCType.EMAIL_MISMATCH)
        raise HTTPException(status_code=401, detail="Email does not match")
    
    return AccessResponse(
        message=f"Welcome!! {user.username}",
        user_id=user.id
    )

@app.get("/ioc/{user_id}", response_model=List[IoCSchema])
async def get_ioc(user_id: int, db: Session = Depends(db.get_session)):
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Sorry, user not found")
    
    iocs = crud.get_iocs(db, user)
    return [IoCSchema.model_validate(ioc) for ioc in iocs]