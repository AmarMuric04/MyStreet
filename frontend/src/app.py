from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawerDivider,
    MDNavigationDrawerItem,
    MDNavigationDrawerItemLeadingIcon,
    MDNavigationDrawerItemText,
)

from utils.auth import get_logged_in_user
from utils.session import clear_token, get_token

Window.size = (450, 750)

class MyStreetApp(MDApp):
    def build(self):
        # clear_token()
        self.root = Builder.load_file("frontend/src/app.kv")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.user_data = None
        return self.root

    def update_navigation_drawer(self):
        self.user_data = get_logged_in_user()
        menu = self.root.ids.nav_drawer_menu

        menu.add_widget(MDLabel(text="MyStreet", theme_text_color="Primary", size_hint_y=None, height=dp(40)))

        if self.user_data:
            username = self.user_data.get("username", "User")

            menu.add_widget(
                MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(
                        icon="account",
                        size_hint_y=None,
                        height=dp(40),
                    ),
                    MDNavigationDrawerItemText(
                        text=username,
                        size_hint_y=None,
                        height=dp(40),
                        valign="center",
                    ),
                    on_release=lambda: print("Profile clicked")
                )
            )

            menu.add_widget(MDNavigationDrawerDivider())

        menu.add_widget(
            MDNavigationDrawerItem(
                MDNavigationDrawerItemLeadingIcon(
                    icon="home",
                    size_hint_y=None,
                    height=dp(40),
                ),
                MDNavigationDrawerItemText(
                    text="Home",
                    size_hint_y=None,
                    height=dp(40),
                    valign="center",
                ),
                on_release=lambda x: self.goto_screen("home")
            )
        )

        if not self.user_data:
            menu.add_widget(
                MDNavigationDrawerItem(
                   MDNavigationDrawerItemLeadingIcon(
                        icon="login",
                        size_hint_y=None,
                        height=dp(40),
                    ),
                    MDNavigationDrawerItemText(
                        text="Log in",
                        size_hint_y=None,
                        height=dp(40),
                        valign="center",
                    ),
                    on_release=lambda x: self.goto_screen("login")
                )
            )
            menu.add_widget(
                MDNavigationDrawerItem(
                   MDNavigationDrawerItemLeadingIcon(
                        icon="account-plus",
                        size_hint_y=None,
                        height=dp(40),
                    ),
                    MDNavigationDrawerItemText(
                        text="Sign up",
                        size_hint_y=None,
                        height=dp(40),
                        valign="center",
                    ),
                    on_release=lambda x: self.goto_screen("signup")
                )
            )
            
        if self.user_data:
                menu.add_widget(
                    MDNavigationDrawerItem(
                        MDNavigationDrawerItemLeadingIcon(
                            icon="logout",
                            size_hint_y=None,
                            height=dp(40),
                        ),
                        MDNavigationDrawerItemText(
                            text="Log out",
                            size_hint_y=None,
                            height=dp(40),
                            valign="center",
                        ),
                        on_release=lambda _: self.logout()
                    )
                )

    def goto_screen(self, screen_name):
        self.root.ids.screen_manager.current = screen_name
        self.root.ids.nav_drawer.set_state("close")
    
    def on_start(self):
        self.update_navigation_drawer()
    
    def logout(self):
        clear_token()
        self.goto_screen("home")
        self.update_navigation_drawer()

if __name__ == "__main__":
    MyStreetApp().run()
