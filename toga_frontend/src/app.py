import toga
from backend_api import login_api, signup_api
from session import get_token
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW


class MyBeeWareApp(toga.App):
    def startup(self):
        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 350))
        # Check if a session exists
        token = get_token()
        if token:
            # If it does, go to home page
            self.show_home_page()
        else:
            # if not, go to login page
            self.show_login_page()
        self.main_window.show()

    def show_login_page(self, widget=None):
        # login page layout
        login_box = toga.Box(
            style=Pack(direction=COLUMN, margin=20, align_items=CENTER)
        )
        title = toga.Label(
            "Login", style=Pack(font_size=24, margin_bottom=20, width=350)
        )
        login_box.add(title)

        self.login_email_input = toga.TextInput(
            placeholder="Enter your email",
            style=Pack(width=300, margin_bottom=10),
        )
        login_box.add(self.login_email_input)

        self.login_password_input = toga.PasswordInput(
            placeholder="Enter your password",
            style=Pack(width=300, margin_bottom=10),
        )
        login_box.add(self.login_password_input)

        self.login_status_label = toga.Label(
            "", style=Pack(font_size=14, color="grey", margin_bottom=20)
        )
        login_box.add(self.login_status_label)

        login_button = toga.Button(
            "Login",
            on_press=self.on_login,
            style=Pack(
                margin=10,
                font_size=16,
                background_color="#4CAF50",
                color="white",
                width=200,
            ),
        )
        login_box.add(login_button)

        switch_to_signup = toga.Button(
            "Don't have an account? Sign up",
            on_press=self.show_signup_page,
            style=Pack(margin=10, font_size=12, width=350),
        )
        login_box.add(switch_to_signup)

        self.main_window.content = login_box

    def show_signup_page(self, widget=None):
        # signup page layout
        signup_box = toga.Box(
            style=Pack(direction=COLUMN, margin=20, align_items=CENTER)
        )
        title = toga.Label(
            "Sign Up", style=Pack(font_size=24, margin_bottom=20, width=350)
        )
        signup_box.add(title)

        self.signup_email_input = toga.TextInput(
            placeholder="Enter your email",
            style=Pack(
                width=300,
                margin_bottom=10,
            ),
        )
        signup_box.add(self.signup_email_input)

        self.signup_password_input = toga.PasswordInput(
            placeholder="Enter your password",
            style=Pack(width=300, margin_bottom=10),
        )
        signup_box.add(self.signup_password_input)

        self.signup_status_label = toga.Label(
            "", style=Pack(font_size=14, color="grey", margin_bottom=20)
        )
        signup_box.add(self.signup_status_label)

        signup_button = toga.Button(
            "Sign Up",
            on_press=self.on_signup,
            style=Pack(
                margin=10,
                font_size=16,
                background_color="#4CAF50",
                color="white",
                width=200,
            ),
        )
        signup_box.add(signup_button)

        switch_to_login = toga.Button(
            "Already have an account? Login",
            on_press=self.show_login_page,
            style=Pack(margin=10, font_size=12, width=350),
        )
        signup_box.add(switch_to_login)

        self.main_window.content = signup_box

    def on_login(self, widget):
        email = self.login_email_input.value
        password = self.login_password_input.value

        # Call the backend API for login
        response = login_api(email, password)
        if response.get("status") == "success":
            self.login_status_label.text = "Login successful!"
            self.login_status_label.style.color = "green"
            self.show_home_page()
        else:
            self.login_status_label.text = response.get("message", "Login failed.")
            self.login_status_label.style.color = "red"

    def on_signup(self, widget):
        email = self.signup_email_input.value
        password = self.signup_password_input.value

        # Call the backend API for signup
        response = signup_api(email, password)
        if response.get("status") == "success":
            self.signup_status_label.text = "Signup successful! You can now log in."
            self.signup_status_label.style.color = "green"
            # After a successful signup, switch to the login page
            self.show_login_page()
        else:
            self.signup_status_label.text = response.get("message", "Signup failed.")
            self.signup_status_label.style.color = "red"

    def show_home_page(self, widget=None):
        # Build a simple home page layout
        home_box = toga.Box(style=Pack(direction=COLUMN, margin=20, align_items=CENTER))
        title = toga.Label(
            "Home Page", style=Pack(font_size=24, margin_bottom=20, width=350)
        )
        home_box.add(title)

        logout_button = toga.Button(
            "Log Out",
            on_press=self.show_login_page,
            style=Pack(
                margin=10,
                font_size=16,
                background_color="#f44336",
                color="white",
                width=200,
            ),
        )
        home_box.add(logout_button)
        self.main_window.content = home_box


def main():
    return MyBeeWareApp("MyStreet", "com.example.mystreet", icon="icon.png")


if __name__ == "__main__":
    main().main_loop()
if __name__ == "__main__":
    main().main_loop()
