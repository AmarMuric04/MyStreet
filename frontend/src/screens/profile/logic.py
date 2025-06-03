from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

try:
    Builder.load_file("frontend/src/screens/profile/design.kv")
except FileNotFoundError:
    Logger.error("ProfileScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"ProfileScreen: Error loading design file: {e}")


class ProfileScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
    
    
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
        """Called when screen is entered - load user data"""
        app = App.get_running_app()
        
        self.user_data = app.user_data
        self.load_profile_data()
    
    def load_profile_data(self):
        """Load and display user profile data"""
        try:
            self.update_profile_display()
        except Exception as e:
            self.show_snackbar(f"Error loading profile: {str(e)}")
    
    def update_profile_display(self):
        """Update the UI with current user data"""
        name_label = self.ids.name_label
        email_label = self.ids.email_label
        bio_label = self.ids.bio_label
        
        if name_label:
            name_label.text = f"[b]{self.user_data['username']}[/b]"
        if email_label:
            email_label.text = self.user_data['email']
        if bio_label:
            bio_label.text = self.user_data['bio'] if self.user_data['bio'] else "You didn't provide a bio..."
        
        self.update_stats()
    
    def update_stats(self):
        """Update the stats cards with current numbers"""
        stats_data = [
            ('posts_stat', 2),
            ('followers_stat', 0),
            ('following_stat', 0)
        ]
        
        for stat_id, value in stats_data:
            stat_label = self.ids.get(stat_id)
            if stat_label:
                stat_label.text = f"[b]{value}[/b]"
    
    def format_number(self, num):
        """Format large numbers (e.g., 2500 -> 2.5K)"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)
    
    def go_back(self):
        """Navigate back to main screen"""
        try:
            self.manager.current = "main"
            self.manager.transition.direction = "right"
        except Exception as e:
            self.show_snackbar("Navigation error")
    
    def open_settings(self):
        """Navigate to settings screen"""
        try:
            self.manager.current = "settings"
            self.manager.transition.direction = "left"
        except Exception as e:
            self.show_snackbar("Settings not available")
    
    def edit_profile(self):
        """Open edit profile dialog or screen"""
        if not self.dialog:
            self.dialog = MDDialog(
                title="Edit Profile",
                text="Edit profile functionality coming soon!",
                buttons=[
                    MDButton(
                        MDButtonText(text="OK"),
                        on_release=self.close_dialog
                    )
                ]
            )
        self.dialog.open()
    
    def share_profile(self):
        """Share profile functionality"""
        self.show_snackbar("Share profile: mystreet.com/profile/johndoe")
    
    def view_posts(self):
        """Navigate to user's posts"""
        try:
            self.manager.current = "my_posts"
            self.manager.transition.direction = "left"
        except Exception as e:
            self.show_snackbar("Posts view not implemented yet")
    
    def view_saved_items(self):
        """Navigate to saved items"""
        try:
            self.manager.current = "saved_items"
            self.manager.transition.direction = "left"
        except Exception as e:
            self.show_snackbar("Saved items not implemented yet")
    
    def view_activity(self):
        """Navigate to activity/analytics"""
        try:
            self.manager.current = "activity"
            self.manager.transition.direction = "left"
        except Exception as e:
            self.show_snackbar("Activity view not implemented yet")
    
    def close_dialog(self, *args):
        """Close any open dialogs"""
        if self.dialog:
            self.dialog.dismiss()
    
    def refresh_profile(self):
        """Pull to refresh functionality"""
        self.show_snackbar("Refreshing profile...")
        Clock.schedule_once(self.finish_refresh, 1.5)
    
    def finish_refresh(self, dt):
        """Complete the refresh process"""
        self.load_profile_data()
        self.show_snackbar("Profile updated!")
    
    def update_profile_picture(self):
        """Handle profile picture update"""
        self.show_snackbar("Profile picture update coming soon!")
    
    def logout(self):
        """Handle user logout"""
        if not self.dialog:
            self.dialog = MDDialog(
                title="Logout",
                text="Are you sure you want to logout?",
                buttons=[
                    MDButton(
                        MDButtonText(text="Cancel"),
                        on_release=self.close_dialog
                    ),
                    MDButton(
                        MDButtonText(text="Logout"),
                        on_release=self.confirm_logout
                    )
                ]
            )
        self.dialog.open()
    
    def confirm_logout(self, *args):
        """Confirm logout and navigate to login"""
        self.close_dialog()
        try:
            self.manager.current = "login"
            self.manager.transition.direction = "right"
            self.show_snackbar("Logged out successfully")
        except Exception as e:
            self.show_snackbar("Logout error")


class UserProfileManager(EventDispatcher):
    def __init__(self):
        super().__init__()
        self.current_user = None
    
    def load_user_profile(self, user_id):
        """Load user profile from database/API"""
        pass
    
    def update_user_profile(self, profile_data):
        """Update user profile data"""
        pass
    
    def upload_profile_picture(self, image_path):
        """Upload new profile picture"""
        pass