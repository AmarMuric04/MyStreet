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

from session import get_token

Builder.load_file("kivy_frontend/src/screens/posts_screen.kv")

API_URL = "http://localhost:5000/posts"

class PostsScreen(MDScreen):
    posts_data = ListProperty([])

    def __init__(self, **kwargs):
        super(PostsScreen, self).__init__(**kwargs)
        self.dialog = None
        self.current_post_id = None
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
        print(msg)
        self.ids.post_button.text = "Submit Post"
        self.ids.post_button.disabled = False

    def clear_inputs(self):
        self.ids.title_input.text = ""
        self.ids.text_input.text = ""

    def fetch_posts(self, dt):
        try:
            response = requests.get(API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                },)
            if response.status_code == 200:
                posts = response.json()
                self.posts_data = [
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
                print(f"Error fetching posts: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")

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
            args=(post_item, previous_like_status, previous_like_count)
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
            args=(self.current_post_id, comment_text)
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
                Clock.schedule_once(lambda dt: self.fetch_posts(0), 0)
            else:
                print(f"Error adding comment: {response.status_code}")
        except Exception as e:
            print(f"Error adding comment: {str(e)}")
