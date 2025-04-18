import json
import threading

import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen

from utils.session import get_token

Builder.load_file("kivy_frontend/src/components/post_item/design.kv")

class PostItem(MDBoxLayout):
    def toggle_like(self, post_item):
        app = MDApp.get_running_app()
        user_data = app.user_data
        
        if not user_data: 
            return
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
            
    def open_menu(self, caller, post):
        menu_items = [
            {
                "text": "Report",
                "on_release": lambda x="Report": self.menu_callback(x),
            },
        ]
        if post.created_by_current_user:
            menu_items = [
                {
                    "text": "Delete",
                    "on_release": lambda x="Delete", y=post: self.menu_callback(x, y),
                },
                {
                    "text": "Edit",
                    "on_release": lambda x="Edit", y=post: self.menu_callback(x, y),
                },
            ]

        self.menu = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()
        
    def menu_callback(self, action, post):
        self.menu.dismiss()
        if action == "Delete":
            self.delete_post(post.group_id, post.post_id)
        elif action == "Edit":
            app = MDApp.get_running_app()
            create_post_screen = app.root.ids.screen_manager.get_screen("create_post")
            create_post_screen.editing_post = post
            create_post_screen.group_id = post.group_id
            app.root.ids.screen_manager.current = "create_post"

 
         
    def delete_post(self, group_id, post_id):
        """
        Calls DELETE /groups/<group_id>/posts/<post_id>
        """
        url = f"http://localhost:5000/groups/{group_id}/posts/{post_id}"
        headers = {}
        headers["Authorization"] = f"Bearer {get_token()}"

        # UrlRequest will do this on a background thread
        UrlRequest(
            url,
            on_success=self.on_delete_success,
            on_error=self.on_delete_error,
            on_failure=self.on_delete_error,
            req_headers=headers,
            method="DELETE",
        )

    def on_delete_success(self, request, result):
        # e.g. remove the widget, show toast, refresh list, etc.
        self.parent.remove_widget(self)
        print("Ok!")
        # Snackbar(text="Post deleted").open()

    def on_delete_error(self, request, error):
        print("Error")
        # Snackbar(text=f"Could not delete post: {error}").open()
