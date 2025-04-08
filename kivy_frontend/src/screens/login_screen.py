from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from backend_api import login_api
from session import save_token


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        
        # Use AnchorLayout to center the content
        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        
        # Create a BoxLayout with fixed width (400dp) for the login content
        content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_x=None,
            width=dp(400)
        )
        
        content_layout.add_widget(MDLabel(
            text="[i]MyStreet[/i]", 
            halign="left",
            theme_text_color="Primary",
            font_style="Body1", 
            markup=True 
        ))
        
        title_layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=5,
            size_hint_x=None,
            width=dp(400)
        )
        
        title_layout.add_widget(MDLabel(
            text="[b]Welcome back![/b]", 
            halign="left",
            theme_text_color="Primary",
            font_style="H3", 
            markup=True 
        ))
        
        title_layout.add_widget(MDLabel(
            text="Enter your email & password to continue",  
            halign="left",
            padding=4,
            theme_text_color="Hint",  
            font_style="Body1",
            markup=True  
        ))
        
        content_layout.add_widget(title_layout)
        
        self.email_input = MDTextField(
            hint_text="Enter your email",
            size_hint_x=1,
            mode="rectangle"
        )
        content_layout.add_widget(self.email_input)
        
        self.password_input = MDTextField(
            hint_text="Enter your password",
            password=True,
            size_hint_x=1,
            mode="rectangle",
        )
        content_layout.add_widget(self.password_input)
        
        login_layout = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_x=None,
            width=dp(400)
        )

        self.login_button = MDRaisedButton(
            text="Log In",
            size_hint=(1, None),
            height=dp(100),
            halign="center",
            md_bg_color=[1, 1, 1, 1],
            text_color=(0, 0, 0, 1),
        )

        self.login_button.bind(on_press=self.login_helper)
        login_layout.add_widget(self.login_button)
        
        # Create an MDLabel with clickable 'Sign up' text using markup.
        switch_to_signup = MDLabel(
            text="Don't have an account? [ref=signup][u][b]Sign up[/b][/u][/ref]",
            markup=True,
            halign="center",
            theme_text_color="Primary"
        )
        switch_to_signup.bind(on_ref_press=self.go_to_signup)
        login_layout.add_widget(switch_to_signup)
        
        content_layout.add_widget(login_layout)
        
        # Add the content layout to the anchor layout, centering it on the screen.
        anchor_layout.add_widget(content_layout)
        self.add_widget(anchor_layout)

    def login_helper(self, instance):
        # Set the button text to "Checking..." and schedule the actual login
        self.login_button.text = "Checking..."
        # Schedule on_login to run after a small delay, so the UI can update
        Clock.schedule_once(lambda dt: self.on_login(instance), 0.1)

    def on_login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        response = login_api(email, password)
        if response.get("status") == "success":
            self.email_input.text = ""
            self.password_input.text = ""
            save_token(response.get("token"))
            self.manager.current = "home"
            self.login_button.text = "Log In"
        else:
            # Reset the button text after showing the error
            self.login_button.text = "Log In"
            self.email_input.error = True
            self.email_input.helper_text = "Invalid credentials"
            self.email_input.helper_text_mode = "on_error"
            self.password_input.error = True
            self.password_input.helper_text = "Invalid credentials"
            self.password_input.helper_text_mode = "on_error"

    def go_to_signup(self, instance, value):
        self.manager.current = "signup"
