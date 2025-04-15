import datetime
import random
import smtplib

import bcrypt
import jwt
from app import app, mongo
from bson import ObjectId
from flask import jsonify, request
from pymongo import DESCENDING

from .session import save_token

"""
    TL;DR
    AUTH - LOGIN, SIGNUP, CODE SEND, CODE VERIFY
    GROUPS - POST, GET, PUT, DELETE
    GROUPS/POSTS - POST, GET, PUT, DELETE
    POSTS COMMENT - POST, PUT, DELETE
    POSTS - LIKE, COMMENT
"""

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


@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    recipient_email = data.get("email")

    if not recipient_email:
        return {"status": "error", "message": "Email address not provided"}, 400

    # Check if the user already exists
    existing_user = mongo.db.users.find_one({"email": recipient_email})
    if existing_user:
        return {"status": "error", "message": "Email already registered"}, 400

    # Generate a 6-digit code
    code = f"{random.randint(0, 999999):06}"
    subject = "Signup Code from MyStreet"
    message_body = f"Your signup code is: {code}"
    message = f"Subject:{subject}\n\n{message_body}"

    try:
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(
                user="muricamar2005@gmail.com", password="jpdvuuwfipwgninx"
            )
            connection.sendmail(
                from_addr="muricamar2005@gmail.com",
                to_addrs=recipient_email,
                msg=message,
            )

        # Remove any existing code for the email
        mongo.db.codes.delete_many({"email": recipient_email})
        # Insert the new code
        mongo.db.codes.insert_one({"email": recipient_email, "code": code})

        return {
            "status": "success",
            "message": "Email sent successfully",
            "code": code,
        }, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    input_code = data.get("code")

    record = mongo.db.codes.find_one({"email": email})

    if not record:
        return {"status": "error", "message": "Code not found or expired"}, 400

    if record["code"] != input_code:
        return {"status": "error", "message": "Invalid code"}, 400

    # Delete the code after successful verification for cleanup.
    mongo.db.codes.delete_one({"email": email})
    return {"status": "success", "message": "Code verified successfully"}, 200


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


# ------------------ POSTS ROUTES -----------------


@app.route("/groups/<group_id>/posts", methods=["POST"])
def create_post_in_group(group_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    try:
        group_obj_id = ObjectId(group_id)
    except Exception:
        return jsonify({"error": "Invalid group_id format"}), 400

    group = mongo.db.groups.find_one({"_id": group_obj_id})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    data = request.get_json()
    title = data.get("title")
    text = data.get("text")
    image = data.get("image")
    tags = data.get("tags", [])
    anonymous = data.get("anonymous", False)

    if not title or not text:
        return jsonify({"error": "Title and text are required"}), 400

    post = {
        "user_id": user["_id"],
        "username": user["username"],
        "group_id": group_obj_id,
        "title": title,
        "text": text,
        "image": image,
        "tags": tags,
        "anonymous": anonymous,
        "likes": [],
        "comments": [],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }

    result = mongo.db.posts.insert_one(post)
    return (
        jsonify(
            {"message": "Post created in group", "post_id": str(result.inserted_id)}
        ),
        201,
    )


@app.route("/groups/<group_id>/posts", methods=["GET"])
def get_posts_in_group(group_id):
    try:
        group_obj_id = ObjectId(group_id)
    except Exception:
        return jsonify({"error": "Invalid group_id format"}), 400

    group = mongo.db.groups.find_one({"_id": group_obj_id})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    user, error_response, status = get_current_user()

    # If user doesn't exist and preview is not allowed
    if error_response and not group.get("allow_preview", False):
        posts_cursor = (
            mongo.db.posts.find({"group_id": group_obj_id})
            .sort("created_at", -1)
            .limit(5)
        )
    else:
        # User exists or preview allowed
        posts_cursor = mongo.db.posts.find({"group_id": group_obj_id}).sort(
            "created_at", -1
        )

    posts = []
    for post in posts_cursor:
        user_info = (
            mongo.db.users.find_one({"_id": post["user_id"]})
            if not post.get("anonymous")
            else None
        )
        post_data = {
            "post_id": str(post["_id"]),
            "title": post.get("title"),
            "text": post.get("text"),
            "username": user_info["username"] if user_info else None,
            "user_email": user_info["email"] if user_info else None,
            "likes": post.get("likes", []),
            "comments": post.get("comments", []),
        }
        posts.append(post_data)

    return jsonify(posts), 200


@app.route("/groups/<group_id>/posts/<post_id>", methods=["GET"])
def get_single_post_in_group(group_id, post_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    try:
        group_obj_id = ObjectId(group_id)
        post_obj_id = ObjectId(post_id)
    except Exception:
        return jsonify({"error": "Invalid group_id or post_id format"}), 400

    group = mongo.db.groups.find_one({"_id": group_obj_id})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    post = mongo.db.posts.find_one({"_id": post_obj_id, "group_id": group_obj_id})
    if not post:
        return jsonify({"error": "Post not found in this group"}), 404

    # Prepare the post data for output.
    post_data = {
        "post_id": str(post["_id"]),
        "user_id": str(post["user_id"]),
        "group_id": str(post["group_id"]),
        "title": post.get("title"),
        "text": post.get("text"),
        "image": post.get("image"),
        "tags": post.get("tags"),
        "likes": post.get("likes"),
        "comments": post.get("comments"),
        "created_at": (
            post.get("created_at").isoformat() if post.get("created_at") else None
        ),
        "updated_at": (
            post.get("updated_at").isoformat() if post.get("updated_at") else None
        ),
    }
    return jsonify(post_data), 200


@app.route("/groups/<group_id>/posts/<post_id>", methods=["PUT"])
def update_post_in_group(group_id, post_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    try:
        group_obj_id = ObjectId(group_id)
        post_obj_id = ObjectId(post_id)
    except Exception:
        return jsonify({"error": "Invalid group_id or post_id format"}), 400

    group = mongo.db.groups.find_one({"_id": group_obj_id})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    data = request.get_json()
    update_fields = {}
    for field in ["title", "text", "image", "tags"]:
        if field in data:
            update_fields[field] = data[field]
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    update_fields["updated_at"] = datetime.datetime.utcnow()

    post = mongo.db.posts.find_one({"_id": post_obj_id, "group_id": group_obj_id})
    if not post:
        return jsonify({"error": "Post not found in this group"}), 404

    # For example, only allow the post creator to update.
    if post["user_id"] != user["_id"]:
        return jsonify({"error": "Not authorized to update this post"}), 403

    mongo.db.posts.update_one({"_id": post_obj_id}, {"$set": update_fields})
    return jsonify({"message": "Post updated in group"}), 200


@app.route("/groups/<group_id>/posts/<post_id>", methods=["DELETE"])
def delete_post_in_group(group_id, post_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    try:
        group_obj_id = ObjectId(group_id)
        post_obj_id = ObjectId(post_id)
    except Exception:
        return jsonify({"error": "Invalid group_id or post_id format"}), 400

    group = mongo.db.groups.find_one({"_id": group_obj_id})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    post = mongo.db.posts.find_one({"_id": post_obj_id, "group_id": group_obj_id})
    if not post:
        return jsonify({"error": "Post not found in this group"}), 404

    if post["user_id"] != user["_id"]:
        return jsonify({"error": "Not authorized to delete this post"}), 403

    mongo.db.posts.delete_one({"_id": post_obj_id})
    return jsonify({"message": "Post deleted from group"}), 200


# ------------------ GROUP ROUTES ------------------


@app.route("/groups", methods=["POST"])
def create_group():
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    data = request.get_json()
    name = data.get("name")
    description = data.get("description", "")
    allow_preview = data.get("allow_preview", True)

    if not name:
        return jsonify({"error": "Group name is required"}), 400

    group = {
        "name": name,
        "description": description,
        "creator": user["_id"],
        "members": [user["_id"]],
        "allow_preview": allow_preview,
        "admins": [user["_id"]],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    result = mongo.db.groups.insert_one(group)
    return (
        jsonify({"message": "Group created", "group_id": str(result.inserted_id)}),
        201,
    )


@app.route("/groups/<group_id>", methods=["GET"])
def get_group(group_id):
    try:
        user, _, _ = get_current_user()
        user_id = str(user["_id"])
    except Exception:
        user = None
        user_id = None

    group = mongo.db.groups.find_one({"_id": ObjectId(group_id)})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    is_member = False
    if user_id:
        is_member = any(user_id == str(member) for member in group.get("members", []))

    # Fetch creator's username
    creator_id = group.get("creator")
    creator = mongo.db.users.find_one({"_id": ObjectId(creator_id)})
    creator_username = creator.get("username") if creator else "Unknown"

    group["_id"] = str(group["_id"])
    group["creator"] = creator_username
    group["members"] = [str(member) for member in group.get("members", [])]
    group["created_at"] = (
        group.get("created_at").isoformat() if group.get("created_at") else None
    )
    group["updated_at"] = (
        group.get("updated_at").isoformat() if group.get("updated_at") else None
    )
    group["is_member"] = is_member

    return jsonify(group), 200


@app.route("/groups", methods=["GET"])
def list_groups():
    groups_cursor = mongo.db.groups.find().sort("created_at", -1)
    groups = []

    for group in groups_cursor:
        creator_id = group.get("creator")
        creator = mongo.db.users.find_one({"_id": ObjectId(creator_id)})
        creator_username = creator.get("username") if creator else "Unknown"

        groups.append(
            {
                "group_id": str(group.get("_id")),
                "name": group.get("name"),
                "description": group.get("description"),
                "creator": creator_username,  # Use username here
                "allow_preview": group.get("allow_preview", True),
                "members": [str(member) for member in group.get("members", [])],
                "created_at": (
                    group.get("created_at").isoformat()
                    if group.get("created_at")
                    else None
                ),
                "updated_at": (
                    group.get("updated_at").isoformat()
                    if group.get("updated_at")
                    else None
                ),
            }
        )

    return jsonify(groups), 200


@app.route("/groups/<group_id>/join", methods=["POST"])
def join_group(group_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status
    try:
        group_obj_id = ObjectId(group_id)
    except Exception:
        return jsonify({"error": "Invalid group_id format"}), 400

    group = mongo.db.groups.find_one({"_id": group_obj_id})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    user_id = str(user["_id"])
    if any(user_id == str(member) for member in group.get("members", [])):
        return jsonify({"message": "User already a member"}), 200

    result = mongo.db.groups.update_one(
        {"_id": group_obj_id}, {"$push": {"members": user["_id"]}}
    )

    return jsonify({"message": "Joined group successfully"}), 200


@app.route("/groups/<group_id>/request-to-join", methods=["POST"])
def request_to_join(group_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    try:
        group_obj_id = ObjectId(group_id)
    except Exception:
        return jsonify({"error": "Invalid group_id format"}), 400

    group = mongo.db.groups.find_one({"_id": group_obj_id})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    creator = mongo.db.users.find_one({"_id": group.get("creator")})
    if not creator:
        return jsonify({"error": "Group creator not found"}), 404

    creator_email = creator.get("email")
    if not creator_email:
        return jsonify({"error": "Creator has no email"}), 400

    # Construct email
    subject = "MyStreet: Join Request"
    accept_link = (
        f"http://localhost:5000/groups/{group_id}/accept?user_id={user['_id']}"
    )
    decline_link = (
        f"http://localhost:5000/groups/{group_id}/decline?user_id={user['_id']}"
    )

    message_body = (
        f"{user['username']} ({user['email']}) wants to join your group '{group['name']}'.\n\n"
        f"Click to accept: {accept_link}\n"
        f"Click to decline: {decline_link}"
    )
    message = f"Subject:{subject}\n\n{message_body}"

    try:
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(
                user="muricamar2005@gmail.com", password="jpdvuuwfipwgninx"
            )
            connection.sendmail(
                from_addr="muricamar2005@gmail.com",
                to_addrs=creator_email,
                msg=message,
            )
        return jsonify({"message": "Request sent to group creator"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/groups/<group_id>/approve/<user_id>", methods=["GET"])
def approve_request(group_id, user_id):
    try:
        group_obj_id = ObjectId(group_id)
        user_obj_id = ObjectId(user_id)
    except Exception:
        return "Invalid ID format", 400

    result = mongo.db.groups.update_one(
        {"_id": group_obj_id}, {"$addToSet": {"members": user_obj_id}}
    )

    return "User approved and added to group", 200


@app.route("/groups/<group_id>/deny/<user_id>", methods=["GET"])
def deny_request(group_id, user_id):
    # You can log it or notify the user later
    return "Join request denied", 200


@app.route("/groups/<group_id>", methods=["PUT"])
def update_group(group_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    data = request.get_json()
    update_fields = {}
    for field in ["name", "description"]:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    # Optional: Only allow the creator to edit group details.
    group = mongo.db.groups.find_one({"_id": ObjectId(group_id)})
    if not group:
        return jsonify({"error": "Group not found"}), 404
    if group["creator"] != user["_id"]:
        return jsonify({"error": "Not authorized to update this group"}), 403

    update_fields["updated_at"] = datetime.datetime.utcnow()

    mongo.db.groups.update_one({"_id": ObjectId(group_id)}, {"$set": update_fields})
    return jsonify({"message": "Group updated"}), 200


@app.route("/groups/<group_id>", methods=["DELETE"])
def delete_group(group_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    group = mongo.db.groups.find_one({"_id": ObjectId(group_id)})
    if not group:
        return jsonify({"error": "Group not found"}), 404

    # Only allow the creator of the group to delete it.
    if group["creator"] != user["_id"]:
        return jsonify({"error": "Not authorized to delete this group"}), 403

    mongo.db.groups.delete_one({"_id": ObjectId(group_id)})
    return jsonify({"message": "Group deleted"}), 200


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
