def encode_password(password):
    return base64.b64encode(password.encode('utf-8')).decode('utf-8')


def decode_password(encoded_password):
    return base64.b64decode(encoded_password.encode('utf-8')).decode('utf-8')
    
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
