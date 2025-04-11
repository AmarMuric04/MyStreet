from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from utils.session import clear_token

Builder.load_file("kivy_frontend/src/screens/home/design.kv")

API_URL = "http://localhost:5000/posts"

class HomeScreen(MDScreen):
    def on_logout(self):
        clear_token()
        app = App.get_running_app()
        app.switch_screen("login")
        