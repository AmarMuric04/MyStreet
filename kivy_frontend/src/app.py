from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp

from utils.session import clear_token, get_token

Window.size = (450, 750)

class MyStreetApp(MDApp):
    def build(self):
        # clear_token()
        self.root = Builder.load_file("kivy_frontend/src/app.kv")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        return self.root

    def on_start(self):
        screen_manager = self.root.ids.screen_manager
        screen_manager.current = "home" if get_token() else "login"

if __name__ == "__main__":
    MyStreetApp().run()
