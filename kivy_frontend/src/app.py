from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.snackbar import (
    MDSnackbar,
    MDSnackbarActionButton,
    MDSnackbarActionButtonText,
    MDSnackbarButtonContainer,
    MDSnackbarCloseButton,
    MDSnackbarSupportingText,
    MDSnackbarText,
)

from screens.create_group.logic import CreateGroup
from screens.create_post.logic import CreatePost
from screens.email_code.logic import EmailCode
from screens.forgot_password.logic import ForgotPassword
from screens.home.logic import HomeScreen
from screens.login.logic import LoginScreen
from screens.posts.logic import PostsScreen
from screens.signup.logic import SignupScreen
from utils.session import clear_token, get_token

Window.size = (450, 750)

class MyStreetApp(MDApp):
    def build(self):
        # clear_token()  # Uncomment if needed
        self.sm = ScreenManager(transition=SlideTransition())
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.sm.add_widget(PostsScreen(name="posts"))
        self.sm.add_widget(CreatePost(name="create_post"))
        self.load_initial_screen()

        MDSnackbar(
    MDSnackbarText(
        text="Single-line snackbar with action",
    ),
    MDSnackbarSupportingText(
        text="and close buttons at the bottom",
        padding=[0, 0, 0, dp(56)],
    ),
    MDSnackbarButtonContainer(
        Widget(),
        MDSnackbarActionButton(
            MDSnackbarActionButtonText(
                text="Action button"
            ),
        ),
        MDSnackbarCloseButton(
            icon="close",
        ),
    ),
    y=dp(124),
    pos_hint={"center_x": 0.5},
    size_hint_x=0.5,
    padding=[0, 0, "8dp", "8dp"],
).open()
        
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
            elif screen_name == 'create_group':
                screen = CreateGroup(name='create_group')

            if screen:
                self.sm.add_widget(screen)

    def switch_screen(self, screen_name):
        self.load_screen(screen_name)
        self.sm.current = screen_name
        
if __name__ == "__main__":
    MyStreetApp().run()
