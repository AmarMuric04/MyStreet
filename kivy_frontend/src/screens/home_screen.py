from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from session import clear_token


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Home Page", font_size=24, color="black"))
        
        logout_button = Button(text="Log Out", size_hint=(1, None), height=40)
        logout_button.bind(on_press=self.on_logout)
        layout.add_widget(logout_button)
        
        switch_to_posts = Button(text="View Posts", size_hint=(1, None), height=40)
        switch_to_posts.bind(on_press=self.go_to_posts)
        
        layout.add_widget(switch_to_posts)
        
        self.add_widget(layout)

    def on_logout(self, instance):
        clear_token()
        self.manager.current = "login"
    def go_to_posts(self, instance):
        self.manager.current = "posts"