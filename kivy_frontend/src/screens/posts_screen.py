import json
import threading

import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen

from session import get_token

Builder.load_file("kivy_frontend/src/screens/posts_screen.kv")

API_URL = "http://localhost:5000/posts" 

class PostsScreen(MDScreen):
    # This property holds a list of dictionaries for the RecycleView to display.
    posts_data = ListProperty([])

    def __init__(self, **kwargs):
        super(PostsScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.fetch_posts, 0)

    def create_post(self):
        title = self.ids.title_input.text.strip()
        text = self.ids.text_input.text.strip()
        if not title or not text:
            print("Error: Title and text are required.")
            return

        self.ids.post_button.text = "Submitting Post..."
        self.ids.post_button.disabled = True

        post_data = {
            "title": title,
            "text": text,
            "image": None,
            "tags": []
        }
        threading.Thread(target=self.create_post_thread, args=(post_data,)).start()

    def create_post_thread(self, post_data):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                },
                data=json.dumps(post_data)
            )
            if response.status_code == 201:
                msg = "Post created successfully!"
                Clock.schedule_once(lambda dt: self.clear_inputs(), 0)
                Clock.schedule_once(lambda dt: self.fetch_posts(0), 0)
            else:
                msg = f"Error creating post: {response.status_code}"
        except Exception as e:
            msg = f"Error: {str(e)}"

        Clock.schedule_once(lambda dt: self.update_post_status(msg), 0)

    def update_post_status(self, msg):
        # For simplicity, we print the message. You could update a status label in the kv design if desired.
        print(msg)
        self.ids.post_button.text = "Submit Post"
        self.ids.post_button.disabled = False

    def clear_inputs(self):
        self.ids.title_input.text = ""
        self.ids.text_input.text = ""

    def fetch_posts(self, dt):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                posts = response.json()
                # Prepare the data for the RecycleView.
                self.posts_data = [
                    {
                        "user_email": post.get("user_email", "Invalid Email"),
                        "title": post.get("title", "No Title"),
                        "text": post.get("text", "No Content")
                    }
                    for post in posts
                ]
            else:
                print(f"Error fetching posts: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")
