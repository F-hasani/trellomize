import json
import os
import uuid
from enum import Enum
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta
import base64


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
        
def deactivate_user():
    username = input("Enter the username of the account to deactivate: ")

    users = load_data('users.json')  # فرض می‌کنیم که داده‌ها در فایل users.json ذخیره شده‌اند
    for user in users:
        if user['username'] == username:
            if user['active']:
                user['active'] = False
                save_data(users, 'users.json')
                console.print(f"User {username} has been deactivated successfully." , style="bold yellow")
            else:
                console.print(f"User {username} is already deactivated.", style="bold yellow")
            return
    console.print(f"User {username} not found.", style="bold red")

def encode_password(password):
    return base64.b64encode(password.encode('utf-8')).decode('utf-8')


def decode_password(encoded_password):
    return base64.b64decode(encoded_password.encode('utf-8')).decode('utf-8')
    

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

# Function to update task status
def update_task_status(project_title, task_description, new_status):
    projects = load_data(PROJECTS_FILE)
    found = False
    for project in projects:
        if project['title'] == project_title:
            for task in project['tasks']:
                if task['description'] == task_description:
                    task['status'] = new_status
                    found = True
                    break
            if found:
                save_data(projects, PROJECTS_FILE)
                console.print("Task status updated.", style="bold green")
                return
    console.print("Project or task not found.", style="bold red")

# Function to edit a task
def edit_task(project_id, task_id, new_status):
    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['id'] == project_id:
            for task in project['tasks']:
                if task['id'] == task_id:
                    task['status'] = new_status
                    save_data(projects, PROJECTS_FILE)
                    console.print("Task status updated successfully.", style="bold green")
                    return
    console.print("Task or project not found.", style="bold red")

def add_comment_to_task(user):
    project_title = console.input("Enter the project title: ")
    task_id = console.input("Enter the task ID: ")
    comment_content = console.input("Enter your comment: ")

    projects = load_data(PROJECTS_FILE)
    for project in projects:
        if project['title'] == project_title and user['username'] in project['members']:
            for task in project['tasks']:
                if task['id'] == task_id and task['assigned_to'] == user['username']:
                    comment = {
                        'timestamp': datetime.now().isoformat(),
                        'username': user['username'],
                        'content': comment_content
                    }
                    task['comments'].append(comment)
                    save_data(projects, PROJECTS_FILE)
                    console.print("Comment added successfully.", style="bold green")
                    return
            console.print("Task not found or not assigned to you.", style="bold red")
            return
    console.print("Project not found or you are not a member of this project.", style="bold red")


# Function to create a user account
def create_account(username, password, email, is_manager):
    users = load_data(DATA_FILE)
    if any(user['username'] == username for user in users):
        console.print("This username is already taken.", style="bold red")
        return False
    encoded_password = encode_password(password)
    user = {
        'id': str(uuid.uuid4()),
        'username': username,
        'password': encoded_password,
        'email': email,
        'role': 'manager' if is_manager else 'member',
        'active': True
    }
    users.append(user)
    save_data(users, DATA_FILE)
    console.print("User account created successfully. Manager status: " + ("Yes" if is_manager else "No"), style="bold green")
    return True


# Function to log in to a user account
def login(username, password):
    users = load_data(DATA_FILE)
    encoded_password = encode_password(password)
    for user in users:
        if user['username'] == username and user['password'] == encoded_password:
            if user['active']:
                console.print(f"Welcome back, {username}! You are logged in as {'a manager' if user['role'] == 'manager' else 'a member'}.", style="bold blue")
                return user
            else:
                console.print("Your account is inactive. Please contact the system administrator.", style="bold red")
                return None
    console.print("Invalid username or password. Please try again or create a new account.", style="bold red")
    return None

def add_project(leader_username):
    projects = load_data(PROJECTS_FILE)
    title = console.input("Enter the title of the new project: ")
    description = console.input("Enter the description of the new project (optional): ")
    priority = console.input("Enter the priority of the project (CRITICAL, HIGH, MEDIUM, LOW): ").strip().upper()
    status = console.input("Enter the status of the project (BACKLOG, TODO, DOING, DONE, ARCHIVED): ").strip().upper()

    if any(project['title'] == title for project in projects):
        console.print("A project with this title already exists. Please use a unique title.", style="bold red")
        return

    if priority not in Priority.__members__:
        console.print("Invalid priority. Setting to default (LOW).", style="bold red")
        priority = Priority.LOW.value

    if status not in Status.__members__:
        console.print("Invalid status. Setting to default (BACKLOG).", style="bold red")
        status = Status.BACKLOG.value

    project_id  = str(uuid.uuid4())
    start_time = datetime.now().replace(microsecond=0)
    end_time = start_time + timedelta(hours=24)
    project = {
        'id': project_id,
        'title': title,
        'description': description,
        'leader': leader_username,
        'members': [leader_username],
        'tasks': [],
        'comments': [],
        'priority': priority,
        'status': status,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat()
    }
    projects.append(project)
    save_data(projects, PROJECTS_FILE)
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
                save_data(projects, PROJECTS_FILE)  # Save changes
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
            console.print(f"Priority: {project['priority']}", style="bold magenta")
            console.print(f"Status: {project['status']}", style="bold magenta")
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
            console.print("Comments:", style="bold magenta")
            for comment in project['comments']:
                console.print(f" - {comment['timestamp']} - {comment['username']}: {comment['content']}", style="bold yellow")
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
            
            if user['username'] == project['leader']:
                console.print("\nOptions for task:", style="bold")
                console.print("1. Edit task description", style="bold")
                console.print("2. Edit task details", style="bold")
                console.print("3. Edit task priority", style="bold")
                console.print("4. Edit task status", style="bold")
                console.print("5. Add a comment to a task", style="bold")
                console.print("6. Return to previous menu", style="bold")
                choice = console.input("Choose an option: ")
                if choice == '1':
                    new_description = console.input("Enter new task description: ")
                    if new_description in Status.__members__:
                        task['status'] = Status[new_description].value
                        project_name = console.input("Enter the project title to view tasks by status: ")
                        project_id = get_project_id_by_name(project_name)
                        edit_task(project_id,task_id,new_description)
                        save_data(load_data(PROJECTS_FILE), PROJECTS_FILE)
                    else:
                        console.print("Invalid status.", style="bold red")
                elif choice == '2':
                    task['details'] = console.input("Enter new task details: ")
                    save_data(load_data(PROJECTS_FILE), PROJECTS_FILE)
                    console.print("Task details updated successfully.", style="bold green")
                elif choice == '3':
                    new_priority = console.input("Enter new task priority (CRITICAL, HIGH, MEDIUM, LOW): ").strip().upper()
                    if new_priority in Priority.__members__:
                        task['priority'] = Priority[new_priority].value
                        save_data(load_data(PROJECTS_FILE), PROJECTS_FILE)
                        console.print("Task priority updated successfully.", style="bold green")
                    else:
                        console.print("Invalid priority.", style="bold red")
                elif choice == '4':
                    new_status = console.input("Enter new task status (BACKLOG, TODO, DOING, DONE, ARCHIVED): ").strip().upper()
                    if new_status in Status.__members__:
                        task['status'] = Status[new_status].value
                        project_name = console.input("Enter the project title to view tasks by status: ")
                        project_id = get_project_id_by_name(project_name)
                        edit_task(project_id,task_id,new_status)
                        save_data(load_data(PROJECTS_FILE), PROJECTS_FILE)
                    else:
                        console.print("Invalid status.", style="bold red")
                elif choice == '5':
                    add_comment_to_task(user)
                elif choice == '6':
                    return
                else:
                    console.print("Invalid choice. Please try again.", style="bold red")
            else :
                console.print("You are not the leader of this project.", style="bold red")
            return

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
            view_task_details(user, project, task_id)
            return
    console.print("Project not found or you are not a member of this project.", style="bold red")

# Function to display user menu and handle actions
def user_menu(user):
    while True:
        console.print("\n1. Add a new project", style="bold")
        console.print("2. List projects that you are leading", style="bold")
        console.print("3. List projects you are a member of", style="bold")
        if user['role'] == 'manager':
            console.print("4. Deactivate a user account", style="bold")
            console.print("5. Exit", style="bold")
        else:
            console.print("4. Exit", style="bold")
        choice = console.input("Choose an option: ")
        if choice == '1':
            add_project(user['username'])
        elif choice == '2':
            list_projects(user)
        elif choice == '3':
            list_projects_as_member(user)
        elif choice == '4' and user['role'] == 'manager':
            deactivate_user()
        elif choice == '4' or (choice == '5' and user['role'] == 'manager'):
            console.print("Exiting the program.", style="bold green")
            break
        else:
            console.print("Invalid choice. Please try again.", style="bold red")

    
    
    # Function to delete expired projects
def delete_expired_projects():
    projects = load_data(PROJECTS_FILE)
    current_time = datetime.now().replace(microsecond=0)
    # Ensure that each project has an 'end_time' key before comparing
    projects = [project for project in projects if 'end_time' in project and datetime.fromisoformat(project['end_time']) > current_time]
    save_data(projects, PROJECTS_FILE)
    
# Main function to handle user interaction
def main():
    delete_expired_projects()  # Delete expired projects at the start
    while True:
        console.print("\nWelcome to the Project Management System", style="bold blue")
        console.print("1. Create a new account", style="bold")
        console.print("2. Log in to your account", style="bold")
        console.print("3. Exit", style="bold")
        choice = console.input("Please choose an option (1, 2, or 3): ").strip()
        if choice == '1':
            username = console.input("Please enter your username: ")
            password = console.input("Please enter your password: ")
            email = console.input("Please enter your email: ")
            is_manager_input = console.input("Are you a manager? (yes/no): ").strip().lower()
            is_manager = is_manager_input == 'yes'
            if create_account(username, password, email, is_manager):
                user = login(username, password)
                if user:
                    user_menu(user)
        elif choice == '2':
            username = console.input("Please enter your username: ")
            password = console.input("Please enter your password: ")
            user = login(username, password)
            if user:
                user_menu(user)
        elif choice == '3':
            console.print("Exiting the program.", style="bold green")
            break
        else:
            console.print("Invalid choice. Please choose 1, 2, or 3.", style="bold red")

if __name__ == '__main__':
    main()
