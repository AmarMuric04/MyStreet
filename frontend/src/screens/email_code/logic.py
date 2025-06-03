import platform
import re
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivymd.uix.screen import MDScreen

# Cross-platform toast/notification handling
try:
    if platform.system() == 'Android':
        from kivymd.toast import toast
    else:
        # Use KivyMD Snackbar for desktop platforms
        from kivymd.uix.snackbar import Snackbar
        def toast(message):
            try:
                snackbar = Snackbar(
                    text=message,
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(1.0 - 20/400)  # Responsive width
                )
                snackbar.open()
            except Exception as e:
                print(f"Notification: {message}")
                Logger.info(f"EmailCode: {message}")
except ImportError:
    def toast(message):
        print(f"Notification: {message}")
        Logger.info(f"EmailCode: {message}")

from utils.auth import send_code_api, signup_api, verify_code_api

# Load the design file with error handling
try:
    Builder.load_file("frontend/src/screens/email_code/design.kv")
except FileNotFoundError:
    Logger.error("EmailCode: Could not load design.kv file")
except Exception as e:
    Logger.error(f"EmailCode: Error loading design file: {e}")

class EmailCode(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verification_in_progress = False
        self.resend_in_progress = False
        self.resend_cooldown = False
        self.cooldown_time = 30  # 30 seconds cooldown for resend
        self.attempt = 1
    
    def on_enter(self):
        """Called when screen is entered"""
        super().on_enter()
        try:
            app = App.get_running_app()
            signup_data = getattr(app, "signup_data", None)
            
            if signup_data and signup_data.get("email"):
                email = signup_data.get("email")
                self.update_email_label(email)
            else:
                Logger.warning("EmailCode: No signup data found")
                self.update_email_label("your email")
                toast("Warning: No signup data found. Please restart signup process.")
                
            # Clear any previous states
            self.clear_errors()
            self.set_verify_loading_state(False)
            self.verification_in_progress = False
            
        except Exception as e:
            Logger.error(f"EmailCode: Error in on_enter: {e}")
            self.update_email_label("your email")
    
    def update_email_label(self, email):
        """Update the email label safely"""
        try:
            if 'email_label' in self.ids:
                self.ids.email_label.text = f"We sent a code to {email}"
            else:
                Logger.warning("EmailCode: email_label not found in screen")
        except Exception as e:
            Logger.error(f"EmailCode: Error updating email label: {e}")
    
    def proceed(self):
        """Handle verify button press"""
        # Prevent multiple simultaneous verification attempts
        if self.verification_in_progress:
            return
            
        # Clear previous error states
        self.clear_errors()
        
        # Get and validate code input
        code = self.get_code_input()
        if not self.validate_code(code):
            return
            
        # Set loading state
        self.set_verify_loading_state(True)
        self.verification_in_progress = True
        
        # Use threading to prevent UI blocking
        threading.Thread(target=self.perform_verification, args=(code,), daemon=True).start()
    
    def get_code_input(self):
        """Get code input safely"""
        try:
            return self.ids.code_input.text.strip()
        except KeyError:
            Logger.error("EmailCode: code_input not found")
            toast("Error: Code input field not found")
            return ""
    
    def validate_code(self, code):
        """Validate verification code"""
        if not code:
            self.set_input_error("Please enter the verification code")
            return False
        
        # Check if code is numeric and appropriate length (usually 4-8 digits)
        if not code.isdigit():
            self.set_input_error("Verification code should contain only numbers")
            return False
            
        if len(code) < 4 or len(code) > 8:
            self.set_input_error("Verification code should be 4-8 digits long")
            return False
            
        return True
    
    def perform_verification(self, code):
        """Perform verification in background thread"""
        try:
            app = App.get_running_app()
            signup_data = getattr(app, "signup_data", None)
            
            if not signup_data:
                Clock.schedule_once(lambda dt: self.handle_verification_error("No signup data found. Please restart the signup process."), 0)
                return
            
            email = signup_data.get("email")
            if not email:
                Clock.schedule_once(lambda dt: self.handle_verification_error("Email not found in signup data"), 0)
                return
            
            # Step 1: Verify the code
            verify_response = verify_code_api(email, code, self.attempt)
            
            self.attempt = self.attempt + 1
            
            if verify_response and verify_response.get("status") == "success":
                # Step 2: Complete signup if verification successful
                signup_response = signup_api(
                    email,
                    signup_data.get("password"),
                    signup_data.get("username")
                )
                Clock.schedule_once(lambda dt: self.handle_signup_response(signup_response), 0)
            else:
                error_msg = verify_response.get("message", "Verification failed") if verify_response else "Verification failed"
                
                Clock.schedule_once(lambda dt: self.handle_verification_error(error_msg), 0)
                
        except Exception as e:
            Logger.error(f"EmailCode: Verification error: {e}")
            
            # Clock.schedule_once(lambda dt: self.handle_verification_error(f"Connection error: {str(e)}"), 0)
    
    def handle_signup_response(self, signup_response):
        """Handle final signup response on main thread"""
        self.verification_in_progress = False
        self.set_verify_loading_state(False)
        
        if signup_response and signup_response.get("status") == "success":
            self.on_signup_complete()
        else:
            error_msg = signup_response.get("message", "Signup failed") if signup_response else "Signup failed"
            self.handle_verification_error(error_msg)
    
    def handle_verification_error(self, error_message):
        """Handle verification errors on main thread"""
        app = App.get_running_app()
        app.show_snackbar("Invalid code. Please try again!")
        self.verification_in_progress = False
        self.set_verify_loading_state(False)
        self.set_input_error(error_message)
        toast(error_message)
    
    def on_signup_complete(self):
        """Handle successful signup completion"""
        try:
            # Clear signup data
            app = App.get_running_app()
                
            
            app = App.get_running_app()
            if app:
                app.signup_data = None
            
            # Clear input and errors
            self.clear_code_input()
            self.clear_errors()
            
            # Show success message
            app = App.get_running_app()
            app.show_snackbar("Account created successfully! Please log in.")
            
            # Navigate to login screen
            if app and hasattr(app, 'root') and hasattr(app.root, 'ids'):
                screen_manager = app.root.ids.get('screen_manager')
                if screen_manager:
                    screen_manager.current = 'login'
                    # Optional: set transition direction
                    if hasattr(screen_manager, 'transition'):
                        screen_manager.transition.direction = 'right'
                else:
                    Logger.error("EmailCode: Screen manager not found")
            else:
                Logger.error("EmailCode: App root or screen manager not accessible")
                
        except Exception as e:
            Logger.error(f"EmailCode: Error completing signup: {e}")
    
    def on_send_again(self):
        """Handle resend code button press"""
        # Prevent multiple simultaneous resend attempts
        if self.resend_in_progress or self.resend_cooldown:
            if self.resend_cooldown:
                toast("Please wait before requesting another code")
            return
            
        try:
            app = App.get_running_app()
            signup_data = getattr(app, "signup_data", None)
            
            if not signup_data or not signup_data.get("email"):
                toast("Error: No email found. Please restart signup process.")
                return
                
            self.resend_in_progress = True
            self.set_resend_loading_state(True)
            
            # Use threading for resend
            email = signup_data.get("email")
            threading.Thread(target=self.perform_resend, args=(email,), daemon=True).start()
            
        except Exception as e:
            Logger.error(f"EmailCode: Error in resend: {e}")
            toast("Error sending code")
    
    def perform_resend(self, email):
        """Perform code resend in background thread"""
        try:
            response = send_code_api(email)
            Clock.schedule_once(lambda dt: self.handle_resend_response(response), 0)
        except Exception as e:
            Logger.error(f"EmailCode: Resend API error: {e}")
            Clock.schedule_once(lambda dt: self.handle_resend_error(str(e)), 0)
    
    def handle_resend_response(self, response):
        """Handle resend response on main thread"""
        self.resend_in_progress = False
        self.set_resend_loading_state(False)
        
        if response and response.get("status") == "success":
            app = App.get_running_app()
            app.show_snackbar("New verification code sent!")
            self.clear_errors()
            self.start_resend_cooldown()
        else:
            error_msg = response.get("message", "Failed to resend code") if response else "Failed to resend code"
            toast(error_msg)
    
    def handle_resend_error(self, error_message):
        """Handle resend errors on main thread"""
        self.resend_in_progress = False
        self.set_resend_loading_state(False)
        toast(f"Connection error: {error_message}")
    
    def start_resend_cooldown(self):
        """Start cooldown period for resend button"""
        self.resend_cooldown = True
        Clock.schedule_once(self.end_resend_cooldown, self.cooldown_time)
    
    def end_resend_cooldown(self, dt):
        """End resend cooldown period"""
        self.resend_cooldown = False
    
    def set_input_error(self, message):
        """Set error state for code input field"""
        try:
            input_field = self.ids.code_input
            if hasattr(input_field, 'error'):
                input_field.error = True
            if hasattr(input_field, 'helper_text'):
                input_field.helper_text = message
                input_field.helper_text_mode = "on_error"
        except KeyError:
            Logger.error("EmailCode: code_input field not found")
    
    def clear_errors(self):
        """Clear error states from input field"""
        try:
            field = self.ids.code_input
            if hasattr(field, 'error'):
                field.error = False
            if hasattr(field, 'helper_text'):
                field.helper_text = ""
        except (KeyError, AttributeError) as e:
            Logger.error(f"EmailCode: Error clearing input field: {e}")
    
    def clear_code_input(self):
        """Clear the code input field"""
        try:
            self.ids.code_input.text = ""
        except KeyError:
            Logger.error("EmailCode: code_input field not found")
    
    def set_verify_loading_state(self, loading):
        """Set loading state for verify button"""
        try:
            # Handle MDButtonText structure
            button_text = self.ids.verify_button
            if hasattr(button_text, 'text'):
                if loading:
                    button_text.text = "Verifying..."
                else:
                    button_text.text = "Verify"
            
            # Find and disable/enable the actual button
            if hasattr(button_text, 'parent'):
                button = button_text.parent
                if hasattr(button, 'disabled'):
                    button.disabled = loading
                    
        except (KeyError, AttributeError) as e:
            Logger.error(f"EmailCode: Error setting verify button state: {e}")
            # Fallback: try to find button by walking the widget tree
            self.set_button_state_fallback(loading, "verify")
    
    def set_resend_loading_state(self, loading):
        """Set loading state for resend button"""
        try:
            # This will depend on your KV structure for the resend button
            # Adjust the ID name as needed
            if 'resend_button' in self.ids:
                button = self.ids.resend_button
                if hasattr(button, 'disabled'):
                    button.disabled = loading
                if hasattr(button, 'text'):
                    button.text = "Sending..." if loading else "Send Again"
        except (KeyError, AttributeError) as e:
            Logger.error(f"EmailCode: Error setting resend button state: {e}")
    
    def set_button_state_fallback(self, loading, button_type):
        """Fallback method to find and set button states"""
        try:
            for widget in self.walk():
                if hasattr(widget, 'text') and hasattr(widget, 'disabled'):
                    if button_type == "verify" and ("verify" in widget.text.lower() or "check" in widget.text.lower()):
                        widget.disabled = loading
                        if loading:
                            widget.text = "Verifying..."
                        else:
                            widget.text = "Verify"
                        break
        except Exception as e:
            Logger.error(f"EmailCode: Fallback button search failed: {e}")
    
    def on_leave(self):
        """Called when screen is left"""
        super().on_leave()
        # Reset any ongoing operations
        self.verification_in_progress = False
        self.resend_in_progress = False
        self.set_verify_loading_state(False)