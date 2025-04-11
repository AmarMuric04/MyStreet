from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp

from screens.create_post.logic import CreatePost
from screens.email_code.logic import EmailCode
from screens.forgot_password.logic import ForgotPassword
from screens.home.logic import HomeScreen
from screens.login.logic import LoginScreen
from screens.posts.logic import PostsScreen
from screens.signup.logic import SignupScreen
from utils.session import get_token

Window.size = (450, 750)

class MyStreetApp(MDApp):
    def build(self):
        self.sm = ScreenManager(transition=SlideTransition())
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.load_initial_screen()
        return self.sm

    def load_initial_screen(self):
        if get_token():
            self.load_screen('home')
            self.sm.current = 'home'
        else:
            self.load_screen('login')
            self.sm.current = 'login'

    def load_screen(self, screen_name):
        if not self.sm.has_screen(screen_name):
            screen = None
            if screen_name == 'login':
                screen = LoginScreen(name='login')
            elif screen_name == 'signup':
                screen = SignupScreen(name='signup')
            elif screen_name == 'home':
                screen = HomeScreen(name='home')
            elif screen_name == 'posts':
                screen = PostsScreen(name='posts')
            elif screen_name == 'forgot_password':
                screen = ForgotPassword(name='forgot_password')
            elif screen_name == 'create_post':
                screen = CreatePost(name='create_post')
            elif screen_name == 'email_code':
                screen = EmailCode(name='email_code')

            if screen:
                self.sm.add_widget(screen)

    def switch_screen(self, screen_name):
        self.load_screen(screen_name)
        self.sm.current = screen_name
        
if __name__ == "__main__":
    MyStreetApp().run()
