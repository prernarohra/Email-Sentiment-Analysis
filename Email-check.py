from typing import List
from fastapi import FastAPI, HTTPException, Depends
import os
import logging
from service import Emails 
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import EmailOut

Base.metadata.create_all(bind=engine)

app = FastAPI()

email_service = Emails()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/analyze-emails")
def watch_emails(db: Session = Depends(get_db)):
    try:
        user = os.getenv("user")
        password = os.getenv("password")
        mail = email_service.connect_to_gmail_imap(user, password)

        emails = email_service.get_last_10_emails(mail)
        email_service.analyze_sentiment(emails, db, "email")

        return {"status": "success", "message": "Email sentiment analysis completed successfully."}
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during email analysis.")
    
@app.get("/emails", response_model=List[EmailOut])
def get_emails(db: Session = Depends(get_db)):
    data = email_service.get_emails_data(db)
    return data

@app.get("/emails/{email_id}")
def get_emails_by_id(email_id: int, db: Session = Depends(get_db)):
    data = email_service.get_emails_data_first(db,email_id)
    return data

@app.get("/search-emails/")
def create_event_by_emails(db: Session = Depends(get_db)):
    keywords = ["appointment", "meeting", "schedule", "call"]

    user = os.getenv("user")
    password = os.getenv("password")
    mail = email_service.connect_to_gmail_imap(user, password)
    email_service.get_last_10_emails_with_keywords(mail, keywords, db)

    return f"Status: Event added successfully "


@app.get("/get_event_type/")
def eventtype():
    types = email_service.get_eventtype()
    return types
    


