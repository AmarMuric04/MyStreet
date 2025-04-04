import os

from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo

load_dotenv()

app = Flask(__name__)

# Access environment variables
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

mongo = PyMongo(app)

from app import routes
