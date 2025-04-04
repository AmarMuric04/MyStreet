from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

# Set the MongoDB connection URI.
# For local development, this connects to a MongoDB instance running on localhost at port 27017,
# using a database named "bee_flask_db".
app.config["MONGO_URI"] = (
    "mongodb+srv://muricamar2004:Kolosseum123@nodejs.vbqigm9.mongodb.net/toga_flask?retryWrites=true&w=majority"
)

# Initialize PyMongo with the Flask app.
mongo = PyMongo(app)

# Import routes after creating the app instance to avoid circular imports.
from app import routes
