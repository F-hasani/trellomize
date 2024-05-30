from loguru import logger
from rich.console import Console
import os
import json


log_file_path = os.path.join(os.path.dirname(__file__), 'app.log')
logger.remove() 
logger.add(log_file_path, rotation="1 MB", retention="10 days", level="INFO")

# Function to load data from file
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def show_logs():
    if not os.path.exists(log_file_path):
        print("Log file does not exist.")
        return None
    with open(log_file_path, 'r') as file:
        logs = file.read()
    if not logs:
        print("Log file is empty.")
        return None
    return logs

def save_logs_to_json(json_file_path):
    logs = show_logs()
    if logs is None:
        print("No logs to save.")
        return
    
    log_entries = logs.splitlines()

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            try:
                log_data = json.load(json_file)
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []

    existing_logs = set(entry['log'] for entry in log_data)

    new_logs = []
    for entry in log_entries:
        if entry not in existing_logs:
            new_logs.append({"log": entry})
    
    if not new_logs:
        print("No new logs to save.")
        return

    log_data.extend(new_logs)

    with open(json_file_path, 'w') as json_file:
        json.dump(log_data, json_file, indent=4)
    print(f"Logs have been saved to {json_file_path}")
    

    