from kivy.lang import Builder
from kivy.logger import Logger
from kivymd.uix.screen import MDScreen

try:
    Builder.load_file("frontend/src/screens/themes/design.kv")
except FileNotFoundError:
    Logger.error("ThemesScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"ThemesScreen: Error loading design file: {e}")

class ThemesScreen(MDScreen):
    pass