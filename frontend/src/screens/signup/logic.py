import platform
import re
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

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
                Logger.info(f"SignupScreen: {message}")
except ImportError:
    def toast(message):
        print(f"Notification: {message}")
        Logger.info(f"SignupScreen: {message}")

from utils.auth import send_code_api

try:
    Builder.load_file("frontend/src/screens/signup/design.kv")
except FileNotFoundError:
    Logger.error("SignupScreen: Could not load design.kv file")
except Exception as e:
    Logger.error(f"SignupScreen: Error loading design file: {e}")

class SignupScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signup_in_progress = False
        
    def show_snackbar(self, message):
        """Cross-platform message display"""
        snackbar = MDSnackbar(
            MDSnackbarText(text=message),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        )
        snackbar.open()
        
    def signup_helper(self):
        """Handle signup button press with validation"""
        if self.signup_in_progress:
            return
            
        self.clear_errors()
        
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()
        username = self.ids.username_input.text.strip()
        
        if not self.validate_inputs(email, password, username):
            return
            
        self.set_loading_state(True)
        self.signup_in_progress = True
        
        threading.Thread(target=self.perform_signup, args=(email, password, username), daemon=True).start()
    
    def validate_inputs(self, email, password, username):
        """Validate all input fields"""
        valid = True
        
        if not email:
            self.set_input_error('email_input', "Email is required")
            valid = False
        elif not self.is_valid_email(email):
            self.set_input_error('email_input', "Please enter a valid email address")
            valid = False
            
        if not username:
            self.set_input_error('username_input', "Username is required")
            valid = False
        elif len(username) < 3:
            self.set_input_error('username_input', "Username must be at least 3 characters")
            valid = False
        elif len(username) > 20:
            self.set_input_error('username_input', "Username must be less than 20 characters")
            valid = False
        elif not self.is_valid_username(username):
            self.set_input_error('username_input', "Username can only contain letters, numbers, and underscores")
            valid = False
            
        if not password:
            self.set_input_error('password_input', "Password is required")
            valid = False
        elif len(password) < 8:
            self.set_input_error('password_input', "Password must be at least 8 characters")
            valid = False
        elif not self.is_strong_password(password):
            self.set_input_error('password_input', "Password must contain letters and numbers")
            valid = False
            
        return valid
    
    def is_valid_email(self, email):
        """Check if email format is valid"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def is_valid_username(self, username):
        """Check if username contains only valid characters"""
        username_pattern = r'^[a-zA-Z0-9_]+$'
        return re.match(username_pattern, username) is not None
    
    def is_strong_password(self, password):
        """Check if password meets strength requirements"""
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        return has_letter and has_number
    
    def set_input_error(self, input_id, message):
        """Set error state for input field"""
        self.show_snackbar(message)
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
            Logger.error(f"SignupScreen: Input field '{input_id}' not found")
    
    def clear_errors(self):
        """Clear error states from all input fields"""
        input_fields = ['email_input', 'username_input', 'password_input']
        
        for field_id in input_fields:
            try:
                field = self.ids[field_id]
                if hasattr(field, 'error'):
                    field.error = False
                if hasattr(field, 'helper_text'):
                    field.helper_text = ""
            except (KeyError, AttributeError) as e:
                Logger.error(f"SignupScreen: Error clearing field {field_id}: {e}")
    
    def perform_signup(self, email, password, username):
        """Perform signup API call in background thread"""
        try:
            response = send_code_api(email)
            Clock.schedule_once(lambda dt: self.handle_signup_response(response, email, password, username), 0)
        except Exception as e:
            Logger.error(f"SignupScreen: Signup API error: {e}")
            Clock.schedule_once(lambda dt: self.handle_signup_error(str(e)), 0)
    
    def handle_signup_response(self, response, email, password, username):
        """Handle signup API response on main thread"""
        self.signup_in_progress = False
        self.set_loading_state(False)
        
        if response and response.get("status") == "success":
            self.on_signup_success(email, password, username)
        else:
            error_message = response.get("message", "Signup failed") if response else "Signup failed"
            Logger.error(f"SignupScreen: Fallback button search failed: {error_message}")
            self.on_signup_failure(error_message)
    
    def handle_signup_error(self, error_message):
        """Handle signup API errors on main thread"""
        self.signup_in_progress = False
        self.set_loading_state(False)
        self.on_signup_failure(f"Connection error: {error_message}")
    
    def on_signup_success(self, email, password, username):
        """Handle successful signup"""
        try:
            app = App.get_running_app()
            if app:
                app.signup_data = {
                    "email": email,
                    "password": password,
                    "username": username,
                }
            
            self.clear_input_fields()
            self.clear_errors()
            
            self.show_snackbar("Verification code sent to your email!")
            
            if app and hasattr(app, 'root') and hasattr(app.root, 'ids'):
                screen_manager = app.root.ids.get('screen_manager')
                if screen_manager:
                    screen_manager.current = 'email_code'
                    if hasattr(screen_manager, 'transition'):
                        screen_manager.transition.direction = 'left'
                else:
                    Logger.error("SignupScreen: Screen manager not found")
            else:
                Logger.error("SignupScreen: App root or screen manager not accessible")
                
        except Exception as e:
            Logger.error(f"SignupScreen: Error handling signup success: {e}")
    
    def on_signup_failure(self, error_message):
        """Handle signup failure"""
        try:
            self.set_input_error('email_input', error_message)
            
            toast(error_message)
            
        except Exception as e:
            Logger.error(f"SignupScreen: Error handling signup failure: {e}")
    
    def clear_input_fields(self):
        """Clear all input fields"""
        input_fields = ['email_input', 'username_input', 'password_input']
        
        for field_id in input_fields:
            try:
                self.ids[field_id].text = ""
            except KeyError:
                Logger.error(f"SignupScreen: Input field '{field_id}' not found")
    
    def get_button_widget(self):
        """Helper to find the actual button widget"""
        try:
            for widget in self.walk():
                if (hasattr(widget, 'style') and widget.style == "elevated" and 
                    hasattr(widget, 'on_press')):
                    return widget
        except Exception as e:
            Logger.error(f"SignupScreen: Error finding button widget: {e}")
        return None
    
    def set_loading_state(self, loading):
        """Set loading state for signup button"""
        try:
            button_text = self.ids.signup_button
            if hasattr(button_text, 'text'):
                if loading:
                    button_text.text = "Sending Code..."
                else:
                    button_text.text = "Sign Up"
            
            if hasattr(button_text, 'parent'):
                button = button_text.parent
                if hasattr(button, 'disabled'):
                    button.disabled = loading
                    
        except (KeyError, AttributeError) as e:
            Logger.error(f"SignupScreen: Error setting button state: {e}")
            try:
                for widget in self.walk():
                    if hasattr(widget, 'style') and widget.style == "elevated":
                        widget.disabled = loading
                        break
            except Exception as e2:
                Logger.error(f"SignupScreen: Fallback button search failed: {e2}")
    
    def on_enter(self):
        """Called when screen is entered"""
        super().on_enter()
        self.clear_errors()
        self.set_loading_state(False)
        self.signup_in_progress = False
    
    def on_leave(self):
        """Called when screen is left"""
        super().on_leave()
        self.signup_in_progress = False
        self.set_loading_state(False)