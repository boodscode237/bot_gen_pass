import random
import string
import json
import os
from app.config import PASSWORDS_FILE, DEFAULT_PASSWORD_LENGTH


def generate_robust_password(length=DEFAULT_PASSWORD_LENGTH):
    if length < 8:
        pass  # On ne fait rien, mais on pourrait logguer ou avertir dans le bot
    characters = string.ascii_letters + string.digits + string.punctuation
    password_list = []
    if length >= 4:
        password_list.append(random.choice(string.ascii_lowercase))
        password_list.append(random.choice(string.ascii_uppercase))
        password_list.append(random.choice(string.digits))
        password_list.append(random.choice(string.punctuation))
        for _ in range(length - 4):
            password_list.append(random.choice(characters))
        random.shuffle(password_list)
    else:
        for _ in range(length):
            password_list.append(random.choice(characters))
    return "".join(password_list)


def save_password_to_json(website, email, password):
    new_entry = {"website": website, "email": email, "password": password}
    data = []
    if os.path.exists(PASSWORDS_FILE) and os.path.getsize(PASSWORDS_FILE) > 0:
        try:
            with open(PASSWORDS_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = []
    if not isinstance(data, list):
        data = []
    data.append(new_entry)
    with open(PASSWORDS_FILE, "w") as f:
        json.dump(data, f, indent=4)
    return True


def get_passwords_json():
    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, "rb") as f:
            return f.read()
    else:
        return b"[]"
