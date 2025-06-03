from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawerDivider,
    MDNavigationDrawerItem,
    MDNavigationDrawerItemLeadingIcon,
    MDNavigationDrawerItemText,
)
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from utils.auth import get_logged_in_user
from utils.session import clear_token, get_token

Window.size = (450, 750)

class MyStreetApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = None
    
    def show_snackbar(self, message):
        """Cross-platform message display"""
        snackbar = MDSnackbar(
            MDSnackbarText(text=message),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        )
        snackbar.open()
        
    def build(self):
        self.root = Builder.load_file("frontend/src/app.kv")
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"
        return self.root

    def update_navigation_drawer(self):
        self.user_data = get_logged_in_user()
        
        nav_drawer = self.root.ids.nav_drawer_menu
        profile_item = self.root.ids.profile_item
        user_divider = self.root.ids.user_divider
        login_item = self.root.ids.login_item
        signup_item = self.root.ids.signup_item
        logout_item = self.root.ids.logout_item
        username_text = self.root.ids.username_text
        
        if self.user_data:
            username = self.user_data.get("username", "User")
            username_text.text = username
            
            profile_item.opacity = 1
            profile_item.disabled = False
            profile_item.size_hint_y = None
            profile_item.height = dp(56)  
            
            user_divider.opacity = 1
            user_divider.size_hint_y = None
            user_divider.height = dp(1)
            
            logout_item.opacity = 1
            logout_item.disabled = False
            logout_item.size_hint_y = None
            logout_item.height = dp(56)
            
            login_item.opacity = 0
            login_item.disabled = True
            login_item.size_hint_y = None
            login_item.height = 0
            
            signup_item.opacity = 0
            signup_item.disabled = True
            signup_item.size_hint_y = None
            signup_item.height = 0
            
        else:
            profile_item.opacity = 0
            profile_item.disabled = True
            profile_item.size_hint_y = None
            profile_item.height = 0
            
            user_divider.opacity = 0
            user_divider.size_hint_y = None
            user_divider.height = 0
            
            logout_item.opacity = 0
            logout_item.disabled = True
            logout_item.size_hint_y = None
            logout_item.height = 0
            
            login_item.opacity = 1
            login_item.disabled = False
            login_item.size_hint_y = None
            login_item.height = dp(56)
            
            signup_item.opacity = 1
            signup_item.disabled = False
            signup_item.size_hint_y = None
            signup_item.height = dp(56)  
           
    def goto_screen(self, screen_name):
        self.root.ids.screen_manager.current = screen_name
        self.root.ids.nav_drawer.set_state("close")
    
    def on_start(self):
        self.update_navigation_drawer()
    
    def logout(self):
        clear_token()
        self.goto_screen("login")
        self.update_navigation_drawer()
        self.show_snackbar("Logged out successfully!")

if __name__ == "__main__":
    MyStreetApp().run()