import json
import os

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".myapp_session")


def save_token(token):
    """Save the token to a file."""
    with open(SESSION_FILE, "w") as f:
        json.dump({"token": token}, f)
