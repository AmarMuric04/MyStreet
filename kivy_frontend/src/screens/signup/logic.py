from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from utils.auth import send_code_api

Builder.load_file("kivy_frontend/src/screens/signup/design.kv")


class SignupScreen(MDScreen):
    def signup_helper(self):
        self.ids.signup_button.text = "Checking..."
        self.ids.signup_button.disabled = True
        Clock.schedule_once(self.on_signup, 0.1)

    def on_signup(self, dt):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()
        username = self.ids.username_input.text.strip()

        response = send_code_api(email)
        if response.get("status") == "success":
            app = App.get_running_app()
            app.signup_data = {
                "email": email,
                "password": password,
                "username": username,
            }
            self.ids.email_input.text = ""
            self.ids.password_input.text = ""
            self.ids.username_input.text = ""
            app.root.ids.screen_manager.current = "email_code"
        else:
            self.ids.email_input.error = True
            self.ids.email_input.helper_text = response.get("message", "Signup failed.")
            self.ids.email_input.helper_text_mode = "on_error"
        self.ids.signup_button.text = "Sign Up"
        self.ids.signup_button.disabled = False
