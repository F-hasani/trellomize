import argparse
import json
import os
import base64

# Define the path to the admin data file
ADMIN_FILE = 'admin.json'
DATA_FILE = 'users.json'
PROJECTS_FILE = 'projects.json'

def encode_password(password):
    """Encode the password using base64."""
    return base64.b64encode(password.encode('utf-8')).decode('utf-8')

def create_admin(username, password):
    """Create an admin account and save it to a JSON file."""
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'r') as file:
            admins = json.load(file)
            if any(admin['username'] == username for admin in admins):
                print("Error: An admin with this username already exists.")
                return

    # Encode the password
    encoded_password = encode_password(password)
    
    # Create admin data
    admin_data = {
        'username': username,
        'password': encoded_password
    }
    
    # Save the admin data to the file
    if not os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'w') as file:
            json.dump([admin_data], file, indent=4)
    else:
        with open(ADMIN_FILE, 'r+') as file:
            data = json.load(file)
            data.append(admin_data)
            file.seek(0)
            json.dump(data, file, indent=4)

    print("Admin account created successfully.")

def purge_data():
    """Purge all data from the system."""
    response = input("Are you sure you want to delete all data? (yes/no): ")
    if response.lower() == 'yes':
        if os.path.exists(ADMIN_FILE):
            os.remove(DATA_FILE)
            os.remove(PROJECTS_FILE)
            
            print("All data has been deleted successfully.")
        else:
            print("No data found to delete.")
    else:
        print("Data deletion canceled.")

def main():
    parser = argparse.ArgumentParser(description="Manage admin accounts for the system.")
    parser.add_argument("command", choices=['create-admin', 'purge-data'], help="Command to execute")
    parser.add_argument("--username", help="Username for the admin")
    parser.add_argument("--password", help="Password for the admin")
    
    args = parser.parse_args()
    
    if args.command == 'create-admin':
        if args.username and args.password:
            create_admin(args.username, args.password)
        else:
            print("Username and password are required for creating an admin.")
    elif args.command == 'purge-data':
        purge_data()

if __name__ == '__main__':
    main()
