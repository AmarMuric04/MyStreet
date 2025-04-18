import json
import threading

import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from utils.session import get_token

Builder.load_file("kivy_frontend/src/screens/home/design.kv")

API_GROUPS_URL = "http://localhost:5000/users/me/groups"
PUBLIC_GROUPS_URL = "http://localhost:5000/groups"


class HomeScreen(MDScreen):
    my_groups_data = ListProperty([])
    groups_data = ListProperty([])
    posts_data = ListProperty([])
    
    cached_posts_data = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Debounce event for fetching public groups
        self._groups_search_event = None

    def on_enter(self):
        print("Fetching groups")
        self.fetch_my_groups()
        # Initial full fetch
        self._schedule_debounced_groups_fetch(0)
        threading.Thread(target=self.fetch_posts_thread, daemon=True).start() 
        Clock.schedule_once(self.check_login_and_show_button)

    def on_search_text(self, instance, value):
        self.posts_data = []
        
        if value == "":
            self.posts_data = self.cached_posts_data
            self.groups_data = []
            return
            
        # Cancel any pending fetch
        if self._groups_search_event:
            self._groups_search_event.cancel()
        # Schedule a fresh one after 0.5s
        self._groups_search_event = Clock.schedule_once(
            lambda dt: self._schedule_debounced_groups_fetch(), 0.5
        )

    def _schedule_debounced_groups_fetch(self, dt=0):
        threading.Thread(target=self.fetch_groups_thread, daemon=True).start()

    def fetch_groups_thread(self):
        try:
            search_input = self.ids.search_for_groups.text.strip()
            params = {}
            if search_input:
                params["name"] = search_input

            response = requests.get(
                PUBLIC_GROUPS_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}",
                },
                params=params,
            )

            if response.status_code == 200:
                groups = response.json()
                app = MDApp.get_running_app()
                is_logged_in = app.user_data
                data = [
                    {
                        "group_name": group.get("name", "No Name"),
                        "description": group.get("description", "No Description"),
                        "creator": f"Created by [b]@{group.get('creator', 'Unknown Creator')}[/b]",
                        "group_id": group.get("group_id", "No Id"),
                        "allow_preview": group.get("allow_preview", True),
                        "is_logged_in": is_logged_in,
                    }
                    for group in groups
                ]
            else:
                print(f"Error fetching groups: {response.status_code}")
                data = []
        except Exception as e:
            print(f"Error fetching groups: {e}")
            data = []

        Clock.schedule_once(lambda dt: self.update_groups_data(data), 0)

    def update_groups_data(self, data):
        self.groups_data = data

    #
    # ——— My Groups Fetch (unchanged) ——————————————————————————————
    #
    def fetch_my_groups(self):
        threading.Thread(target=self.fetch_my_groups_thread, daemon=True).start()

    def fetch_my_groups_thread(self):
        try:
            response = requests.get(
                API_GROUPS_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}",
                },
            )
            if response.status_code == 200:
                groups = response.json()
                app = MDApp.get_running_app()
                is_logged_in = app.user_data
                data = [
                    {
                        "group_name": group.get("name", "No Name"),
                        "description": group.get("description", "No Description"),
                        "creator": f"Created by [b]@{group.get('creator', 'Unknown Creator')}[/b]",
                        "group_id": group.get("group_id", "No Id"),
                        "allow_preview": group.get("allow_preview", True),
                        "is_logged_in": is_logged_in,
                    }
                    for group in groups
                ]
            else:
                print(f"Error fetching my groups: {response.status_code}")
                data = []
        except Exception as e:
            print(f"Error fetching my groups: {e}")
            data = []

        Clock.schedule_once(lambda dt: self.update_my_groups_data(data), 0)

    def update_my_groups_data(self, data):
        self.my_groups_data = data

    #
    # ——— Posts Fetch (unchanged) ————————————————————————————————
    #
    def fetch_posts_thread(self):
        try:
            url = f"{API_GROUPS_URL}/posts"
            response = requests.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}",
                },
            )
            if response.status_code == 200:
                posts = response.json()
                print(posts)
                data = [
                    {
                        "post_id": str(post.get("post_id")),
                        "username": f"@{post['username']}"
                        if post.get("username")
                        else "Posted anonymously",
                        "user_email": f" · {post['user_email']}"
                        if post.get("user_email")
                        else "",
                        "title": post.get("title", "No Title"),
                        "text": post.get("text", "No Content"),
                        "like_count": len(post.get("likes", [])),
                        "liked_by_user": post.get("liked_by_user", False),
                        "comment_count": len(post.get("comments", [])),
                        "created_by_current_user": post.get("created_by_current_user", False),
                        "group_id": post.get("group_id", None)
                    }
                    for post in posts
                ]
            else:
                print(f"Error fetching posts: {response.status_code}")
                data = []
        except Exception as e:
            print(f"Error: {e}")
            data = []

        Clock.schedule_once(lambda dt: self.update_posts_data(data), 0)

    def update_posts_data(self, data):
        self.posts_data = data
        self.cached_posts_data = data

    #
    # ——— UI Helpers ——————————————————————————————————————————————
    #
    def check_login_and_show_button(self, dt):
        app = MDApp.get_running_app()
        is_logged_in = app.user_data
        self.ids.create_group_btn.opacity = 1 if is_logged_in else 0
        self.ids.create_group_btn.disabled = 0 if is_logged_in else 1

    def request_to_join(self, group_id):
        try:
            token = get_token()
            response = requests.post(
                f"http://localhost:5000/groups/{group_id}/request-to-join",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
            )
            if response.status_code != 200:
                data = response.json()
                print("Join error:", data.get("error", response.status_code))
        except Exception as e:
            print(f"Error sending join request: {e}")

    def handle_group_press(self, group_id, allow_preview):
        if allow_preview:
            self.manager.get_screen("posts").group_id = group_id
            self.manager.current = "posts"
        else:
            self.request_to_join(group_id)
