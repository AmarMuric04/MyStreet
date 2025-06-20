import datetime
import random
import smtplib
from email.message import EmailMessage

import bcrypt
import jwt
from app import app, mongo
from bson import ObjectId
from flask import jsonify, request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pymongo import DESCENDING

from .session import clear_token, get_token, save_token

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

    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

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

    existing_user = mongo.db.users.find_one({"email": recipient_email})
    if existing_user:
        return {"status": "error", "message": "Email already registered"}, 400

    code = f"{random.randint(0, 999999):06}"
    subject = "Signup Code from MyStreet"
    message_body = f"Your signup code is: {code}"
    message = f"Subject:{subject}\n\n{message_body}"

    try:
        msg = EmailMessage()
        msg["From"] = "MyStreet <muricamar2005@gmail.com>"
        msg["To"] = recipient_email
        msg["Subject"] = "Welcome to MyStreet!"
        msg.set_content("This is the plain text fallback.")
        msg.add_alternative(
            f"""
            <html>
                <body>
                    <h1 style="color: #2e6c80;">Welcome to <strong>MyStreet</strong>!</h1>
                    <p>We're excited to have you on board. 🎉</p>
                    <p>{message_body}</p>
                </body>
            </html>
            """,
            subtype="html",
        )

        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(
                user="muricamar2005@gmail.com", password="jpdvuuwfipwgninx"
            )
            connection.send_message(msg)

        mongo.db.codes.delete_many({"email": recipient_email})
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

    mongo.db.codes.delete_one({"email": email})
    return {"status": "success", "message": "Code verified successfully"}, 200


# ------------------ PERSONAL ROUTES ------------------


def get_current_user():
    try:
        token = request.headers.get("Authorization").split()[1]
    except:
        token = ""
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


@app.route("/current_user", methods=["GET"])
def current_user():
    token = get_token()
    if not token:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        payload = jwt.decode(
            token,
            app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
    except ExpiredSignatureError:
        clear_token()
        return jsonify({"error": "Session expired"}), 401
    except InvalidTokenError:
        clear_token()
        return jsonify({"error": "Invalid token"}), 401

    email = payload.get("email")
    user = mongo.db.users.find_one({"email": email})
    if not user:
        clear_token()
        return jsonify({"error": "User not found"}), 401

    return (
        jsonify(
            {"user": {"username": user.get("username"), "email": user.get("email")}}
        ),
        200,
    )


@app.route("/users/me/groups", methods=["GET"])
def get_my_groups():
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    user_obj_id = user["_id"]

    groups_cursor = mongo.db.groups.find({"members": user_obj_id}).sort(
        "created_at", -1
    )

    groups = []
    for group in groups_cursor:
        groups.append(
            {
                "group_id": str(group["_id"]),
                "name": group.get("name"),
                "description": group.get("description"),
                "created_at": group.get("created_at"),
                "member_count": len(group.get("members", [])),
                "allow_preview": group.get("allow_preview", False),
            }
        )

    return jsonify(groups), 200


@app.route("/users/me/groups/posts", methods=["GET"])
def get_my_groups_posts():
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    user_obj_id = user["_id"]

    group_cursor = mongo.db.groups.find({"members": user_obj_id}, {"_id": 1})
    group_ids = [g["_id"] for g in group_cursor]
    if not group_ids:
        return jsonify([]), 200

    posts_cursor = mongo.db.posts.find({"group_id": {"$in": group_ids}}).sort(
        "created_at", -1
    )

    posts = []
    for post in posts_cursor:
        if not post.get("anonymous"):
            user_info = mongo.db.users.find_one({"_id": post["user_id"]})
        else:
            user_info = None

        liked_by_user = user_obj_id in post.get("likes", [])

        comment_count = mongo.db.comments.count_documents({"post_id": post["_id"]})

        posts.append(
            {
                "group_id": str(post["group_id"]),
                "post_id": str(post["_id"]),
                "username": user_info["username"] if user_info else None,
                "user_email": user_info["email"] if user_info else None,
                "title": post.get("title", "No Title"),
                "text": post.get("text", "No Content"),
                "likes": post.get("likes", []),
                "liked_by_user": liked_by_user,
                "comment_count": comment_count,
                "image": post.get("image"),
            }
        )

    return jsonify(posts), 200


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
    user_obj_id = user["_id"] if user else None

    if error_response and not group.get("allow_preview", False):
        posts_cursor = (
            mongo.db.posts.find({"group_id": group_obj_id})
            .sort("created_at", -1)
            .limit(5)
        )
    else:
        posts_cursor = mongo.db.posts.find({"group_id": group_obj_id}).sort(
            "created_at", -1
        )

    posts = []
    for post in posts_cursor:
        comments_cursor = mongo.db.comments.find({"post_id": post["_id"]}).sort(
            "created_at", 1
        )
        comment_count = mongo.db.comments.count_documents({"post_id": post["_id"]})

        comments = []
        liked_by_user = user_obj_id in post.get("likes", []) if user_obj_id else False
        created_by_current_user = (
            user_obj_id == post.get("user_id") if user_obj_id else False
        )

        user_info = (
            mongo.db.users.find_one({"_id": post["user_id"]})
            if not post.get("anonymous")
            else None
        )

        post_data = {
            "post_id": str(post["_id"]),
            "title": post.get("title"),
            "text": post.get("text"),
            "anonymous": post.get("anonymous"),
            "username": user_info["username"] if user_info else None,
            "user_email": user_info["email"] if user_info else None,
            "likes": post.get("likes", []),
            "liked_by_user": liked_by_user,
            "created_by_current_user": created_by_current_user,
            "comment_count": comment_count,
            "group_id": str(post.get("group_id")) if post.get("group_id") else None,
            "image": post.get("image"),
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
    for field in ["title", "text", "anonymous", "image", "tags"]:
        if field in data:
            update_fields[field] = data[field]
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    update_fields["updated_at"] = datetime.datetime.utcnow()

    post = mongo.db.posts.find_one({"_id": post_obj_id, "group_id": group_obj_id})
    if not post:
        return jsonify({"error": "Post not found in this group"}), 404

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

    creator_id = group.get("creator")
    creator = mongo.db.users.find_one({"_id": ObjectId(creator_id)})
    creator_username = creator.get("username") if creator else "Unknown"

    print(group)

    group["_id"] = str(group["_id"])
    group["creator"] = creator_username
    group["members"] = [str(member) for member in group.get("members", [])]
    group["description"] = group.get("description", "No description")
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
    name_query = request.args.get("name")
    creator_query = request.args.get("creator")

    query = {}

    if name_query:
        query["name"] = {"$regex": name_query, "$options": "i"}

    if creator_query:
        creator = mongo.db.users.find_one({"username": creator_query})
        if creator:
            query["creator"] = str(creator["_id"])
        else:
            return jsonify([]), 200

    groups_cursor = mongo.db.groups.find(query).sort("created_at", -1)
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
                "creator": creator_username,
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
    likes_str = [str(like) for like in likes]

    if user_id_str in likes_str:
        mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)}, {"$pull": {"likes": user["_id"]}}
        )
        message = "Like removed"
    else:
        mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)}, {"$push": {"likes": user["_id"]}}
        )
        message = "Post liked"
    return jsonify({"message": message}), 200


# ------------------ COMMENT ROUTES ------------------


@app.route("/posts/<post_id>/comments", methods=["GET"])
def get_post_comments(post_id):
    try:
        user, error_response, status = get_current_user()
        current_user_id = user["_id"] if user else None

        comments = mongo.db.comments.find({"post_id": ObjectId(post_id)})
        formatted = []

        for c in comments:
            is_current_user = (
                current_user_id == c.get("user_id") if current_user_id else False
            )

            formatted.append(
                {
                    "id": str(c["_id"]),
                    "username": c.get("username", "Anonymous"),
                    "message": c.get("message", ""),
                    "likes": c.get("likes", 0),
                    "date": c.get("created_at", datetime.datetime.utcnow()).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "is_current_user": is_current_user,
                }
            )
        return jsonify(formatted), 200

    except Exception as e:
        print("Error fetching comments:", e)
        return jsonify({"error": "Could not fetch comments"}), 500


@app.route("/posts/<post_id>/comment", methods=["POST"])
def add_comment(post_id):
    user, error_response, status = get_current_user()

    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "Comment text is required"}), 400

    comment = {
        "_id": ObjectId(),
        "post_id": ObjectId(post_id),
        "user_id": user["_id"],
        "username": user.get("username", "Anonymous"),
        "message": message,
        "likes": 0,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }

    mongo.db.comments.insert_one(comment)
    return jsonify({"message": "Comment added", "comment_id": str(comment["_id"])}), 201


@app.route("/posts/<post_id>/comment/<comment_id>/like", methods=["POST"])
def like_comment(post_id, comment_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    result = mongo.db.comments.update_one(
        {"_id": ObjectId(comment_id), "post_id": ObjectId(post_id)},
        {"$inc": {"likes": 1}},
    )

    if result.matched_count == 0:
        return jsonify({"error": "Comment not found"}), 404

    return jsonify({"message": "Comment liked"}), 200


@app.route("/posts/<post_id>/comment/<comment_id>", methods=["PUT"])
def edit_comment(post_id, comment_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    data = request.get_json()
    new_text = data.get("comment")
    if not new_text:
        return jsonify({"error": "New comment text is required"}), 400

    comment = mongo.db.comments.find_one(
        {"_id": ObjectId(comment_id), "post_id": ObjectId(post_id)}
    )
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    if comment["user_id"] != user["_id"]:
        return jsonify({"error": "Not authorized to edit this comment"}), 403

    mongo.db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": {"comment": new_text, "updated_at": datetime.datetime.utcnow()}},
    )
    return jsonify({"message": "Comment updated"}), 200


@app.route("/posts/<post_id>/comment/<comment_id>", methods=["DELETE"])
def delete_comment(post_id, comment_id):
    user, error_response, status = get_current_user()
    if error_response:
        return error_response, status

    comment = mongo.db.comments.find_one(
        {"_id": ObjectId(comment_id), "post_id": ObjectId(post_id)}
    )
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    if comment["user_id"] != user["_id"]:
        return jsonify({"error": "Not authorized to delete this comment"}), 403

    mongo.db.comments.delete_one({"_id": ObjectId(comment_id)})
    return jsonify({"message": "Comment deleted"}), 200
