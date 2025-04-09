from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from backend_api import login_api
from session import save_token

Builder.load_file("kivy_frontend/src/screens/login_screen.kv")

class LoginScreen(MDScreen):
    def login_helper(self):
        self.ids.login_button.text = "Checking..."
        Clock.schedule_once(self.on_login, 0.1)

    def on_login(self, dt):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()
        response = login_api(email, password)
        if response.get("status") == "success":
            self.ids.email_input.text = ""
            self.ids.password_input.text = ""
            save_token(response.get("token"))
            self.manager.current = "home"
            self.ids.login_button.text = "Log In"
        else:
            self.ids.login_button.text = "Log In"
            self.ids.email_input.error = True
            self.ids.email_input.helper_text = "Invalid credentials"
            self.ids.email_input.helper_text_mode = "on_error"
            self.ids.password_input.error = True
            self.ids.password_input.helper_text = "Invalid credentials"
            self.ids.password_input.helper_text_mode = "on_error"

    def go_to_signup(self):
        self.manager.current = "signup"
