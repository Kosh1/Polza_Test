from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy.orm import Session
import requests
import os
from dotenv import load_dotenv
from typing import Optional
from openai import OpenAI
import json
import logging  # добавим импорт

from database import get_db, engine
import models
from models import Complaint, ComplaintCreate, ComplaintResponse

# Настроим логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

app = FastAPI(title="Customer Complaints API")

# APILayer configuration
APILAYER_KEY = os.getenv("APILAYER_KEY")
SENTIMENT_API_URL = "https://api.apilayer.com/sentiment/analysis"
SPAM_CHECK_URL = "https://api.apilayer.com/spamchecker"

# Add OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Добавим новые импорты и конфигурацию
IP_API_URL = "http://ip-api.com/json/"

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

def check_spam(text: str) -> bool:
    """Check if text is spam using GPT-4"""
    if not OPENAI_API_KEY:
        return False
    
    try:
        prompt = """
        Проанализируй текст на предмет спама. Учитывай следующие критерии:
        - Наличие рекламных предложений
        - Призывы к немедленным действиям
        - Обещания нереальных выгод
        - Подозрительные ссылки или контакты
        - Массовая рассылка
        
        Ответь только "true" если это спам, или "false" если это не спам.
        
        Текст для анализа: {text}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",  # используем GPT-4
            messages=[
                {"role": "system", "content": "Ты - система определения спама. Отвечай только true или false."},
                {"role": "user", "content": prompt.format(text=text)}
            ],
            temperature=0.3,  # низкая температура для более консистентных ответов
            max_tokens=10  # нам нужно только одно слово
        )
        
        # Получаем ответ и конвертируем его в boolean
        result = response.choices[0].message.content.strip().lower()
        logger.info(f"Spam check response from GPT-4: {result}")
        
        return result == "true"
        
    except Exception as e:
        logger.error(f"Error in spam detection: {str(e)}")
        return False

def get_location_info(ip: str) -> Optional[str]:
    """Get location info from IP"""
    try:
        response = requests.get(f"{IP_API_URL}{ip}")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return f"{data.get('city', '')}, {data.get('country', '')}"
        return None
    except Exception as e:
        print(f"Error in IP geolocation: {str(e)}")
        return None

@app.post("/complaints/", response_model=ComplaintResponse)
def create_complaint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db),
    client_ip: str = Header(None, alias="X-Forwarded-For")
):
    try:
        # Get the first IP if multiple are provided
        ip_address = client_ip.split(',')[0].strip() if client_ip else None
        
        # Analyze sentiment
        sentiment = analyze_sentiment(complaint.text)
        
        # Check for spam
        is_spam = check_spam(complaint.text)
        
        # Get location from IP
        location = get_location_info(ip_address) if ip_address else None
        
        # Create complaint record
        db_complaint = Complaint(
            text=complaint.text,
            sentiment=sentiment,
            category=categorize_complaint(complaint.text),
            is_spam=is_spam,
            ip_address=ip_address,
            location=location
        )
        
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        
        return ComplaintResponse(
            id=db_complaint.id,
            status=db_complaint.status,
            sentiment=db_complaint.sentiment,
            category=db_complaint.category,
            is_spam=db_complaint.is_spam,
            location=db_complaint.location
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint 