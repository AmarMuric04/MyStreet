import datetime
import json
import threading

import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from utils.session import get_token

Builder.load_file("kivy_frontend/src/screens/posts/design.kv")

API_URL = "http://localhost:5000/posts"

class PostsScreen(MDScreen):
    posts_data = ListProperty([])

    def __init__(self, **kwargs):
        super(PostsScreen, self).__init__(**kwargs)
        self.dialog = None
        self.current_post_id = None

    def on_enter(self):
        self.show_loader()
        threading.Thread(target=self.fetch_posts_thread).start()

    def show_loader(self):
        if "loader" in self.ids:
            self.ids.loader.active = True
            self.ids.loader.opacity = 1

    def hide_loader(self):
        if "loader" in self.ids:
            self.ids.loader.active = False
            self.ids.loader.opacity = 0

    def update_post_status(self, msg):
        print(msg)
        self.ids.post_button.text = "Submit Post"
        self.ids.post_button.disabled = False

    def on_leave(self):
        self.posts_data = []
        self.hide_loader()
        
    def fetch_posts_thread(self):
        try:
            response = requests.get(
                API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                }
            )
            if response.status_code == 200:
                posts = response.json()
                data = [
                    {
                        "post_id": str(post.get("post_id")),
                        "username": post.get("username", "No Username"),
                        "user_email": post.get("user_email", "No Email"),
                        "title": post.get("title", "No Title"),
                        "text": post.get("text", "No Content"),
                        "like_count": len(post.get("likes", [])),
                        "liked_by_user": post.get("liked_by_user", False),
                        "comment_count": len(post.get("comments", []))
                    }
                    for post in posts
                ]
            else:
                data = []
                print(f"Error fetching posts: {response.status_code}")
        except Exception as e:
            data = []
            print(f"Error: {str(e)}")

        # Update posts_data in the main thread and hide loader.
        Clock.schedule_once(lambda dt: self.update_posts_data(data), 0)

    def update_posts_data(self, data):
        self.posts_data = data
        self.hide_loader()

    def toggle_like(self, post_item):
        previous_like_status = post_item.liked_by_user
        previous_like_count = post_item.like_count

        if post_item.liked_by_user:
            post_item.like_count -= 1
            post_item.liked_by_user = False
        else:
            post_item.like_count += 1
            post_item.liked_by_user = True

        threading.Thread(
            target=self.toggle_like_thread,
            args=(post_item, previous_like_status, previous_like_count),
            daemon=True
        ).start()

    def toggle_like_thread(self, post_item, previous_like_status, previous_like_count):
        try:
            response = requests.post(
                f"{API_URL}/{post_item.post_id}/like",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                }
            )
            if response.status_code != 200:
                raise Exception(f"Error toggling like: {response.status_code}")
        except Exception as e:
            post_item.liked_by_user = previous_like_status
            post_item.like_count = previous_like_count
            print(f"Error toggling like: {str(e)}")

    def prompt_comment(self, post_id):
        self.current_post_id = post_id
        self.dialog = MDDialog(
            title="Add Comment",
            type="custom",
            content_cls=MDTextField(hint_text="Enter comment text", multiline=True),
            buttons=[
                MDRaisedButton(text="Submit", on_release=self.submit_comment),
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def submit_comment(self, instance):
        comment_field = self.dialog.content_cls
        comment_text = comment_field.text.strip()
        if not comment_text:
            print("Error: Comment text is required.")
            return
        threading.Thread(
            target=self.submit_comment_thread,
            args=(self.current_post_id, comment_text),
            daemon=True
        ).start()
        self.dialog.dismiss()

    def submit_comment_thread(self, post_id, comment_text):
        try:
            response = requests.post(
                f"{API_URL}/{post_id}/comment",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                },
                data=json.dumps({"comment": comment_text})
            )
            if response.status_code == 201:
                threading.Thread(target=self.fetch_posts_thread, daemon=True).start()
            else:
                print(f"Error adding comment: {response.status_code}")
        except Exception as e:
            print(f"Error adding comment: {str(e)}")
