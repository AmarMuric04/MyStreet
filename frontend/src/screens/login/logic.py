from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from utils.auth import login_api

Builder.load_file("frontend/src/screens/login/design.kv")

class LoginScreen(MDScreen):
    def login_helper(self):
        self.ids.login_button.text = "Checking..."
        self.ids.login_button.disabled = True
        Clock.schedule_once(self.on_login, 0.1)

    def on_login(self, dt):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()
        response = login_api(email, password)
        if response.get("status") == "success":
            self.ids.email_input.text = ""
            self.ids.password_input.text = ""

            app = App.get_running_app()
            app.update_navigation_drawer()
            app.root.ids.screen_manager.current = 'home'
        else:
            self.ids.email_input.error = True
            self.ids.email_input.helper_text = "Invalid credentials"
            self.ids.email_input.helper_text_mode = "on_error"
            self.ids.password_input.error = True
            self.ids.password_input.helper_text = "Invalid credentials"
            self.ids.password_input.helper_text_mode = "on_error"

        self.ids.login_button.disabled = False
        self.ids.login_button.text = "Log In"
