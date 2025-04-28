import json
import os
import threading

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogContentContainer,
    MDDialogHeadlineText,
    MDDialogIcon,
    MDDialogSupportingText,
)
from kivymd.uix.divider import MDDivider
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from utils.session import get_token

Builder.load_file("frontend/src/screens/create_post/design.kv")


class CreatePost(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(
            select_path=self.select_path,
            exit_manager=self.exit_manager,
            preview=True,
        )
        self.selected_image_path = None
    group_id = StringProperty("")
    current_dialog = None 
    editing_post = ObjectProperty(None, allownone=True)
    
    def open_file_manager(self):
        start_path = "/"
        if platform == "win":
            start_path = "C:/"
        elif platform == "android":
            from android.storage import primary_external_storage_path
            start_path = primary_external_storage_path()

        self.file_manager.show(start_path)

    def select_path(self, path):
        self.exit_manager()
        self.selected_image_path = path
        self.ids.selected_image_label.text = os.path.basename(path)

    def exit_manager(self, *args):
        self.file_manager.close()
    
    import requests

    def upload_to_cloudinary(self, image_path):
        cloud_name = "dccik7g13"
        upload_preset = "somy3n3f"

        url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
        data = {"upload_preset": upload_preset}
        with open(image_path, "rb") as file_data:
            files = {"file": file_data}
            response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            return response.json()["secure_url"]
        else:
            print(f"Cloudinary upload failed: {response.text}")
            return None
    
    def create_post(self):
        title = self.ids.title_input.text.strip()
        text = self.ids.text_input.text.strip()
        if not title or not text:
            print("Error: Title and text are required.")
            return

        self.ids.post_button.text = "Submitting..."
        self.ids.post_button.disabled = True

        anonymous = self.ids.anonymous_checkbox.active

        image_url = None
        if self.selected_image_path:
            image_url = self.upload_to_cloudinary(self.selected_image_path)

        post_data = {
            "title": title,
            "text": text,
            "image": image_url, 
            "tags": [],
            "anonymous": anonymous
        }

        if self.editing_post:
            threading.Thread(target=self.update_post_thread, args=(post_data,), daemon=True).start()
        else:
            threading.Thread(target=self.create_post_thread, args=(post_data,), daemon=True).start()

    def update_post_thread(self, post_data):
        try:
            url = f"http://localhost:5000/groups/{self.group_id}/posts/{self.editing_post.post_id}"
            response = requests.put(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                },
                data=json.dumps(post_data)
            )
            if response.status_code == 200:
                msg = "Post updated successfully!"
                Clock.schedule_once(lambda dt: self.clear_inputs(), 0)
                app = App.get_running_app()
                posts_screen = app.root.ids.screen_manager.get_screen("posts")
                posts_screen.posts_fetched = False
                Clock.schedule_once(lambda dt: setattr(app.root.ids.screen_manager, "current", "posts"), 0)
                MDSnackbar(
                    MDSnackbarText(
                        text="Post updated successfully!",
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.5,
                ).open()
            else:
                msg = f"Error updating post: {response.status_code}"
        except Exception as e:
            msg = f"Error: {str(e)}"

        Clock.schedule_once(lambda dt: self.update_post_status(msg), 0)
            
    def create_post_thread(self, post_data):
        try:
            # Build the URL for posting to the specific group using group_id.
            url = f"http://localhost:5000/groups/{self.group_id}/posts"
            response = requests.post(
                url,
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
                posts_screen = app.root.ids.screen_manager.get_screen("posts")
                posts_screen.posts_fetched = False
                Clock.schedule_once(lambda dt: setattr(app.root.ids.screen_manager, "current", "posts"), 0)
                MDSnackbar(
                    MDSnackbarText(
                        text="Post added successfully!",
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.5,
                ).open()
            else:
                msg = f"Error creating post: {response.status_code}"
        except Exception as e:
            msg = f"Error: {str(e)}"

        Clock.schedule_once(lambda dt: self.update_post_status(msg), 0)

    def on_pre_enter(self):
        if self.editing_post:
            self.ids.title_input.text = self.editing_post.title
            self.ids.text_input.text = self.editing_post.text
            self.ids.anonymous_checkbox.active = self.editing_post.anonymous
            self.ids.post_button.text = "Update Post"
        else:
            self.clear_inputs()
            self.ids.post_button.text = "Create Post"


    def on_leave(self):
        self.editing_post = None
        
    def update_post_status(self, msg):
        print(msg)
        self.ids.post_button.text = "Submit Post"
        self.ids.post_button.disabled = False

    def clear_inputs(self):
        self.ids.title_input.text = ""
        self.ids.text_input.text = ""

    def close_dialog(self, *args):
        if self.current_dialog:
            self.current_dialog.dismiss()
            self.current_dialog = None

    def post_and_close_dialog(self, *args):
        # Call the post creation logic, then close the dialog.
        self.create_post()
        self.close_dialog()

    def show_alert_dialog(self):
        # ----------------------- Custom content container -----------------------
        content_container = MDDialogContentContainer(orientation="vertical")
        content_container.add_widget(MDDivider())
        
        post_preview = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(140)
        )
        
        image_preview = MDBoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(60)
        )
        
        image = MDIconButton(
            icon="account",
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        image_preview.add_widget(image)
        image_preview.add_widget(Widget())
        
        content_preview = MDBoxLayout(
            orientation='vertical'
        )
        # Example labels for the preview; adjust as needed
        content_preview.add_widget(MDLabel(text="You", bold=True, font_style="Body", role="large"))
        content_preview.add_widget(MDLabel(text=self.ids.title_input.text, bold=True, font_style="Body", role="large"))
        content_preview.add_widget(MDLabel(text=self.ids.text_input.text, font_style="Body", role="medium"))

        # Interactions preview: like, comment, bookmark and repost icons with labels.
        interactions_preview = MDBoxLayout(
            orientation="horizontal",
        )
        
        # Like box
        like_box = MDBoxLayout(orientation='horizontal')
        like_button = MDIconButton(
            icon="thumb-up-outline",
            pos_hint={"center_y": 0.5},
            on_release=lambda x: print("Toggle like")  # Replace with your like toggle method
        )
        like_label = MDLabel(
            text="0",
            size_hint=(None, None),
            size=(dp(20), dp(40)),
            halign="center",
            valign="middle",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        like_box.add_widget(like_button)
        like_box.add_widget(like_label)
        interactions_preview.add_widget(like_box)

        # Comment box
        comment_box = MDBoxLayout(orientation='horizontal')
        comment_button = MDIconButton(
            icon="comment-outline",
            pos_hint={"center_y": 0.5},
            on_release=lambda x: print("Toggle comment")  # Replace with your comment method
        )
        comment_label = MDLabel(
            text="0",
            size_hint=(None, None),
            size=(dp(20), dp(40)),
            halign="center",
            valign="middle",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        comment_box.add_widget(comment_button)
        comment_box.add_widget(comment_label)
        interactions_preview.add_widget(comment_box)

        # Bookmark box
        bookmark_box = MDBoxLayout(orientation='horizontal')
        bookmark_button = MDIconButton(
            icon="bookmark-outline",
            pos_hint={"center_y": 0.5},
            on_release=lambda x: print("Toggle bookmark")  # Replace with your bookmark method
        )
        bookmark_label = MDLabel(
            text="0",
            size_hint=(None, None),
            size=(dp(20), dp(40)),
            halign="center",
            valign="middle",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        bookmark_box.add_widget(bookmark_button)
        bookmark_box.add_widget(bookmark_label)
        interactions_preview.add_widget(bookmark_box)

        # Repost box
        repost_box = MDBoxLayout(orientation='horizontal')
        repost_button = MDIconButton(
            icon="repeat",
            pos_hint={"center_y": 0.5},
            on_release=lambda x: print("Toggle repost")  # Replace with your repost method
        )
        repost_label = MDLabel(
            text="0",
            size_hint=(None, None),
            size=(dp(20), dp(40)),
            halign="center",
            valign="middle",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        repost_box.add_widget(repost_button)
        repost_box.add_widget(repost_label)
        interactions_preview.add_widget(repost_box)

        content_preview.add_widget(interactions_preview)
        post_preview.add_widget(image_preview)
        post_preview.add_widget(content_preview)
        
        content_container.add_widget(post_preview)
        content_container.add_widget(MDDivider())

        # --------------------------- Button container --------------------------
        button_container = MDDialogButtonContainer(spacing="8dp")
        button_container.add_widget(Widget())  # For spacing

        # "Change" button closes the dialog
        button_container.add_widget(
            MDButton(
                MDButtonText(text="Change"),
                style="text",
                on_release=lambda x: self.close_dialog()
            )
        )
        # "Post" button calls create_post() then closes the dialog.
        button_container.add_widget(
            MDButton(
                MDButtonText(text="Post"),
                style="text",
                on_release=lambda x: self.post_and_close_dialog()
            )
        )

        # ------------------------------ Dialog ---------------------------------
        dialog = MDDialog(
            MDDialogIcon(icon="plus"),
            MDDialogHeadlineText(text="Continue with posting?"),
            MDDialogSupportingText(
                text="This is what your post will look like to other people, "
                     "are you happy with it or would you like to change something?"
            ),
            content_container,
            button_container,
        )
        dialog.open()
        self.current_dialog = dialog


