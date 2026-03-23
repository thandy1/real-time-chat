import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from dotenv import load_dotenv
from database import get_database_connection, initialize_database

# Load environment variables from .env file.
load_dotenv()

# Creates Flask application.
app = Flask(__name__)   

# Sets the secret key for session encryption so users cant tamper with session data.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  

# Initialize SocketIO for real-time communication.
socketio = SocketIO(app)

# Creates a login manager that handles user sessions.
login_manager = LoginManager()  
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated.

# Initialize database on first run.
initialize_database()  

class User:
    """Represents a logged-in user to check user status."""
    def __init__(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    # May need to override this if needed.
    def get_id(self):
        """Returns the user ID that gets stored in the session cookie."""
        return str(self.user_id)

@login_manager.user_loader  
def load_user(user_id):
    """
    Loads a User object from the database using the user_id stored in the session cookie.
    This runs automatically on every request where a user is logged in.
    """
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        db_cursor.execute(
            '''SELECT user_id, username, email FROM users where user_id = ?''', (user_id,)
        )
        # Fetch the user's data (id, username, email, password_hash)
        user_row = db_cursor.fetchone()
        # Check if user_row exists
        if user_row:
            return User(
                user_row['user_id'], 
                user_row['username'], 
                user_row['email']
                )
        return None
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    GET: Display registration form.
    POST: Process form submission, hash password, insert new user into database.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password') or ''
        hashed_password = generate_password_hash(password) 
        # Try to insert the form data into the database.
        try:
            with get_database_connection() as database_connection:
                db_cursor = database_connection.cursor()
                db_cursor.execute(
                    '''INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)''', (username, email, hashed_password)
                )
        except sqlite3.IntegrityError:
            flash("Username already exists,", "error")
        else:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

    # If 'GET' or flash error, render the template.
    return render_template('auth/register.html')

@app.route('/login', methods=["POST", "GET"])
def login():
    """
    Handle user authentication.
    GET: Render the login form.
    POST: Query database for user, verify password hash, create session with login_user().
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') or ''
        with get_database_connection() as database_connection:
            db_cursor = database_connection.cursor()
            db_cursor.execute(
                '''SELECT user_id, username, email, password_hash FROM users WHERE username = ?
                ''', (username,)
            )
            # Fetch the user's data (id, username, email, password_hash)
            user_row = db_cursor.fetchone()
            # Check if user_row exists
            if user_row and check_password_hash(user_row['password_hash'], password):
                    # Password correct - log them in.
                    user = User(
                        user_row['user_id'],
                        user_row['username'],
                        user_row['email']
                    )
                    login_user(user)
                    return redirect(url_for('home'))    
            else:
                # Either user doesn't exist OR password is wrong.
                flash("Invalid username or password", 'error')

    # If 'GET' or flash error, render the template.
    return render_template('auth/login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("home"))    

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/create_room", methods=["POST", "GET"])
@login_required
def create_room():
    """
    Handles Creating a Room.
    GET: Render the create_room template.
    POST: Retrieve the room-name from the form, insert room_name as a column into rooms table in DB, redirect to room_list.
    """
    if request.method == "POST":
        room_name = request.form.get('room-name')
        try:
            with get_database_connection() as database_connection:
                db_cursor = database_connection.cursor()
                db_cursor.execute(
                    '''INSERT INTO rooms (room_name) VALUES (?)
                    ''', (room_name,)
                )
        # Catch integrity error for duplicate room names.
        except sqlite3.IntegrityError:
            flash("Room Name already exists,", "error")
        else:
            flash("Room Creation Successful!", "success")
            return redirect(url_for("rooms_list"))
    
    return render_template("rooms/create_room.html")
    
@app.route("/rooms_list")
@login_required
def rooms_list():
    '''
    List the rooms that currently exist.
    '''
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        # Query database for each column list in rooms table and order in descending order.
        db_cursor.execute(
            '''SELECT room_id, room_name, created_at FROM rooms ORDER BY created_at DESC'''
        )
        rooms = db_cursor.fetchall()    # Get all rows
        return render_template("rooms/rooms_list.html", rooms=rooms)



if __name__ == '__main__':
    socketio.run(app, debug=True)

