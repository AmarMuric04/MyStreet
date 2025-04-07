from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from backend_api import signup_api


class SignupScreen(MDScreen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        layout.add_widget(MDLabel(
            text="Sign Up",
            halign="center",
            theme_text_color="Primary",
            font_style="H4"
        ))

        self.email_input = MDTextField(
            hint_text="Enter your email",
            size_hint_x=1,
            pos_hint={"center_x": 0.5}
        )
        layout.add_widget(self.email_input)

        self.password_input = MDTextField(
            hint_text="Enter your password",
            password=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5}
        )
        layout.add_widget(self.password_input)

        self.status_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Hint",
            font_style="Caption"
        )
        layout.add_widget(self.status_label)

        signup_button = MDRectangleFlatButton(
            text="Sign Up",
            pos_hint={"center_x": 0.5}
        )
        signup_button.bind(on_press=self.on_signup)
        layout.add_widget(signup_button)

        switch_to_login = MDRectangleFlatButton(
            text="Already have an account? Login",
            pos_hint={"center_x": 0.5}
        )
        switch_to_login.bind(on_press=self.go_to_login)
        layout.add_widget(switch_to_login)

        self.add_widget(layout)

    def on_signup(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        response = signup_api(email, password)
        if response.get("status") == "success":
            self.status_label.text = "Signup successful! You can now log in."
            self.manager.current = "login"
        else:
            self.status_label.text = response.get("message", "Signup failed.")

    def go_to_login(self, instance):
        self.manager.current = "login"
