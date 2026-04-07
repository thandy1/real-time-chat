import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_database_connection
from .models import User

# Create blueprint, no app import needed.
routes = Blueprint('routes', __name__)

@routes.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration.
    GET: Display registration form.
    POST: Process form submission, hash password, insert new user into database."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password') or ''
        hashed_password = generate_password_hash(password) 
        try:
            with get_database_connection() as database_connection:
                db_cursor = database_connection.cursor()
                db_cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)
                    """, (username, email, hashed_password)
                )
        # Handle potential integrity errors (like duplicate username or email) 
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower():
                flash("Username already exists.", "error")
            elif "email" in str(e).lower():
                flash("Email already exists.", "error")
            else:
                flash("Registration failed. Please try again.", "error")
        else:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('.login'))

    return render_template('auth/register.html')


@routes.route('/login', methods=["POST", "GET"])
def login():
    """Handle user login.
    GET: Display login form.
    POST: Process form submission, verify password, log user in if successful."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') or ''
        with get_database_connection() as database_connection:
            db_cursor = database_connection.cursor()
            db_cursor.execute(
                """
                SELECT user_id, username, email, password_hash FROM users WHERE username = ?
                """, (username,)
            )
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
                    return redirect(url_for('.home'))    
            else:
                flash("Invalid username or password", 'error')

    return render_template('auth/login.html')


@routes.route("/logout")
@login_required
def logout():
    """"Handle user logout by clearing the session and redirecting to the home page."""
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for(".home"))    


@routes.route("/")
@login_required
def home():
    """Render the home page. This is a protected route that requires the user to be logged in."""
    return render_template("index.html")


@routes.route("/create_room", methods=["POST", "GET"])
@login_required
def create_room():
    """Handle the creation of new chat rooms.
    GET: Render the form to create a new room.
    POST: Process the form submission, insert new room into database, handle duplicate room names."""
    if request.method == "POST":
        room_name = request.form.get('room-name')
        try:
            with get_database_connection() as database_connection:
                db_cursor = database_connection.cursor()
                db_cursor.execute(
                    """
                    INSERT INTO rooms (room_name) VALUES (?)
                    """, (room_name,)
                )
        except sqlite3.IntegrityError:
            flash("Room Name already exists,", "error")
        else:
            flash("Room Creation Successful!", "success")
            return redirect(url_for(".rooms_list"))
    
    return render_template("rooms/create_room.html")
    

@routes.route("/rooms_list")
@login_required
def rooms_list():
    """Handles Displaying the List of Rooms.
    Queries the database for all rooms, orders them by creation date in descending order, 
    and renders the rooms_list template with the retrieved rooms data."""
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        db_cursor.execute(
            '''SELECT room_id, room_name, created_at FROM rooms ORDER BY created_at DESC'''
        )
        rooms = db_cursor.fetchall()    
        return render_template("rooms/rooms_list.html", rooms=rooms)


@routes.route("/chat/<int:room_id>")
@login_required
def chat(room_id):
    """Handles Displaying the Chat Room."""
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        # Fetch the room details
        db_cursor.execute(
            '''SELECT * FROM rooms WHERE room_id = ?''', (room_id,)
        )
        room = db_cursor.fetchone()
        if not room:
            flash("Room not found.", "error")
            return redirect(url_for(".rooms_list"))
        # Fetch the messages for the room along with the username of the sender
        db_cursor.execute(
            """
            SELECT messages.message_id, messages.message_content, messages.message_timestamp, users.username
            FROM messages
            JOIN users ON messages.user_id = users.user_id
            WHERE messages.room_id = ?
            ORDER BY messages.message_timestamp ASC
            """, (room_id,)
        )
        messages = db_cursor.fetchall()
        return render_template("rooms/chat.html", room=room, messages=messages)

  
      