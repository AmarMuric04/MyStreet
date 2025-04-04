import requests
import toga
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW


class MyBeeWareApp(toga.App):
    def startup(self):
        # Main box to hold widgets
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))

        # Title label with styling
        title_label = toga.Label(
            "BeeWare & Flask Demo",
            style=Pack(font_size=20, font_weight="bold", padding_bottom=20),
        )
        main_box.add(title_label)

        # Status label
        self.status_label = toga.Label(
            "Press the button to send data!",
            style=Pack(font_size=14, color="grey", padding_bottom=20),
        )
        main_box.add(self.status_label)

        # Button box (helps with layout)
        button_box = toga.Box(
            style=Pack(direction=ROW, alignment=CENTER, padding_top=10)
        )

        # Send Data Button with styling
        send_button = toga.Button(
            "Send Data",
            on_press=self.send_data,
            style=Pack(
                padding=10,
                font_size=16,
                background_color="#4CAF50",
                color="white",
                width=200,
            ),
        )
        button_box.add(send_button)

        main_box.add(button_box)

        # Setup main window
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 250))
        self.main_window.content = main_box
        self.main_window.show()

    def send_data(self, widget):
        url = "http://localhost:5000/add"
        payload = {"message": "Hello from BeeWare!"}

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
