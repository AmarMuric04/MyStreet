import json
import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDListItem, MDListItemHeadlineText
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

try:
    Builder.load_file("frontend/src/screens/settings/design.kv")
except FileNotFoundError:
    Logger.error("SettingsScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"SettingsScreen: Error loading design file: {e}")

class SettingsScreen(MDScreen):
    """Settings screen with full functionality for user preferences."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_file = "user_settings.json"
        self.language_dialog = None
        self.delete_dialog = None
        self.load_settings()
    
    def show_snackbar(self, message):
        """Cross-platform message display"""
        snackbar = MDSnackbar(
            MDSnackbarText(text=message),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        )
        snackbar.open()
    
    def on_enter(self):
        """Called when the screen is entered - update UI with current settings."""
        self.update_ui_from_settings()
    
    def load_settings(self):
        """Load user settings from file or create default settings."""
        default_settings = {
            "dark_mode": False,
            "language": "English",
            "push_notifications": True,
            "email_notifications": True,
            "user_name": "John Doe",
            "user_email": "john.doe@email.com"
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
                for key, value in default_settings.items():
                    if key not in self.settings:
                        self.settings[key] = value
            else:
                self.settings = default_settings
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = default_settings
    
    def save_settings(self):
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def update_ui_from_settings(self):
        """Update UI elements to reflect current settings."""
        try:
            if hasattr(self.ids, 'dark_mode_switch'):
                self.ids.dark_mode_switch.active = self.settings.get("dark_mode", False)
            if hasattr(self.ids, 'notifications_switch'):
                self.ids.notifications_switch.active = self.settings.get("push_notifications", True)
            if hasattr(self.ids, 'email_notifications_switch'):
                self.ids.email_notifications_switch.active = self.settings.get("email_notifications", True)
        except Exception as e:
            print(f"Error updating UI: {e}")
    
    def go_back_to_profile(self):
        """Navigate back to profile screen."""
        try:
            self.manager.current = "profile"
        except Exception as e:
            print(f"Navigation error: {e}")
    
    def on_dark_mode_toggle(self, switch_instance, active_value):
        """Handle dark mode toggle."""
        self.settings["dark_mode"] = active_value
        self.save_settings()
        
        app = MDApp.get_running_app()
        if app:
            app.theme_cls.theme_style = "Dark" if app.theme_cls.theme_style == "Light" else "Light"
        
        print(f"Dark mode {'enabled' if active_value else 'disabled'}")
    
    def on_notifications_toggle(self, switch_instance, active_value):
        """Handle push notifications toggle."""
        self.settings["push_notifications"] = active_value
        self.save_settings()
        print(f"Push notifications {'enabled' if active_value else 'disabled'}")
    
    def on_email_notifications_toggle(self, switch_instance, active_value):
        """Handle email notifications toggle."""
        self.settings["email_notifications"] = active_value
        self.save_settings()
        print(f"Email notifications {'enabled' if active_value else 'disabled'}")
    
    def open_personal_info(self):
        """Open personal information screen/dialog."""
        print("Opening Personal Information...")
    
    def open_privacy_security(self):
        """Open privacy and security settings."""
        print("Opening Privacy & Security...")
    
    def open_change_password(self):
        """Open change password dialog/screen."""
        print("Opening Change Password...")
    
    def open_language_selector(self):
        """Open language selection dialog."""
        if not self.language_dialog:
            languages = ["English", "Spanish", "French", "German", "Italian", "Portuguese"]
            current_language = self.settings.get("language", "English")
            
            content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(300)
            )
            
            for language in languages:
                item = MDListItem(
                    MDListItemHeadlineText(text=language),
                  
                )
                content.add_widget(item)
            
            self.language_dialog = MDDialog(
                title="Select Language",
                content_cls=content,
                buttons=[
                    MDButton(
                        MDButtonText(text="CANCEL"),
                        on_release=self.close_language_dialog
                    ),
                ]
            )
        
        self.language_dialog.open()
    
    def select_language(self, language):
        """Select a new language."""
        self.settings["language"] = language
        self.save_settings()
        print(f"Language changed to: {language}")
        self.close_language_dialog()
    
    def close_language_dialog(self, *args):
        """Close language selection dialog."""
        if self.language_dialog:
            self.language_dialog.dismiss()
    
    def open_help_center(self):
        """Open help center."""
        print("Opening Help Center...")
    
    def open_contact_us(self):
        """Open contact us page."""
        print("Opening Contact Us...")
    
    def open_about(self):
        """Open about page."""
        print("Opening About...")
    
    def sign_out(self):
        """Handle user sign out."""
        print("Signing out...")
    
    def confirm_delete_account(self):
        """Show confirmation dialog for account deletion."""
        if not self.delete_dialog:
            self.delete_dialog = MDDialog(
                title="Delete Account",
                text="Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently lost.",
                buttons=[
                    MDButton(
                        MDButtonText(text="CANCEL"),
                        on_release=self.close_delete_dialog
                    ),
                    MDButton(
                        MDButtonText(text="DELETE"),
                        style="filled",
                        theme_bg_color="Custom",
                        md_bg_color="#F44336",
                        on_release=self.delete_account
                    ),
                ]
            )
        
        self.delete_dialog.open()
    
    def delete_account(self, *args):
        """Handle account deletion."""
        print("Account deleted")
        
        self.close_delete_dialog()
    
    def close_delete_dialog(self, *args):
        """Close delete account confirmation dialog."""
        if self.delete_dialog:
            self.delete_dialog.dismiss()
