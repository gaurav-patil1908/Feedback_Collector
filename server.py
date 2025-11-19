from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import os

app = FastAPI(title="Feedback Collector API")

DATA_FILE = "category_feedback.csv"
COLUMNS = [
    "Timestamp", "Name", "Email", "Category",
    "Q1", "Q2", "Q3", "Q4", "Q5", "Suggestions"
]

# Create CSV if not exists
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)

security = HTTPBasic()
ADMIN_PASSWORD = "Gaurav"

# Category questions (same as your Streamlit version)
CATEGORY_QUESTIONS = {
    "🏦 Banking Service": [
        "Which type of banking do you use most?",
        "Have you faced any transaction failures recently?",
        "How secure do you feel about online banking?",
        "How satisfied are you with customer support?",
        "How easy is your bank's app or website to use?",
    ],
    "📱 Mobile Service": [
        "Which mobile operator do you use?",
        "Do you face frequent call drops?",
        "How is your internet speed?",
        "How satisfied are you with customer support?",
        "Are recharge plans affordable?",
    ],
    "🌐 Internet / Wi-Fi": [
        "Which internet provider do you use?",
        "Do you face frequent disconnections?",
        "Is your speed consistent?",
        "Are you satisfied with technical support?",
        "Is your internet plan value for money?",
    ],
    "🛍️ E-Commerce": [
        "Which shopping platform do you use most?",
        "Are you happy with delivery timings?",
        "How satisfied are you with product quality?",
        "How easy is the refund/return process?",
        "Are prices reasonable compared to stores?",
    ],
    "🏥 Healthcare Service": [
        "How easy is it to get appointments?",
        "Are doctors polite and helpful?",
        "Is the waiting time reasonable?",
        "How satisfied are you with medical facilities?",
        "Do you find the cost of treatment fair?",
    ],
    "🏫 Education / College Service": [
        "Are teachers supportive and friendly?",
        "Is study material easy to understand?",
        "How useful are online lectures or portals?",
        "Are you satisfied with campus facilities?",
        "Would you recommend this institute to others?",
    ]
}

# -------------------------
# Pydantic Model
# -------------------------

class Feedback(BaseModel):
    name: str
    email: str
    category: str
    q1: str
    q2: str
    q3: int
    q4: int
    q5: int
    suggestions: str = ""

# -------------------------
# Helper Function
# -------------------------

def save_feedback(data: dict):
    df = pd.DataFrame([data])
    df.to_csv(DATA_FILE, mode="a", header=False, index=False)

def admin_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# -------------------------
# API ROUTES
# -------------------------

@app.get("/")
def home():
    return {"message": "Feedback Collector API Running 🚀"}

@app.get("/categories")
def get_categories():
    return list(CATEGORY_QUESTIONS.keys())

@app.get("/questions/{category}")
def get_questions(category: str):
    if category not in CATEGORY_QUESTIONS:
        raise HTTPException(404, "Category not found")
    return CATEGORY_QUESTIONS[category]

@app.post("/submit")
def submit_feedback(feedback: Feedback):
    if feedback.category not in CATEGORY_QUESTIONS:
        raise HTTPException(400, "Invalid category")

    data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": feedback.name,
        "Email": feedback.email,
        "Category": feedback.category,
        "Q1": feedback.q1,
        "Q2": feedback.q2,
        "Q3": feedback.q3,
        "Q4": feedback.q4,
        "Q5": feedback.q5,
        "Suggestions": feedback.suggestions
    }

    save_feedback(data)
    return {"message": "Feedback submitted successfully 🎉"}

@app.get("/admin/all")
def get_all_feedback(auth: bool = Depends(admin_auth)):
    df = pd.read_csv(DATA_FILE)
    return df.to_dict(orient="records")

@app.get("/admin/by-category/{category}")
def get_feedback_by_category(category: str, auth: bool = Depends(admin_auth)):
    df = pd.read_csv(DATA_FILE)
    if category not in CATEGORY_QUESTIONS:
        raise HTTPException(404, "Category not found")

    df = df[df["Category"] == category]
    return df.to_dict(orient="records")
