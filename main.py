from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import requests
import os
from dotenv import load_dotenv
from typing import Optional
from openai import OpenAI
import json

from database import get_db, engine
import models
from models import Complaint, ComplaintCreate, ComplaintResponse

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

app = FastAPI(title="Customer Complaints API")

# APILayer configuration
APILAYER_KEY = os.getenv("APILAYER_KEY")
SENTIMENT_API_URL = "https://api.apilayer.com/sentiment/analysis"

# Add OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_sentiment(text: str) -> Optional[str]:
    """Analyze text sentiment using APILayer API"""
    if not APILAYER_KEY:
        return "unknown"
    
    try:
        headers = {
            "apikey": APILAYER_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(
            SENTIMENT_API_URL,
            headers=headers,
            json={"text": text}
        )
        
        if response.status_code == 200:
            result = response.json()
            # Map API response to our sentiment categories
            score = result.get("score", 0)
            if score > 0.3:
                return "positive"
            elif score < -0.3:
                return "negative"
            else:
                return "neutral"
        return "unknown"
    except Exception:
        return "unknown"

def categorize_complaint(text: str) -> str:
    """Categorize complaint using GPT-4"""
    if not OPENAI_API_KEY:
        return "другое"
    
    try:
        prompt = """
        Определи категорию жалобы клиента. Возможные категории:
        - техническая (проблемы с сервисом, технические сбои, проблемы с SMS и т.д.)
        - оплата (проблемы с платежами, счетами, возвратами)
        - другое (все остальные жалобы)
        
        Верни только одно слово - категорию, без кавычек и JSON.
        
        Жалоба клиента: {text}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты - система классификации жалоб клиентов. Отвечай одним словом - категорией."},
                {"role": "user", "content": prompt.format(text=text)}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        # Get the response text directly
        category = response.choices[0].message.content.strip().lower()
        
        # Validate category
        valid_categories = {"техническая", "оплата", "другое"}
        return category if category in valid_categories else "другое"
        
    except Exception as e:
        print(f"Error in categorization: {str(e)}")
        return "другое"

@app.post("/complaints/", response_model=ComplaintResponse)
def create_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    try:
        # Analyze sentiment
        sentiment = analyze_sentiment(complaint.text)
        
        # Create complaint record
        db_complaint = Complaint(
            text=complaint.text,
            sentiment=sentiment,
            category=categorize_complaint(complaint.text)
        )
        
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        
        return ComplaintResponse(
            id=db_complaint.id,
            status=db_complaint.status,
            sentiment=db_complaint.sentiment,
            category=db_complaint.category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint 