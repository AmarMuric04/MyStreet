from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from backend_api import login_api
from session import save_token


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Login", font_size=24, color="black"))
        
        self.email_input = TextInput(hint_text="Enter your email", size_hint=(1, None), height=40)
        layout.add_widget(self.email_input)
        
        self.password_input = TextInput(hint_text="Enter your password", password=True, size_hint=(1, None), height=40)
        layout.add_widget(self.password_input)
        
        self.status_label = Label(text="", font_size=14)
        layout.add_widget(self.status_label)
        
        login_button = Button(text="Login", size_hint=(1, None), height=40)
        login_button.bind(on_press=self.on_login)
        layout.add_widget(login_button)
        
        switch_to_signup = Button(text="Don't have an account? Sign up", size_hint=(1, None), height=40)
        switch_to_signup.bind(on_press=self.go_to_signup)
        layout.add_widget(switch_to_signup)
        
        self.add_widget(layout)

    def on_login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        response = login_api(email, password)
        if response.get("status") == "success":
            self.status_label.text = "Login successful!"
            save_token(response.get("token")) 
            self.manager.current = "home"
        else:
            self.status_label.text = response.get("message", "Login failed.")

    def go_to_signup(self, instance):
        self.manager.current = "signup"
