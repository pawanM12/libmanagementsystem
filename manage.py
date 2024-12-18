# Function to load users
def load_users():
    with open('database/users.json', 'r') as file:
        return json.load(file)

# Function to register a user
def register_user(username, email):
    users = load_users()
    new_user = {
        "username": username,
        "email": email,
        "borrowed_books": []
    }
    users.append(new_user)
    with open('database/users.json', 'w') as file:
        json.dump(users, file)
