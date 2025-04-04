import requests
import toga
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW


class MyBeeWareApp(toga.App):
    def startup(self):
        # Main box to hold widgets
        main_box = toga.Box(style=Pack(direction=COLUMN, margin=20, align_items=CENTER))

        # Title label
        title_label = toga.Label(
            "MyStreet",
            style=Pack(font_size=20, font_weight="bold", margin_bottom=4),
        )
        main_box.add(title_label)

        subtitle_label = toga.Label(
            "MyStreet is a social media application designed for neighbors to communicate,\n"
            "share updates, and stay connected. The app will feature a feed similar to Instagram, "
            "where users can log in, post updates, interact with posts, like, and comment.",
            style=Pack(font_size=12, color="gray", margin_bottom=20),
        )
        main_box.add(subtitle_label)

        # Email input field
        self.email_input = toga.TextInput(
            placeholder="Enter your email", style=Pack(width=300, margin_bottom=10)
        )
        main_box.add(self.email_input)

        # Password input field
        self.password_input = toga.TextInput(
            placeholder="Enter your password", style=Pack(width=300, margin_bottom=10)
        )
        main_box.add(self.password_input)

        # Status label
        self.status_label = toga.Label(
            "Press the button to send data!",
            style=Pack(font_size=14, color="grey", margin_bottom=20),
        )
        main_box.add(self.status_label)

        # Button box
        button_box = toga.Box(
            style=Pack(direction=ROW, align_items=CENTER, margin_top=10)
        )

        # Send Data Button
        send_button = toga.Button(
            "Send Data",
            on_press=self.send_data,
            style=Pack(
                margin=10,
                font_size=16,
                background_color="#4CAF50",
                color="white",
                width=200,
            ),
        )
        button_box.add(send_button)

        main_box.add(button_box)

        # Setup main window
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 300))
        self.main_window.content = main_box
        self.main_window.show()

    def send_data(self, widget):
        url = "http://localhost:5000/add"
        payload = {
            "email": self.email_input.value.strip(),
            "password": self.password_input.value.strip(),
        }

        if not payload["email"] or not payload["password"]:
            self.status_label.text = "⚠️ Please enter both email and password!"
            self.status_label.style.color = "red"
            return

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 201:
                self.status_label.text = "✅ Data sent successfully!"
                self.status_label.style.color = "green"
            else:
                self.status_label.text = f"❌ Error: {response.status_code}"
                self.status_label.style.color = "red"
        except Exception as e:
            self.status_label.text = f"⚠️ Request failed: {e}"
            self.status_label.style.color = "red"


def main():
    return MyBeeWareApp("BeeWare-Flask-Mongo App", "org.example.bfwma")


if __name__ == "__main__":
    main().main_loop()
