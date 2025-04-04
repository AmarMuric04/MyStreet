import requests
from session import save_token


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
            token = data.get("token")
            if token:
                # Save the token to a file
                save_token(token)
                return {
                    "status": "success",
                    "token": token,
                    "message": "Login successful!",
                }
            else:
                return {"status": "error", "message": "Token not found in response."}
        else:
            error_message = response.json().get(
                "error", f"Error: {response.status_code}"
            )
            return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}


def signup_api(email, password):
    """
    Sends signup credentials to the backend server.

    Args:
        email (str): User's email address.
        password (str): User's password.

    Returns:
        dict: Response from the server.
    """
    url = "http://localhost:5000/signup"
    payload = {"email": email.strip(), "password": password.strip()}

    if not email or not password:
        return {"status": "error", "message": "Please enter both email and password!"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            return {"status": "success", "message": "Signup successful!"}
        else:
            # Extract error message if available
            error_message = response.json().get(
                "error", f"Error: {response.status_code}"
            )
            return {"status": "error", "message": error_message}
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}
