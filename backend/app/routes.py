import datetime

import bcrypt
import jwt
from app import app, mongo
from bson import ObjectId
from flask import jsonify, request
from pymongo import DESCENDING

from .session import save_token

# ------------------ AUTH ROUTES ------------------


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Retrieve the user from MongoDB
    user = mongo.db.users.find_one({"email": email})

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        token = jwt.encode(
            {
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        print(f"Created a token: {token}")
        # For PyJWT v2.x token is returned as a string, if not decode it.
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        save_token(token)

        return jsonify(), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Check if the user already exists
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    # Hash the password before saving it
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user_id = mongo.db.users.insert_one(
        {"email": email, "password": hashed_password, "username": username}
    ).inserted_id

    return jsonify({"user_id": str(user_id)}), 201


def get_current_user():
    token = request.headers.get("Authorization").split()[1]
    print(token)
    if not token:
        return None, jsonify({"error": "Token is missing"}), 401
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        user = mongo.db.users.find_one({"email": payload.get("email")})
        if not user:
            return None, jsonify({"error": "User not found"}), 404
        return user, None, None
    except Exception as e:
        return None, jsonify({"error": "Invalid token", "message": str(e)}), 401


# ------------------ POST ROUTES ------------------


@app.route("/posts", methods=["POST"])
def add_post():
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    data = request.get_json()
    title = data.get("title")
    text = data.get("text")
    image = data.get("image")  # optional Cloudinary image URL
    tags = data.get("tags")

    if not title or not text:
        return jsonify({"error": "Title and text are required"}), 400

    post = {
        "user_id": user["_id"],
        "title": title,
        "text": text,
        "image": image,
        "tags": tags if tags else [],
        "likes": [],  # will store user ObjectIds who liked the post
        "comments": [],  # list of comment subdocuments
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    result = mongo.db.posts.insert_one(post)
    return jsonify({"message": "Post created", "post_id": str(result.inserted_id)}), 201


@app.route("/posts/<post_id>", methods=["PUT"])
def edit_post(post_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    data = request.get_json()
    # Allow updating title, text, image, and tags
    update_fields = {}
    for field in ["title", "text", "image", "tags"]:
        if field in data:
            update_fields[field] = data[field]
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    update_fields["updated_at"] = datetime.datetime.utcnow()

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if post["user_id"] != user["_id"]:
        return jsonify({"error": "Not authorized to update this post"}), 403

    mongo.db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": update_fields})
    return jsonify({"message": "Post updated"}), 200


@app.route("/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if post["user_id"] != user["_id"]:
        return jsonify({"error": "Not authorized to delete this post"}), 403

    mongo.db.posts.delete_one({"_id": ObjectId(post_id)})
    return jsonify({"message": "Post deleted"}), 200


@app.route("/posts", methods=["GET"])
def get_posts():
    current_user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    current_user_email = current_user.get("email")
    posts_cursor = mongo.db.posts.find().sort("created_at", DESCENDING)
    posts = []
    for post in posts_cursor:
        user_id = post.get("user_id")
        user_email = None

        if user_id:
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            username = user.get("username") if user else None
            user_email = user.get("email") if user else None

        likes = post.get("likes", [])
        liked_users = list(mongo.db.users.find({"_id": {"$in": likes}}, {"email": 1}))
        liked_user_emails = [user["email"] for user in liked_users if "email" in user]

        liked_by_user = current_user_email in liked_user_emails

        posts.append(
            {
                "post_id": str(post.get("_id")),
                "user_id": str(user_id),
                "user_email": user_email,
                "username": username,
                "title": post.get("title"),
                "text": post.get("text"),
                "image": post.get("image"),
                "tags": post.get("tags"),
                "likes": likes,
                "liked_by_user": liked_by_user,
                "comments": post.get("comments"),
                "created_at": (
                    post.get("created_at").isoformat()
                    if post.get("created_at")
                    else None
                ),
                "updated_at": (
                    post.get("updated_at").isoformat()
                    if post.get("updated_at")
                    else None
                ),
            }
        )
    return jsonify(posts), 200


# ------------------ LIKE ROUTE ------------------


@app.route("/posts/<post_id>/like", methods=["POST"])
def toggle_like(post_id):
    print(post_id)
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"error": "Post not found"}), 404

    user_id_str = str(user["_id"])
    likes = post.get("likes", [])
    # Convert likes to string list for easy comparison
    likes_str = [str(like) for like in likes]

    if user_id_str in likes_str:
        # Remove the like
        mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)}, {"$pull": {"likes": user["_id"]}}
        )
        message = "Like removed"
    else:
        # Add the like
        mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)}, {"$push": {"likes": user["_id"]}}
        )
        message = "Post liked"
    return jsonify({"message": message}), 200


# ------------------ COMMENT ROUTES ------------------


@app.route("/posts/<post_id>/comment", methods=["POST"])
def add_comment(post_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    data = request.get_json()
    comment_text = data.get("comment")
    if not comment_text:
        return jsonify({"error": "Comment text is required"}), 400

    comment = {
        "_id": ObjectId(),  # generate a unique ObjectId for the comment
        "user_id": user["_id"],
        "comment": comment_text,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    result = mongo.db.posts.update_one(
        {"_id": ObjectId(post_id)}, {"$push": {"comments": comment}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Post not found"}), 404
    return jsonify({"message": "Comment added", "comment_id": str(comment["_id"])}), 201


@app.route("/posts/<post_id>/comment/<comment_id>", methods=["PUT"])
def edit_comment(post_id, comment_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    data = request.get_json()
    new_text = data.get("comment")
    if not new_text:
        return jsonify({"error": "New comment text is required"}), 400

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Check if the comment exists and belongs to the user.
    comments = post.get("comments", [])
    comment_found = None
    for c in comments:
        if str(c["_id"]) == comment_id:
            comment_found = c
            break

    if not comment_found:
        return jsonify({"error": "Comment not found"}), 404
    if comment_found["user_id"] != user["_id"]:
        return jsonify({"error": "Not authorized to edit this comment"}), 403

    # Update the specific comment using the positional operator
    mongo.db.posts.update_one(
        {"_id": ObjectId(post_id), "comments._id": ObjectId(comment_id)},
        {
            "$set": {
                "comments.$.comment": new_text,
                "comments.$.updated_at": datetime.datetime.utcnow(),
            }
        },
    )
    return jsonify({"message": "Comment updated"}), 200


@app.route("/posts/<post_id>/comment/<comment_id>", methods=["DELETE"])
def delete_comment(post_id, comment_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Find the comment and verify ownership.
    comments = post.get("comments", [])
    comment_found = None
    for c in comments:
        if str(c["_id"]) == comment_id:
            comment_found = c
            break

    if not comment_found:
        return jsonify({"error": "Comment not found"}), 404
    if comment_found["user_id"] != user["_id"]:
        return jsonify({"error": "Not authorized to delete this comment"}), 403

    mongo.db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"comments": {"_id": ObjectId(comment_id)}}},
    )
    return jsonify({"message": "Comment deleted"}), 200
