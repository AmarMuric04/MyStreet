import json
import threading

import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen

from utils.session import get_token

Builder.load_file("frontend/src/screens/posts/design.kv")

class PostsScreen(MDScreen):
    posts_data = ListProperty([])
    group_id = StringProperty("")
    is_loading_posts  = BooleanProperty(False)

    def on_pre_enter(self):
        if len(self.posts_data) == 0:
            self.show_loader()
            
        threading.Thread(target=self.fetch_group_info_thread, daemon=True).start()
        threading.Thread(target=self.fetch_posts_thread, daemon=True).start()

    def show_loader(self):
        self.ids.loader.active = True
        self.ids.loader.opacity = 1

    def hide_loader(self):
        self.ids.loader.active = False
        self.ids.loader.opacity = 0

    def update_post_status(self, msg):
        self.ids.post_button.text = "Submit Post"
        self.ids.post_button.disabled = False

    def on_leave(self):
        self.posts_data = []
        self.group_id = ""
        self.is_loading_posts = False
        self.hide_loader()
        self.ids.title.text = ""
        self.ids.description.text = ""

    def fetch_posts_thread(self):
        try:
            self.is_loading_posts = True
            url = f"http://localhost:5000/groups/{self.group_id}/posts"
            response = requests.get(
                url,
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
                        "username": f"@{post['username']}" if post.get("username") else "Posted anonymously",
                        "user_email": f" · {post['user_email']}" if post.get("user_email") else "",
                        "title": post.get("title", "No Title"),
                        "text": post.get("text", "No Content"),
                        "like_count": len(post.get("likes", [])),
                        "liked_by_user": post.get("liked_by_user", False),
                        "anonymous": post.get("anonymous", False),
                        "comment_count": post.get("comment_count", 0),
                        "created_by_current_user": post.get("created_by_current_user", False),
                        "group_id": post.get("group_id", None),
                        "image_url": post.get("image", "")
                    }
                    for post in posts
                ]
            else:
                data = []
                print(f"Error fetching posts: {response.status_code}")
        except Exception as e:
            data = []
            print(f"Error: {str(e)}")
        self.is_loading_posts = False
        

        Clock.schedule_once(lambda dt: self.update_posts_data(data), 0)

    def update_posts_data(self, data):
        self.posts_data = data
        print(self.posts_data)
        self.hide_loader()

    def fetch_group_info_thread(self):
        try:
            url = f"http://localhost:5000/groups/{self.group_id}"
            response = requests.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                }
            )
            if response.status_code == 200:
                group = response.json()
                Clock.schedule_once(lambda dt: self.update_group_ui(group), 0)
            else:
                print(f"Error fetching group info: {response.status_code}")
        except Exception as e:
            print(f"Error fetching group info: {str(e)}")

    def update_group_ui(self, group):
        self.ids.title.text = group.get("name", "Unknown Group")
        self.ids.description.text = group.get("description", "")
        
        is_member = group.get("is_member", False)
        app = MDApp.get_running_app()
        user_data = app.user_data
        if not is_member and user_data:
            self.ids.join_btn.opacity = 1
            self.ids.join_btn.disabled = False
            self.ids.create_post_btn.disabled = True
            self.ids.create_post_btn.opacity = 0
        elif user_data and is_member:
            self.ids.join_btn.opacity = 0
            self.ids.join_btn.disabled = True
            self.ids.create_post_btn.disabled = False
            self.ids.create_post_btn.opacity = 1
            
    def join_group(self):
        self.ids.join_btn.disabled = True
        threading.Thread(target=self.join_group_thread, daemon=True).start()

    def join_group_thread(self):
        try:
            url = f"http://localhost:5000/groups/{self.group_id}/join"
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                }
            )
            if response.status_code == 200:
                Clock.schedule_once(lambda dt: self.on_join_success(), 0)
                threading.Thread(target=self.fetch_group_info_thread, daemon=True).start()
            else:
                print(f"Error joining group: {response.status_code}")
        except Exception as e:
            print(f"Error in join_group_thread: {str(e)}")
        finally:
            Clock.schedule_once(lambda dt: setattr(self.ids.join_btn, "disabled", False), 0)
    def on_join_success(self):
        self.ids.join_btn.opacity = 0
        self.ids.create_post_btn.opacity = 1
        self.ids.create_post_btn.disabled = False