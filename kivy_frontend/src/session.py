import json
import os

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".myapp_session")


def get_token():
    """Retrieve the token from the file, if it exists."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("token")
        except Exception:
            return None
    return None


def clear_token():
    """Delete the session file."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
