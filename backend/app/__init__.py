from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = (
    "mongodb+srv://muricamar2004:Kolosseum123@nodejs.vbqigm9.mongodb.net/toga_flask?retryWrites=true&w=majority"
)
app.config["SECRET_KEY"] = "your_super_secret_key"

# Initialize PyMongo with the Flask app.
mongo = PyMongo(app)

# Import routes after creating the app instance to avoid circular imports.
from app import routes
