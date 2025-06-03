from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen

try:
    Builder.load_file("frontend/src/screens/delete_account/design.kv")
except FileNotFoundError:
    Logger.error("DeleteAccountScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"DeleteAccountScreen: Error loading design file: {e}")


class DeleteAccountScreen(MDScreen):
    def delete(self):
        app = App.get_running_app()
        if self.ids.confirmation_field.text != "DELETE":
            app.show_snackbar("Enter correct confirmation text.")
            return
        
        app.logout()
        app.show_snackbar("Account deleted successfully!")