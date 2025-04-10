from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from utils.session import clear_token

Builder.load_file("kivy_frontend/src/screens/home_screen.kv")

class HomeScreen(MDScreen):
    def on_logout(self):
        clear_token()
        app = App.get_running_app()
        App.switch_screen("login")