import json
import os
import uuid
from enum import Enum
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta
from loguru import logger
import base64


log_file_path = os.path.join(os.path.dirname(__file__), 'app.log')

logger.remove()  
logger.add(log_file_path, rotation="1 MB", retention="10 days", level="INFO")

console = Console()

DATA_FILE = 'users.json'
PROJECTS_FILE = 'projects.json'

class Priority(Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'

class Status(Enum):
    BACKLOG = 'BACKLOG'
    TODO = 'TODO'
    DOING = 'DOING'
    DONE = 'DONE'
    ARCHIVED = 'ARCHIVED'
    
def log_action(action_message):
    logger.info(action_message)

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
    

# Function to load data from file
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

# Function to save data to file
def save_data(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
        
def get_project_id_by_name(project_name):
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_name:
            project_id = project['id']
            return project_id
    console.print("Project not found.", style="bold red")
    return None

def get_task_description_by_id(task_id):
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        for task in project['tasks']:
            if task['id'] == task_id:
                task_description = task['description']
                return task_description
    console.print("Task not found.", style="bold red")
    return None


def update_task_description():
    project_title = input("Enter the project title: ")
    task_id = input("Enter the task ID: ")
    new_description = input("Enter the new description: ")

    task_description = get_task_description_by_id(task_id)
    projects = load_data('projects.json')  # فرض می‌کنیم که داده‌ها در فایل projects.json ذخیره شده‌اند
    for project in projects:
        if project['title'] == project_title:
            for task in project['tasks']:
                if task['id'] == task_id:
                    task['description'] = new_description
                    save_data(projects, 'projects.json')
                    log_action(f"{task_description}'s description changed to {new_description}")
                    json_file_path = input("Enter the path for the JSON file: ") 
                    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                    save_logs_to_json(json_file_path)
                    console.print("Task description updated successfully.", style="bold green")
                    return
            console.print("Task not found.", style="bold red")
            return
    console.print("Project not found.", style="bold red")   
    
def change_task_priority(user):
    project_title = console.input("Enter the project title: ")
    task_id = console.input("Enter the task ID: ")
    new_priority = console.input("Enter the new priority (CRITICAL, HIGH, MEDIUM, LOW): ").strip().upper()


    task_description = get_task_description_by_id(task_id)
    if new_priority not in Priority.__members__:
        console.print("Invalid priority.", style="bold red")
        return

    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and (user['username'] == project['leader'] or user['username'] in [task['assigned_to'] for task in project['tasks'] if task['id'] == task_id]):
            for task in project['tasks']:
                if task['id'] == task_id:
                    task['priority'] = new_priority
                    save_data(projects, PROJECTS_FILE)
                    log_action(f" Task {task_description} priority has been updated to {new_priority}")
                    json_file_path = input("Enter the path for the JSON file: ") 
                    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                    save_logs_to_json(json_file_path)
                    console.print("Task priority updated successfully.", style="bold green")
                    return
            console.print("Task not found.", style="bold red")
            return
    console.print("Project not found or you do not have the necessary permissions.", style="bold red")


def update_task_details():
    project_title = input("Enter the project title: ")
    task_id = input("Enter the task ID: ")

    task_description = get_task_description_by_id(task_id)
    projects = load_data('projects.json')
    for project in projects:
        if project['title'] == project_title:
            for task in project['tasks']:
                if task['id'] == task_id:
                    print(f"details: {task['details']}")

                    new_details = input("Enter the new details: ")

                    if new_details:
                        task['details'] = new_details

                    save_data(projects, 'projects.json')
                    log_action(f"{task_description}'s details changed to {new_details}")
                    json_file_path = input("Enter the path for the JSON file: ") 
                    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                    save_logs_to_json(json_file_path)
                    console.print("Task details updated successfully.", style="bold green")
                    return
            console.print("Task not found.", style="bold red")
            return
    console.print("Project not found.", style="bold red")

# Function to edit a task
def edit_task(project_id, task_id, new_status):
    
    projects = load_data(PROJECTS_FILE)
    
    task_description = get_task_description_by_id(task_id)
    for project in projects:
        if project['id'] == project_id:
            for task in project['tasks']:
                if task['id'] == task_id:
                    task['status'] = new_status
                    save_data(projects, PROJECTS_FILE)
                    log_action(f" Task {task_description} status has been updated to {new_status}")
                    json_file_path = input("Enter the path for the JSON file: ") 
                    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                    save_logs_to_json(json_file_path)
                    console.print("Task status updated successfully.", style="bold green")
                    return
    console.print("Task or project not found.", style="bold red")

def add_comment_to_task(user):
    project_title = console.input("Enter the project title: ")
    task_id = console.input("Enter the task ID: ")
    comment_content = console.input("Enter your comment: ")

    task_description = get_task_description_by_id(task_id)
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and user['username'] in project['members']:
            for task in project['tasks']:
                if task['id'] == task_id and (task['assigned_to'] == user['username'] or user['username'] == project['leader']):
                    comment = {
                        'timestamp': datetime.now().replace(microsecond=0).isoformat(),
                        'username': user['username'],
                        'content': comment_content
                    }
                    task['comments'].append(comment)
                    save_data(projects, PROJECTS_FILE)
                    log_action(f"Comment was added in {task_description} task")
                    json_file_path = input("Enter the path for the JSON file: ") 
                    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                    save_logs_to_json(json_file_path)
                    console.print("Comment added successfully.", style="bold green")
                    return
            console.print("Task not found or not assigned to you.", style="bold red")
            return
    console.print("Project not found or you are not a member of this project.", style="bold red")



def view_task_details(user, project, task_id):
    for task in project['tasks']:
        if task['id'] == task_id:
            console.print(f"Task Description: {task['description']}", style="bold magenta")
            console.print(f"Task Details: {task.get('details', 'No details provided')}", style="bold magenta")
            console.print(f"Assigned To: {task['assigned_to']}", style="bold magenta")
            console.print(f"Priority: {task['priority']}", style="bold magenta")
            console.print(f"Status: {task['status']}", style="bold magenta")
            console.print(f"Start Time: {task['start_time']}", style="bold magenta")
            console.print(f"End Time: {task['end_time']}", style="bold magenta")
            console.print("Comments:", style="bold magenta")
            for comment in task['comments']:
                console.print(f" - {comment['timestamp']} - {comment['username']}: {comment['content']}", style="bold yellow")
            
            if task['assigned_to'] == user['username'] or user['username'] == project['leader']:
                console.print("\nOptions for task:", style="bold")
                console.print("1. Edit task description", style="bold")
                console.print("2. Edit task details", style="bold")
                console.print("3. Edit task priority", style="bold")
                console.print("4. Edit task status", style="bold")
                console.print("5. Add a comment to a task", style="bold")
                console.print("6. Return to previous menu", style="bold")
                choice = console.input("Choose an option: ")
                if choice == '1':
                    update_task_description()
                    
                elif choice == '2':
                    update_task_details()
                elif choice == '3':
                    change_task_priority(user)
                elif choice == '4':
                    project_title = console.input("Enter the project title: ")
                    task_id = console.input("Enter the task ID: ")
                    new_status = console.input("Enter the new status (BACKLOG , TODO , DOING , DONE , ARCHIVED): ").strip().upper()
                    project_id = get_project_id_by_name(project_title)
                    edit_task(project['id'], task_id, new_status)
                elif choice == '5':
                    add_comment_to_task(user)
                elif choice == '6':
                    return
                else:
                    console.print("Invalid choice. Please try again.", style="bold red")
            else :
                console.print("You are not the leader of this project or not assigned to this task.", style="bold red")
            return
