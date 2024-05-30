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


# Initialize Rich console
console = Console()

# Path to the data storage file
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
        
def add_project(leader_username):
    projects = load_data(PROJECTS_FILE)
    title = console.input("Enter the title of the new project: ")

    if any(project['title'] == title for project in projects):
        console.print("A project with this title already exists. Please use a unique title.", style="bold red")
        return

    project_id  = str(uuid.uuid4())
    start_time = datetime.now().replace(microsecond=0)
    end_time = start_time + timedelta(hours=24)
    project = {
        'id': project_id,
        'title': title,
        'leader': leader_username,
        'members': [leader_username],
        'tasks': [],
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat()
    }
    projects.append(project)
    save_data(projects, PROJECTS_FILE)
    log_action(f"User {leader_username} created a new project: {title}")
    json_file_path = input("Enter the path for the JSON file: ") 
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    save_logs_to_json(json_file_path)

    console.print("Project added successfully!", style="bold green")

# Function to add a member to a project
def add_member_to_project(leader_username):
    project_title = console.input("Enter the project title to add a member: ")
    username = console.input("Enter the username of the member to add: ")
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and project['leader'] == leader_username:
            if username in project['members']:
                console.print("This user is already a member of the project.", style="bold red")
                return
            project['members'].append(username)
            save_data(projects, PROJECTS_FILE)
            log_action(f"User {leader_username} added {username} to the project")
            json_file_path = input("Enter the path for the JSON file: ") 
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            save_logs_to_json(json_file_path)
            console.print("Member added successfully to the project.", style="bold green")
            return
    console.print("Project not found or you are not the leader of this project.", style="bold red")

# Function to remove a member from a project
def remove_member_from_project(leader_username):
    project_title = console.input("Enter the project title to remove a member from: ")
    username = console.input("Enter the username of the member to remove: ")
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and project['leader'] == leader_username:
            if username in project['members']:
                project['members'].remove(username)
                save_data(projects, PROJECTS_FILE)
                log_action(f"User {leader_username} removed {username} from the project")
                json_file_path = input("Enter the path for the JSON file: ") 
                os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                save_logs_to_json(json_file_path)
                console.print("Member removed successfully from the project.", style="bold green")
                return
            else:
                console.print("This user is not a member of the project.", style="bold red")
                return
    console.print("Project not found or you are not the leader of this project.", style="bold red")

def assign_task_to_member(leader_username):
    project_title = console.input("Enter the project title to assign a task: ")
    member_username = console.input("Enter the username of the member to assign the task to: ")
    task_description = console.input("Enter the task description: ")
    task_details = console.input("Enter additional details for the task (optional): ")
    start_time = datetime.now().replace(microsecond=0)
    end_time = start_time + timedelta(hours=24)
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and project['leader'] == leader_username:
            if member_username in project['members']:
                # Ensure the 'tasks' key exists in the project dictionary
                if 'tasks' not in project:
                    project['tasks'] = []  # Create an empty list if 'tasks' key does not exist

                task = {
                    'id': str(uuid.uuid4()),
                    'description': task_description,
                    'details': task_details,  # Add details to the task
                    'assigned_to': member_username,
                    'priority': Priority.LOW.value,  # Default priority
                    'status': Status.BACKLOG.value,  # Default status
                    'comments': [],  # Initialize comments list
                    'start_time': start_time.isoformat(),  # Add start time
                    'end_time': end_time.isoformat()  # Add end time
                }
                project['tasks'].append(task)
                save_data(projects, PROJECTS_FILE)  
                log_action(f"User {leader_username} assigned task {task_description} to the {member_username}")
                json_file_path = input("Enter the path for the JSON file: ") 
                os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                save_logs_to_json(json_file_path)
                console.print("Task assigned successfully to the member.", style="bold green")
                return
            else:
                console.print("This user is not a member of the project.", style="bold red")
                return
    console.print("Project not found or you are not the leader of this project.", style="bold red")

# Function to delete a project
def delete_project(leader_username):
    project_title = console.input("Enter the project title to delete: ")
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and project['leader'] == leader_username:
            projects.remove(project)
            save_data(projects, PROJECTS_FILE)
            log_action(f"User {leader_username} deleted the project {project_title}")
            json_file_path = input("Enter the path for the JSON file: ") 
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            save_logs_to_json(json_file_path)
            console.print("Project deleted successfully.", style="bold green")
            return
    console.print("Project not found or you are not the leader of this project.", style="bold red")

def list_projects(user):
    projects = load_data(PROJECTS_FILE)
    user_projects = [p for p in projects if p['leader'] == user['username']]
    
    if user_projects:
        for project in user_projects:
            console.print(f"Title: {project['title']}", style="bold magenta")
        while True:
            console.print("\nOptions for projects you are leading:", style="bold")
            console.print("1. Add a member to a project", style="bold")
            console.print("2. Remove a member from a project", style="bold")
            console.print("3. Assign a task to a member", style="bold")
            console.print("4. View project details", style="bold")
            console.print("5. View tasks by status", style="bold") 
            console.print("6. Delete a project", style="bold")
            console.print("7. Return to main menu", style="bold")
            choice = console.input("Choose an option: ")
            if choice == '1':
                add_member_to_project(user['username'])
            elif choice == '2':
                remove_member_from_project(user['username'])
            elif choice == '3':
                assign_task_to_member(user['username'])
            elif choice == '4':
                display_project_details(user)
            elif choice == '5':
                view_tasks_by_status(user) 
            elif choice == '6':
                delete_project(user['username'])
            elif choice == '7':
                break
            else:
                console.print("Invalid choice. Please try again.", style="bold red")
    else:
        console.print("No projects found where you are the leader.", style="bold red")

# Function to display project details for a member
def display_project_details(user):
    project_title = console.input("Enter the project title to view details: ")
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and (user['username'] in project['members'] or user['username'] == project['leader']):
            console.print(f"Project Title: {project['title']}", style="bold magenta")
            console.print(f"Project Description: {project.get('description', 'No description provided')}", style="bold magenta")
            console.print(f"Project Leader: {project['leader']}", style="bold magenta")
            console.print(f"Start Time: {project['start_time']}", style="bold magenta")
            console.print(f"End Time: {project['end_time']}", style="bold magenta")
            console.print("Members:", style="bold magenta")
            for member in project['members']:
                console.print(f" - {member}", style="bold yellow")
            console.print("Tasks:", style="bold magenta")
            for task in project['tasks']:
                console.print(f" - {task['description']} assigned to {task['assigned_to']}", style="bold yellow")
                console.print(f"   Priority: {task['priority']}", style="bold yellow")
                console.print(f"   Status: {task['status']}", style="bold yellow")
                console.print(f"   Start Time: {task['start_time']}", style="bold yellow")
                console.print(f"   End Time: {task['end_time']}", style="bold yellow")
                console.print("   Comments:", style="bold yellow")
                for comment in task['comments']:
                    console.print(f"     {comment['timestamp']} - {comment['username']}: {comment['content']}", style="bold yellow")
            return
    console.print("Project not found or you are not a member of this project.", style="bold red")

# Function to list projects where the user is a member
def list_projects_as_member(user):
    projects = load_data(PROJECTS_FILE)
    user_projects = [p for p in projects if user['username'] in p['members']]
    if user_projects:
        for project in user_projects:
            console.print(f"Title: {project['title']}", style="bold magenta")
        while True:
            console.print("\nOptions for projects you are a member of:", style="bold")
            console.print("1. View project details", style="bold")
            console.print("2. View tasks by status", style="bold")
            console.print("3. Return to main menu", style="bold")
            choice = console.input("Choose an option: ")
            if choice == '1':
                display_project_details(user)
            elif choice == '2':
                view_tasks_by_status(user)
            elif choice == '3':
                break
            else:
                console.print("Invalid choice. Please try again.", style="bold red")
    else:
        console.print("No projects found where you are a member.", style="bold red")

def view_tasks_by_status(user):
    project_title = console.input("Enter the project title to view tasks by status: ")
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and (user['username'] in project['members'] or user['username'] == project['leader']):
            tasks_by_status = {status: [] for status in Status}
            for task in project['tasks']:
                tasks_by_status[Status[task['status']]].append(task)
            
            table = Table(title="Tasks by Status and Details")
            table.add_column("Backlog", style="dim", width=20)
            table.add_column("To Do", style="dim", width=20)
            table.add_column("Doing", style="dim", width=20)
            table.add_column("Done", style="dim", width=20)
            table.add_column("Archived", style="dim", width=20)
            
            max_rows = max(len(tasks_by_status[status]) for status in Status)
            for i in range(max_rows):
                row = []
                for status in Status:
                    if i < len(tasks_by_status[status]):
                        task = tasks_by_status[status][i]
                        row.append(f"{task['description']} (ID: {task['id']})")
                    else:
                        row.append("")
                table.add_row(*row)
            
            console.print(table)
            task_id = console.input("Enter the task ID to edit: ")
            #view_task_details(user, project, task_id)
            return
    console.print("Project not found or you are not a member of this project.", style="bold red")
