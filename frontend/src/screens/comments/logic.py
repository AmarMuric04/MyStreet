import json
import threading

import requests
from kivy.clock import mainthread
from kivy.graphics import Color, Ellipse
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.textfield import MDTextField

from utils.session import get_token

Builder.load_file("frontend/src/screens/comments/design.kv")


class Comments(MDScreen):
    def build(self):
        return Builder.load_string(kv)
    
    def on_enter(self):
        print("Getting comments")
        self.fetch_and_display_comments(self.post_id)

    def submit_comment(self):
        comment_text = self.ids.comment_input.text.strip()
        if not comment_text:
            print("Comment is empty")
            return

        threading.Thread(
            target=self.submit_comment_thread,
            args=(self.post_id, comment_text),
            daemon=True
        ).start()
        self.ids.comment_input.text = ""

    def submit_comment_thread(self, post_id, comment_text):
        try:
            response = requests.post(
                f"http://localhost:5000/posts/{post_id}/comment",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}",
                },
                data=json.dumps({"message": comment_text}),
            )
            if response.status_code == 201:
                self.fetch_and_display_comments(post_id)
            else:
                print(f"Failed to post comment: {response.status_code}")
        except Exception as e:
            print(f"Error posting comment: {e}")

    def fetch_and_display_comments(self, post_id):
        try:
            response = requests.get(f"http://localhost:5000/posts/{post_id}/comments", headers={"Authorization": f"Bearer {get_token()}"})
            if response.status_code == 200:
                comments_data = response.json()
                self.update_comments_view(comments_data)
                print(comments_data)
            else:
                print("Failed to fetch comments:", response.status_code)
        except Exception as e:
            print("Error fetching comments:", str(e))

    @mainthread
    def update_comments_view(self, comments):
        self.ids.console_rv.data = [
            {"message": c["message"], "username": c["username"], "is_current_user": c["is_current_user"]} for c in comments
        ]
