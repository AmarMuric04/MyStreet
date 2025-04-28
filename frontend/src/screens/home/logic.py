import json
from threading import Lock, Thread

import requests
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from components.post_item.logic import PostItem

Factory.register('PostItem', cls=PostItem)
from utils.session import get_token

Builder.load_file("frontend/src/screens/home/design.kv")

API_GROUPS_URL = "http://localhost:5000/users/me/groups"
PUBLIC_GROUPS_URL = "http://localhost:5000/groups"


class HomeScreen(MDScreen):
    my_groups_data = ListProperty([])
    groups_data = ListProperty([])
    posts_data = ListProperty([])
    cached_posts_data = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._groups_search_event = None
        self._latest_search_value = ""
        self._fetch_lock = Lock()
    
    def on_leave(self):
        self.ids.search_for_groups.text = ""

    def on_enter(self):
        print("Fetching groups")
        self.fetch_my_groups()
        # Initial full fetch
        self._schedule_debounced_groups_fetch(0)
        Thread(target=self.fetch_posts_thread, daemon=True).start() 
        Clock.schedule_once(self.check_login_and_show_button)

    def on_search_text(self, instance, value):
        self.posts_data = []
        self._latest_search_value = value

        if value == "":
            if self._groups_search_event:
                self._groups_search_event.cancel()
            self.groups_data = []
            self.ids.groups_view.size_hint = (1, 0)
            self.posts_data = self.cached_posts_data
            return

        if self._groups_search_event:
            self._groups_search_event.cancel()

        self._groups_search_event = Clock.schedule_once(
            lambda dt: self._schedule_debounced_groups_fetch(value), 0.5
        )
    def _schedule_debounced_groups_fetch(self, value):
        Thread(target=self.fetch_groups_thread, args=(value,), daemon=True).start()

    def fetch_groups_thread(self, search_input):
        with self._fetch_lock:
            try:
                search_input = search_input.strip()
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

        # Only update if current search input matches the latest one
        if search_input == self._latest_search_value and search_input != "":
            Clock.schedule_once(lambda dt: (
                self.update_groups_data(data)
            ), 0)

    def update_groups_data(self, data):
        self.groups_data = data
        self.ids.groups_view.size_hint = (1, 1)

    def fetch_my_groups(self):
        Thread(target=self.fetch_my_groups_thread, daemon=True).start()

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
                        "anonymous": post.get("anonymous", False),
                        "comment_count": post.get("comment_count", 0),
                        "created_by_current_user": post.get("created_by_current_user", False),
                        "group_id": post.get("group_id", None),
                        "image_url": post.get("image", "")  
                        
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
