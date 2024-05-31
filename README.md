# trellomize
# Project Management System

This project is a project management system implemented using Python and various libraries such as `json`, `os`, `uuid`, `enum`, `rich`, `datetime`, `loguru`, `base64`, and `colorama`. This system allows users to manage their projects and tasks, add and remove team members, and update the status of tasks.

## Features

- **User Account Creation**: Users can create new accounts and log in to the system.
- **Project Management**: Users can create new projects, add and remove team members, and assign tasks to team members.
- **Task Management**: Users can create, edit, and update tasks.
- **Logging**: All activities in the system are logged and can be stored in a JSON file.
- **Automatic Deletion of Expired Projects**: Projects that have passed their end date are automatically deleted.

## Installation and Setup

1. Clone this repository:
    ```bash
    git clone https://github.com/username/project-management-system.git
    cd project-management-system
    ```

2. Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create the `app.log` file in the project directory:
    ```bash
    touch app.log
    ```

5. Run the application:
    ```bash
    python main.py
    ```

## Usage

After running the application, the main menu will be displayed, which includes options for creating a user account, logging in, and exiting the program. Once logged in, users can manage their projects and tasks.

## Project Structure

- `main.py`: The main file of the application that includes the main menu and functions for managing projects and tasks.
- `users.json`: File for storing user information.
- `projects.json`: File for storing project information.
- `app.log`: Log file for recording activities.

## Contributing

If you would like to contribute to this project, please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file.

## Authors

- [FatemeHasani](https://github.com/F-hasani)
- [FarhoodGH](https://github.com/FarhoodGH)
