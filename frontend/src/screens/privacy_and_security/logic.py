from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen

try:
    Builder.load_file("frontend/src/screens/privacy_and_security/design.kv")
except FileNotFoundError:
    Logger.error("PrivacySecurityScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"PrivacySecurityScreen: Error loading design file: {e}")


class PrivacySecurityScreen(MDScreen):
    pass

