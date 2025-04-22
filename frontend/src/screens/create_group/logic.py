import json
import threading

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from utils.session import get_token

Builder.load_file("frontend/src/screens/create_group/design.kv")

API_URL = "http://localhost:5000/groups"  

class CreateGroup(MDScreen):
    def create_group(self):
        # Retrieve group name and description inputs from the UI.
        name = self.ids.name_input.text.strip()
        description = self.ids.description_input.text.strip()
        print("Creating group:", name, description)
        
        if not name:
            print("Error: Group name is required.")
            return
        
        # Update button state to reflect processing.
        self.ids.group_button.text = "Submitting Group..."
        self.ids.group_button.disabled = True
        allow_preview = self.ids.allow_preview_checkbox.active
        
        group_data = {
            "name": name,
            "description": description,
            "allow_preview": allow_preview
        }
        
        # Start a thread for the network request (daemon thread to not block app exit).
        threading.Thread(target=self.create_group_thread, args=(group_data,), daemon=True).start()

    def create_group_thread(self, group_data):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                },
                data=json.dumps(group_data)
            )
            if response.status_code == 201:
                msg = "Group created successfully!"
                # Clear input fields on success.
                Clock.schedule_once(lambda dt: self.clear_inputs(), 0)
                app = App.get_running_app()
                Clock.schedule_once(lambda dt: setattr(app.root.ids.screen_manager, "current", "home"), 0)
            else:
                msg = f"Error creating group: {response.status_code}"
        except Exception as e:
            msg = f"Error: {str(e)}"

        # Update the UI to reflect status.
        Clock.schedule_once(lambda dt: self.update_group_status(msg), 0)

    def update_group_status(self, msg):
        print(msg)
        self.ids.group_button.text = "Create Group"
        self.ids.group_button.disabled = False

    def clear_inputs(self):
        self.ids.name_input.text = ""
        self.ids.description_input.text = ""
