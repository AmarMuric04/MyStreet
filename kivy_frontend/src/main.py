from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from screens.home_screen import HomeScreen
from screens.login_screen import LoginScreen
from screens.signup_screen import SignupScreen
from session import get_token


class MyStreetApp(MDApp):
    def build(self):
        self.sm = ScreenManager()
        
        # Create and add the screens
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(SignupScreen(name="signup"))
        self.sm.add_widget(HomeScreen(name="home"))
        
        # Start with the home screen if a token exists, otherwise login
        if get_token():
            self.sm.current = "home"
        else:
            self.sm.current = "login"
        
        return self.sm

if __name__ == "__main__":
    MyStreetApp().run()

