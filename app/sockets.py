from flask import Blueprint, request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user, login_required
from . import socketio
from .database import get_database_connection

sockets = Blueprint("sockets", __name__)

# Rooms
@socketio.on("join")
def on_join(data):
    """
    This function allows the user to join a room through the server and
    send room's message history data to the client to parse and display 
    to the user who made the request. Additionally, the function will emit status messages for all users in the given room to see when a new user joins the room. 
    """
    room = data["room_id"]
    join_room(room)
    # Retrieve message history of the given room.
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        db_cursor.execute(
            """
            SELECT messages.message_content, messages.message_timestamp, 
            messages.message_id, users.username 
            FROM messages 
            JOIN users ON messages.user_id = users.user_id
            WHERE messages.room_id = ?
            ORDER BY messages.message_timestamp ASC
            """, (room,)
        )
        room_history = db_cursor.fetchall()
    if room_history:
        # Serialize Row objects in room_history into a list of dictionaries.
        history = [dict(row) for row in room_history]
        emit("room_history", {"messages": history}, to=request.sid)
   
    # Send a status message to all users in the given room when a new user joins the room.
    emit("status", {"message": f"{current_user.username} has joined the room"}, to=room)

@socketio.on("leave")
def on_leave(data):
    """
   
    """
    room = data["room_id"]
    leave_room(room)
    emit("status", {"msg": f"{current_user.username} has left the room."}, to=room)

# Receiving Messages




# Sending Messages

# THIS IS A STUB FILE.