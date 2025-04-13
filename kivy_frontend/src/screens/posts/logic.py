import json
import threading

import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivymd.uix.screen import MDScreen

from utils.session import get_token

Builder.load_file("kivy_frontend/src/screens/posts/design.kv")

class PostsScreen(MDScreen):
    posts_data = ListProperty([])
    group_id = StringProperty("") 

    def on_pre_enter(self):
        # Print the group_id and fetch group details to update the title label.
        print("Displaying posts for group:", self.group_id)
        threading.Thread(target=self.fetch_group_info_thread, daemon=True).start()

    def on_enter(self):
        self.show_loader()
        threading.Thread(target=self.fetch_posts_thread, daemon=True).start()

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
        if "post_button" in self.ids:
            self.ids.post_button.text = "Submit Post"
            self.ids.post_button.disabled = False

    def on_leave(self):
        self.posts_data = []
        self.hide_loader()

    def fetch_posts_thread(self):
        try:
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

        Clock.schedule_once(lambda dt: self.update_posts_data(data), 0)

    def update_posts_data(self, data):
        self.posts_data = data
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
                group_name = group.get("name", "Unknown Group")
                is_member = group.get("is_member", False)
                # Update the UI on the main thread.
                Clock.schedule_once(lambda dt: self.update_group_ui(group_name, is_member), 0)
            else:
                print(f"Error fetching group info: {response.status_code}")
        except Exception as e:
            print(f"Error fetching group info: {str(e)}")

    def update_group_ui(self, group_name, is_member):
        # Update the group title.
        self.ids.title.text = group_name
        # If not a member, show the join button.
        if not is_member:
            self.ids.join_btn.opacity = 1
            self.ids.join_btn.disabled = False
            self.ids.create_post_btn.opacity = 0
            self.ids.create_post_btn.disabled = True
        else:
            self.ids.join_btn.opacity = 0
            self.ids.join_btn.disabled = True
            self.ids.create_post_btn.opacity = 1
            self.ids.create_post_btn.disabled = False
            
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
                print("Joined group successfully")
                # Optionally refresh the group info.
                threading.Thread(target=self.fetch_group_info_thread, daemon=True).start()
            else:
                print(f"Error joining group: {response.status_code}")
        except Exception as e:
            print(f"Error in join_group_thread: {str(e)}")
        finally:
            # Re-enable the join button after the request is complete.
            Clock.schedule_once(lambda dt: setattr(self.ids.join_btn, "disabled", False), 0)

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
                f"http://localhost:5000/posts/{post_item.post_id}/like",
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
            content_cls=Builder.load_string(
                'MDTextField:\n    hint_text: "Enter comment text"\n    multiline: True'
            ),
            buttons=[
                MDButton(text="Submit", on_release=self.submit_comment),
                MDButton(text="Cancel", on_release=lambda x: self.dialog.dismiss())
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
                f"http://localhost:5000/posts/{post_id}/comment",
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
