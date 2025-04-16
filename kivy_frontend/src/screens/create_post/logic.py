import json
import threading

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
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
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from utils.session import get_token

Builder.load_file("kivy_frontend/src/screens/create_post/design.kv")


class CreatePost(MDScreen):
    group_id = StringProperty("")
    current_dialog = None  # store the dialog instance

    def create_post(self):
        title = self.ids.title_input.text.strip()
        text = self.ids.text_input.text.strip()
        print(title, text)
        if not title or not text:
            print("Error: Title and text are required.")
            return

        self.ids.post_button.text = "Submitting Post..."
        self.ids.post_button.disabled = True

        anonymous = self.ids.anonymous_checkbox.active

        post_data = {
            "title": title,
            "text": text,
            "image": None,
            "tags": [],
            "anonymous": anonymous  
        }
        threading.Thread(target=self.create_post_thread, args=(post_data,), daemon=True).start()

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


