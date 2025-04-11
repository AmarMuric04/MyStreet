import json
import threading

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from utils.session import get_token

Builder.load_file("kivy_frontend/src/screens/create_post/design.kv")

API_URL = "http://localhost:5000/posts"

class CreatePost(MDScreen):
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
        # Mark the thread as daemon so it doesn't hang the app on exit.
        threading.Thread(target=self.create_post_thread, args=(post_data,), daemon=True).start()

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
                app = App.get_running_app()
                posts_screen = app.root.get_screen("posts")
                posts_screen.posts_fetched = False
                # Now, switch to the posts screen so that on_enter triggers a refetch.
                Clock.schedule_once(lambda dt: app.switch_screen("posts"), 0)
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
