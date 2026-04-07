import os
from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from a .env file. This allows us to keep sensitive information like the SECRET_KEY out of our source code.
load_dotenv()

# Create flask app instance. This is the core of our application where we will register routes, initialize extensions, and configure settings.
app = Flask(__name__)   

# Set the secret key for session management and CSRF protection. 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  

# Initialize SocketIO with the Flask app to enable real-time communication features.
socketio = SocketIO(app)

# Initialize Flask-Login's LoginManager to handle user authentication and session management. 
login_manager = LoginManager()  
login_manager.init_app(app)
login_manager.login_view = 'routes.login' 

# Extensions are set up, safe to import from our own modules now.
from .database import initialize_database, get_database_connection
from .models import User

@login_manager.user_loader  
def load_user(user_id):
    """
    On every request made by an authenticated user, flask-login will call this function to fetch the user_id from the session cookie and uses it to retrieve the full User object from the database. The returned
    User object is what flask-login exposes as current_user throughout
    the request.
    """
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        db_cursor.execute(
            '''SELECT user_id, username, email FROM users where user_id = ?''', (user_id,)
        )
        user_row = db_cursor.fetchone()
        # Check if a user was found and return a User object. If no user is found, return None.
        if user_row:
            return User(
                user_row['user_id'], 
                user_row['username'], 
                user_row['email']
                )
        return None

# Initialize the database by creating necessary tables if they don't exist. 
initialize_database()  

# Bottom imports prevent circular imports — must stay here
from .routes import routes   # registers all @routes.route() handlers
from . import sockets           # registers all @socketio.on() handlers

app.register_blueprint(routes)





