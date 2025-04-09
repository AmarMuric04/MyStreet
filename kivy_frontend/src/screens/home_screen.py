from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from session import clear_token

Builder.load_file("kivy_frontend/src/screens/home_screen.kv")

class HomeScreen(MDScreen):
    def on_logout(self):
        clear_token()
        self.manager.current = "login"