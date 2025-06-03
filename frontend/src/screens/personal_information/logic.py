import time

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

try:
    Builder.load_file("frontend/src/screens/personal_information/design.kv")
except FileNotFoundError:
    Logger.error("PersonalScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"PersonalScreen: Error loading design file: {e}")
    
class PersonalInfoScreen(MDScreen):
    """
    Personal Information Screen - allows users to edit their profile information
    """
    
    def on_enter(self):
        """Called when screen is entered"""
        app = App.get_running_app()
        
        self.ids.username_field.text = app.user_data['username']
        self.ids.email_field.text = app.user_data['email']
    
    def save(self):
        app = App.get_running_app()
      
        app.user_data['bio'] = self.ids.bio_field.text
        app.user_data['username'] = self.ids.username_field.text
    
        time.sleep(1)
        
        app.show_snackbar("Profile updated successfully!")
        app.goto_screen("settings")