import json
import random

import requests

from session import get_token

# ========================
# CONFIG
# ========================
API_URL = "http://localhost:5000/posts"
AUTH_HEADERS = {
    "Authorization": f"Bearer {get_token().strip()}",
    "Content-Type": "application/json"
}

# ========================
# MOCK DATA
# ========================
mock_titles = [
    "My First Post",
    "Exploring Nature",
    "Coding Journey",
    "Daily Thoughts",
    "Photography Tips",
]

mock_texts = [
    "Today I went hiking and it was amazing!",
    "Learning Python has been a great experience so far.",
    "Here's a photo I took during sunset.",
    "Debugging code is like solving a mystery.",
    "Cloud computing is changing everything!",
]

mock_images = [
    "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    None,
    "https://res.cloudinary.com/demo/image/upload/v1681322312/example.jpg",
]

mock_tags = [
    ["nature", "travel"],
    ["python", "coding"],
    ["photography", "sunset"],
    ["debugging", "tech"],
    ["cloud", "AI"],
]


# ========================
# FUNCTION TO CREATE A POST
# ========================
def create_mock_post():
    post_data = {
        "title": random.choice(mock_titles),
        "text": random.choice(mock_texts),
        "image": random.choice(mock_images),
        "tags": random.choice(mock_tags),
    }
    print(post_data)
    print(get_token())

    response = requests.post(API_URL, headers=AUTH_HEADERS, data=json.dumps(post_data))

    if response.status_code == 201:
        print("✅ Post created:", response.json())
    else:
        print("❌ Failed to create post:", response.status_code)
        try:
            print(response.json())
        except:
            print(response.text)


# ========================
# MAIN
# ========================
if __name__ == "__main__":
    for _ in range(5):  # Create 5 mock posts
        create_mock_post()
