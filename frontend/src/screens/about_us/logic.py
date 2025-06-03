from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen

try:
    Builder.load_file("frontend/src/screens/about_us/design.kv")
except FileNotFoundError:
    Logger.error("AboutUsScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"AboutUsScreen: Error loading design file: {e}")


class AboutUsScreen(MDScreen):
    pass