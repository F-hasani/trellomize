import json
import os
import uuid
from enum import Enum
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta
from loguru import logger

# Initialize Rich console
console = Console()

# Path to the data storage file
DATA_FILE = 'users.json'
PROJECTS_FILE = 'projects.json'
LOG_FILE = 'activity.log'


# Function to load data from file
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

# Function to save data to file
def save_data(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        console.print(f"Data saved to {file_path}", style="bold green")
    except Exception as e:
        console.print(f"Error saving data to {file_path}: {e}", style="bold red")

def create_account(username, password, email, is_manager):
    users = load_data(DATA_FILE)
    if any(user['username'] == username for user in users):
        console.print("This username is already taken.", style="bold red")
        return False
    user = {
        'id': str(uuid.uuid4()),
        'username': username,
        'password': password,
        'email': email,
        'role': 'manager' if is_manager else 'member',
        'active': True
    }
    users.append(user)
    save_data(users, DATA_FILE)
    logger.info(f"User account created: {username}, Manager status: {'Yes' if is_manager else 'No'}")
    console.print("User account created successfully. Manager status: " + ("Yes" if is_manager else "No"), style="bold green")
    return True

# Function to log in to a user account
def login(username, password):
    users = load_data(DATA_FILE)
    for user in users:
        if user['username'] == username and user['password'] == password:
            if user['active']:
                logger.info(f"User logged in: {username}")
                console.print(f"Welcome back, {username}! You are logged in as {'a manager' if user['role'] == 'manager' else 'a member'}.", style="bold blue")
                return user
            else:
                console.print("Your account is inactive. Please contact the system administrator.", style="bold red")
                return None
    console.print("Invalid username or password. Please try again or create a new account.", style="bold red")
    return None