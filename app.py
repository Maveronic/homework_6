from flask import Flask, request, jsonify, render_template
import bcrypt
import json
import os


app = Flask(__name__)
USER_FILE = 'users.txt'

# Function that loads the list of registered users
def get_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'W') as f:
            json.dump({}, f)
    with open(USER_FILE, 'r') as f:
        return json.load(f)

# Function that saves a new user in the database(text file)
def save_user(user):
    with open(USER_FILE, 'w') as f:
        json.dump(user, f)

# Function to hash a password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Function to check a password against a hash
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Validate the user by email and password
def validate_user(email, password):
    if not password:  # Check if the password is None or empty
        return False

    users = get_users()
    if email in users and check_password(password, users[email].get('password', '')):
        return True
    return False


# Utility function to sanitize user data
def sanitize_user_data(user):
    sanitized = user.copy()  # Make a copy to avoid modifying the original
    sanitized.pop('password', None)  # Remove the password field if it exists
    return sanitized


# Routes
@app.route('/')
def home():
    return "This is the homepage for the first homework."

# Form Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        age = request.form['age']
        password = request.form['password']

        users = get_users()
        if email in users:
            return render_template('register.html', message="User already exists.", success=False)

        hashed_password = hash_password(password)  # Hash the password
        users[email] = {"email": email, "age": age, "password": hashed_password}
        save_user(users)

        return render_template('register.html', message="User registered successfully!", success=True)
    
    # Display the form without a message
    return render_template('register.html')

# API endpoint to add a user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    email = data.get('email')
    age = data.get('age')
    password = data.get('password')

    if not email or not age or not password:
        return jsonify({"error": "Email, age, and password are required."}), 400

    users = get_users()
    if email in users:
        return jsonify({"error": "User already exists."}), 400

    hashed_password = hash_password(password)  # Hash the password
    users[email] = {"email": email, "age": age, "password": hashed_password}
    save_user(users)
    return jsonify({"message": "User registered successfully!"}), 201


# API to get a user
@app.route('/get_user/<email>', methods=['GET'])
def get_user(email):
    users = get_users()

    # Check if the user exists
    if email not in users:
        return jsonify({"error": "User not found"}), 404

    # Validate the password
    password = request.headers.get('Password')
    if not password or not validate_user(email, password):
        return jsonify({"error": "Unauthorized access."}), 403

    # Return sanitized user data
    sanitized_user = sanitize_user_data(users[email])
    return jsonify(sanitized_user), 200



# API endpoint to update a user
@app.route('/update_user/<email>', methods=['PUT'])
def update_user(email):
    password = request.headers.get('Password')
    if not validate_user(email, password):
        return jsonify({"error": "Unauthorized access."}), 403

    data = request.json
    users = get_users()
    if email not in users:
        return jsonify({"error": "User not found"}), 404

    users[email].update(data)
    save_user(users)

    # Optionally return sanitized user data
    sanitized_user = sanitize_user_data(users[email])
    return jsonify({"message": "User updated successfully!", "user": sanitized_user}), 200


# API endpoint to delete a user
@app.route('/delete_user/<email>', methods=['DELETE'])
def delete_user(email):
    password = request.headers.get('Password')

    # Validate the password first, even if the user does not exist
    if not password or not validate_user(email, password):
        return jsonify({"error": "Unauthorized access."}), 403

    users = get_users()

    # Check if the user exists
    if email not in users:
        return jsonify({"error": "User not found"}), 404

    # Delete the user
    del users[email]
    save_user(users)
    return jsonify({"message": "User deleted successfully!"}), 200


if __name__ == '__main__':
    app.run(debug=False)
