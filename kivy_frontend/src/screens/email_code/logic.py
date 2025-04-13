from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from utils.auth import send_code_api, signup_api, verify_code_api

Builder.load_file("kivy_frontend/src/screens/email_code/design.kv")

class EmailCode(MDScreen):
    def on_enter(self):
        app = App.get_running_app()
        signup_data = getattr(app, "signup_data", None)
        email = signup_data.get("email") if signup_data else "your email"
        self.ids.email_label.text = f"We sent a code to {email}"

    def proceed(self):
        self.ids.verify_button.text = "Verifying..."
        self.ids.verify_button.disabled = True
        Clock.schedule_once(self.on_verify, 0.1)

    def on_verify(self):
        code = self.ids.code_input.text.strip()

        if not code:
            self.ids.code_input.error = True
            self.ids.code_input.helper_text = "Please enter the verification code."
            self.ids.code_input.helper_text_mode = "on_error"
            self.reset_button()
            return

        app = App.get_running_app()
        signup_data = getattr(app, "signup_data", None)

        if not signup_data:
            self.ids.code_input.error = True
            self.ids.code_input.helper_text = "No signup data found. Please restart the signup process."
            self.ids.code_input.helper_text_mode = "on_error"
            self.reset_button()
            return

        email = signup_data.get("email")
        verify_response = verify_code_api(email, code)

        if verify_response.get("status") == "success":
            signup_response = signup_api(
                email,
                signup_data.get("password"),
                signup_data.get("username")
            )
            if signup_response.get("status") == "success":
                app.signup_data = None
                app.root.ids.screen_manager.current = "login"
            else:
                self.ids.code_input.error = True
                self.ids.code_input.helper_text = signup_response.get("message", "Signup failed.")
                self.ids.code_input.helper_text_mode = "on_error"
                self.reset_button()
        else:
            self.ids.code_input.error = True
            self.ids.code_input.helper_text = verify_response.get("message", "Verification failed.")
            self.ids.code_input.helper_text_mode = "on_error"
            self.reset_button()

    def on_send_again(self):
        app = App.get_running_app()
        signup_data = getattr(app, "signup_data", None)
        
        email = signup_data.get("email")
        
        response = send_code_api(signup_data.get("email"))
        if response.get("status") == "success":
            pass
        else:
            pass

    def reset_button(self):
        self.ids.verify_button.text = "Verify"
        self.ids.verify_button.disabled = False
