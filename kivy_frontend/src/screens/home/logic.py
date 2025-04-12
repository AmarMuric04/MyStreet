import json
import threading

import requests
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen

from utils.session import get_token

# Load the KV file for groups
Builder.load_file("kivy_frontend/src/screens/home/design.kv")

API_GROUPS_URL = "http://localhost:5000/groups"  # Make sure your backend endpoint is correct

class HomeScreen(MDScreen):
    # This property is bound to the RecycleView's data property.
    groups_data = ListProperty([])

    def on_enter(self):
        # When the screen enters, fetch the groups dynamically.
        self.fetch_groups()

    def fetch_groups(self):
        # Execute the network request in a background thread.
        threading.Thread(target=self.fetch_groups_thread, daemon=True).start()

    def fetch_groups_thread(self):
        try:
            response = requests.get(
                API_GROUPS_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                }
            )
            if response.status_code == 200:
                groups = response.json()
                # Convert the fetched list of groups to the format expected by the RecycleView.
                # Adjust the key names if your backend returns different names.
                data = [
                    {
                        "group_name": group.get("name", "No Name"),
                        "description": group.get("description", "No Description"),
                        "creator": group.get("creator", "Unknown Creator")
                    }
                    for group in groups
                ]
            else:
                print(f"Error fetching groups: {response.status_code}")
                data = []
        except Exception as e:
            print(f"Error fetching groups: {str(e)}")
            data = []

        # Update the groups_data property on the main thread.
        Clock.schedule_once(lambda dt: self.update_groups_data(data), 0)

    def update_groups_data(self, data):
        self.groups_data = data
