from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from backend_api import signup_api


class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Sign Up", font_size=24, color="black"))
        
        self.email_input = TextInput(hint_text="Enter your email", size_hint=(1, None), height=40)
        layout.add_widget(self.email_input)
        
        
        self.password_input = TextInput(hint_text="Enter your password", password=True, size_hint=(1, None), height=40)
        layout.add_widget(self.password_input)
        
        self.status_label = Label(text="", font_size=14)
        layout.add_widget(self.status_label)
        
        signup_button = Button(text="Sign Up", size_hint=(1, None), height=40)
        signup_button.bind(on_press=self.on_signup)
        layout.add_widget(signup_button)
        
        switch_to_login = Button(text="Already have an account? Login", size_hint=(1, None), height=40)
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
