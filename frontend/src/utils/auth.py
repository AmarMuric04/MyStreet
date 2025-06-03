import requests

from utils.session import get_token


def login_api(email, password):
    """
    Sends login credentials to the backend server and saves the token.

    Args:
        email (str): User's email address.
        password (str): User's password.

    Returns:
        dict: Response from the server.
    """
    url = "http://localhost:5000/login"
    payload = {"email": email.strip(), "password": password.strip()}
    if not email or not password:
        return {"status": "error", "message": "Please enter both email and password!"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return {"status": "success", "message": "Login successful!"}
        else:
            error_message = response.json().get("error", f"Error: {response.status_code}")
            return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}


def signup_api(email, password, username):
    """
    Sends signup credentials to the backend server.

    Args:
        email (str): User's email address.
        password (str): User's password.
        username (str): User's chosen username.

    Returns:
        dict: Response from the server.
    """
    url = "http://localhost:5000/signup"
    payload = {"email": email.strip(), "password": password.strip(), "username": username.strip()}

    if not email or not password or not username:
        return {"status": "error", "message": "Please enter email, password and username!"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            return {"status": "success", "message": "Signup successful!"}
        else:
            error_message = response.json().get("error", f"Error: {response.status_code}")
            return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}


def send_code_api(email):
    """
    Requests the server to generate and send a 6-digit verification code via email.
    
    Args:
        email (str): The recipient's email address.
        
    Returns:
        dict: Response from the server.
    """
    url = "http://localhost:5000/send-code"
    payload = {"email": email.strip()}
    
    if not email:
        return {"status": "error", "message": "Email is required!"}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            # Optionally, the response might include the code (not recommended in production).
            return {"status": "success", "message": "Verification code sent!"}
        else:
            error_message = response.json().get("error", f"Error: {response.status_code}")
            return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}


def verify_code_api(email, code, attempt):
    """
    Verifies the provided 6-digit code against the one stored on the server.
    
    Args:
        email (str): The user's email address.
        code (str): The 6-digit code provided by the user.
        
    Returns:
        dict: Response from the server.
    """
    url = "http://localhost:5000/verify-code"
    payload = {"email": email.strip(), "code": code.strip()}
    
    if not email or not code:
        return {"status": "error", "message": "Email and code are required!"}
    
    if attempt == 1:
        return {"status": "error", "message": "Invalid code. Try Again!"}
        
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return {"status": "success", "message": "Code verified successfully!"}
        else:
            error_message = response.json().get("error", f"Error: {response.status_code}")
            return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}

def get_logged_in_user():
    token = get_token()
    if not token:
        print("No token found; user is not logged in.")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get("http://localhost:5000/current_user", headers=headers)
        if response.status_code == 200:
            user_data = response.json().get("user")
            print("User data fetched:", user_data)
            user_data['bio'] = ""
            return user_data
        else:
            print("Error from backend:", response.json())
            return None
    except Exception as e:
        print("An error occurred while fetching user data:", e)
        return None