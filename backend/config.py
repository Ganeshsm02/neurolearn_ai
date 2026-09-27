import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "neurolearn_ai"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

SUBJECTS = [
    "Deep Learning",
    "Machine Learning",
    "MLOps",
    "Cloud Computing & Application Development (CCAD)",
    "Natural Language Processing (NLP)",
    "Generative AI",
    "Reinforcement Learning"
]
