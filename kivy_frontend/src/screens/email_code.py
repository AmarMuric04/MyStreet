from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from utils.auth import signup_api, verify_code_api

Builder.load_file("kivy_frontend/src/screens/email_code.kv")

class EmailCode(MDScreen):
    def verify_helper(self):
        self.ids.verify_button.text = "Verifying..."
        self.ids.verify_button.disabled = True
        Clock.schedule_once(self.on_verify, 0.1)

    def on_verify(self, dt):
        code = self.ids.code_input.text.strip()
        if not code:
            self.ids.code_input.error = True
            self.ids.code_input.helper_text = "Please enter the verification code."
            self.ids.code_input.helper_text_mode = "on_error"
            self.ids.verify_button.text = "Verify"
            self.ids.verify_button.disabled = False
            return

        app = App.get_running_app()
        signup_data = getattr(app, "signup_data", None)
        if not signup_data:
            self.ids.code_input.error = True
            self.ids.code_input.helper_text = "Signup data not found. Please try again."
            self.ids.code_input.helper_text_mode = "on_error"
            self.ids.verify
