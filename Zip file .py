from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Enable CORS for frontend access
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite setup
engine = create_engine("sqlite:///predictions.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Database model
class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    prediction = Column(Integer)
    probability = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Request model
class PredictRequest(BaseModel):
    SMA_5: float
    SMA_10: float
    RSI_14: float
    MACD: float
    Volatility: float
    Price_Range: float
    Gap: float
    Volume_Change: float
    user_email: str

# Dummy prediction logic
@app.post("/predict")
async def predict(data: PredictRequest):
    prediction = 1 if data.SMA_5 > data.SMA_10 else 0
    probability = 0.78 if prediction == 1 else 0.22

    db = SessionLocal()
    db.add(Prediction(user_email=data.user_email, prediction=prediction, probability=probability))
    db.commit()
    db.close()

    return {"prediction": prediction, "probability": probability}

# Fetch user prediction history
@app.get("/history")
async def get_history(user_email: str = Query(...)):
    db = SessionLocal()
    results = db.query(Prediction).filter(Prediction.user_email == user_email).order_by(Prediction.timestamp.desc()).all()
    db.close()
    return [
        {
            "prediction": r.prediction,
            "probability": r.probability,
            "timestamp": r.timestamp
        }
        for r in results
    ]
