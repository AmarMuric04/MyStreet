
import time

from kivy.app import App
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

try:
    Builder.load_file("frontend/src/screens/change_password/design.kv")
except FileNotFoundError:
    Logger.error("ChangePasswordScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"ChangePasswordScreen: Error loading design file: {e}")


class ChangePasswordScreen(MDScreen):
    def show_snackbar(self, message):
        """Cross-platform message display"""
        snackbar = MDSnackbar(
            MDSnackbarText(text=message),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        )
        snackbar.open()
        
        self.ids.current.text = ""
        self.ids.new.text = ""
        self.ids.confirm.text = ""
        
        time.sleep(1)
        
        app = App.get_running_app()
        app.goto_screen("settings")