import platform
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivymd.uix.screen import MDScreen

try:
    if platform.system() == 'Android':
        from kivymd.toast import toast
    else:
        from kivymd.uix.snackbar import Snackbar
        def toast(message):
            try:
                snackbar = Snackbar(
                    text=message,
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(1.0 - 20/400) 
                )
                snackbar.open()
            except Exception as e:
                print(f"Notification: {message}")
                Logger.info(f"LoginScreen: {message}")
except ImportError:
    def toast(message):
        print(f"Notification: {message}")
        Logger.info(f"LoginScreen: {message}")

from utils.auth import login_api

try:
    Builder.load_file("frontend/src/screens/login/design.kv")
except FileNotFoundError:
    Logger.error("LoginScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"LoginScreen: Error loading design file: {e}")

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login_in_progress = False
    
    def login_helper(self):
        """Handle login button press with validation"""
        if self.login_in_progress:
            return
            
        self.clear_errors()
        
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()
        
        if not self.validate_inputs(email, password):
            return
            
        self.set_loading_state(True)
        self.login_in_progress = True
        
        threading.Thread(target=self.perform_login, args=(email, password), daemon=True).start()
    
    def get_button_widget(self):
        """Helper to find the actual button widget"""
        try:
            for widget in self.walk():
                if (hasattr(widget, 'style') and widget.style == "elevated" and 
                    hasattr(widget, 'on_press')):
                    return widget
        except Exception as e:
            Logger.error(f"LoginScreen: Error finding button widget: {e}")
        return None
    
    def validate_inputs(self, email, password):
        """Validate email and password inputs"""
        valid = True
        
        if not email:
            self.set_input_error('email_input', "Email is required")
            valid = False
        elif '@' not in email or '.' not in email.split('@')[-1]:
            self.set_input_error('email_input', "Please enter a valid email")
            valid = False
            
        if not password:
            self.set_input_error('password_input', "Password is required")
            valid = False
        elif len(password) < 6:
            self.set_input_error('password_input', "Password must be at least 6 characters")
            valid = False
            
        return valid
    
    def set_input_error(self, input_id, message):
        """Set error state for input field"""
        try:
            input_field = self.ids[input_id]
            if hasattr(input_field, 'error'):
                input_field.error = True
            if hasattr(input_field, 'helper_text'):
                input_field.helper_text = message
                input_field.helper_text_mode = "on_error"
            else:
                toast(f"{input_id.replace('_', ' ').title()}: {message}")
        except KeyError:
            Logger.error(f"LoginScreen: Input field '{input_id}' not found")
    
    def clear_errors(self):
        """Clear error states from input fields"""
        try:
            email_field = self.ids.email_input
            if hasattr(email_field, 'error'):
                email_field.error = False
            if hasattr(email_field, 'helper_text'):
                email_field.helper_text = ""
            
            password_field = self.ids.password_input
            if hasattr(password_field, 'error'):
                password_field.error = False
            if hasattr(password_field, 'helper_text'):
                password_field.helper_text = ""
                
        except (KeyError, AttributeError) as e:
            Logger.error(f"LoginScreen: Error clearing input fields: {e}")
    
    def perform_login(self, email, password):
        """Perform login API call in background thread"""
        try:
            response = login_api(email, password)
            Clock.schedule_once(lambda dt: self.handle_login_response(response, email, password), 0)
        except Exception as e:
            Logger.error(f"LoginScreen: Login API error: {e}")
            Clock.schedule_once(lambda dt: self.handle_login_error(str(e)), 0)
    
    def handle_login_response(self, response, email, password):
        """Handle login API response on main thread"""
        self.login_in_progress = False
        self.set_loading_state(False)
        
        if response and response.get("status") == "success":
            self.on_login_success(response)
        else:
            error_message = response.get("message", "Invalid credentials") if response else "Login failed"
            self.on_login_failure(error_message)
    
    def handle_login_error(self, error_message):
        """Handle login API errors on main thread"""
        self.login_in_progress = False
        self.set_loading_state(False)
        self.on_login_failure(f"Connection error: {error_message}")
    
    def on_login_success(self, response):
        """Handle successful login"""
        try:
            self.ids.email_input.text = ""
            self.ids.password_input.text = ""
            self.clear_errors()
            
            app = App.get_running_app()
            app.show_snackbar("Login successful!")
            
            app = App.get_running_app()
            if app and hasattr(app, 'update_navigation_drawer'):
                app.update_navigation_drawer()
            
            if app and hasattr(app, 'root') and hasattr(app.root, 'ids'):
                screen_manager = app.root.ids.get('screen_manager')
                if screen_manager:
                    screen_manager.current = 'home'
                    if hasattr(screen_manager, 'transition'):
                        screen_manager.transition.direction = 'left'
                else:
                    Logger.error("LoginScreen: Screen manager not found")
            else:
                Logger.error("LoginScreen: App root or screen manager not accessible")
                
        except Exception as e:
            Logger.error(f"LoginScreen: Error handling login success: {e}")
    
    def on_login_failure(self, error_message):
        """Handle login failure"""
        try:
            self.set_input_error('email_input', error_message)
            self.set_input_error('password_input', error_message)
            
            toast(error_message)
            
        except Exception as e:
            Logger.error(f"LoginScreen: Error handling login failure: {e}")
    
    def set_loading_state(self, loading):
        """Set loading state for login button"""
        try:
            button_text = self.ids.login_button
            if hasattr(button_text, 'text'):
                if loading:
                    button_text.text = "Checking..."
                else:
                    button_text.text = "Log In"
            
            if hasattr(button_text, 'parent'):
                button = button_text.parent
                    
        except (KeyError, AttributeError) as e:
            Logger.error(f"LoginScreen: Error setting button state: {e}")
            try:
                for widget in self.walk():
                    if hasattr(widget, 'style') and widget.style == "elevated":
                        widget.disabled = loading
                        break
            except Exception as e2:
                Logger.error(f"LoginScreen: Fallback button search failed: {e2}")
    
    def on_enter(self):
        """Called when screen is entered"""
        super().on_enter()
        self.clear_errors()
        self.set_loading_state(False)
        self.login_in_progress = False
    
    def on_leave(self):
        """Called when screen is left"""
        super().on_leave()
        self.login_in_progress = False
        self.set_loading_state(False)