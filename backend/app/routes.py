from app import app, mongo
from flask import jsonify, request


@app.route("/")
def home():
    return "Hello from Flask and MongoDB!"


@app.route("/add", methods=["POST"])
def add_message():
    # Get JSON data from the request body
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    # Insert the document into the "messages" collection in MongoDB
    result = mongo.db.messages.insert_one({"message": data["message"]})

    # Return the inserted document's id as a response
    return jsonify({"inserted_id": str(result.inserted_id)}), 201


@app.route("/messages", methods=["GET"])
def get_messages():
    # Retrieve all documents from the "messages" collection
    messages = mongo.db.messages.find()
    output = []
    for msg in messages:
        output.append({"id": str(msg["_id"]), "message": msg["message"]})
    return jsonify({"messages": output}), 200
