from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from session import clear_token


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        layout.add_widget(MDLabel(
            text="Home Page",
            halign="center",
            theme_text_color="Primary",
            font_style="H4"
        ))

        logout_button = MDRectangleFlatButton(
            text="Log Out",
            pos_hint={"center_x": 0.5}
        )
        logout_button.bind(on_press=self.on_logout)
        layout.add_widget(logout_button)

        switch_to_posts = MDRectangleFlatButton(
            text="View Posts",
            pos_hint={"center_x": 0.5}
        )
        switch_to_posts.bind(on_press=self.go_to_posts)
        layout.add_widget(switch_to_posts)

        self.add_widget(layout)

    def on_logout(self, instance):
        clear_token()
        self.manager.current = "login"

    def go_to_posts(self, instance):
        self.manager.current = "posts"
