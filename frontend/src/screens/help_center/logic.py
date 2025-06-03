from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.logger import Logger
from kivymd.uix.screen import MDScreen

try:
    Builder.load_file("frontend/src/screens/help_center/design.kv")
except FileNotFoundError:
    Logger.error("HelpCenterScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"HelpCenterScreen: Error loading design file: {e}")


class HelpCenterScreen(MDScreen):
  pass