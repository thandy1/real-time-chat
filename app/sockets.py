from flask import request
from flask_socketio import emit, join_room, leave_room, send
from flask_login import current_user, login_required
from . import socketio
from .database import get_database_connection
from datetime import datetime


@socketio.on("join")
def on_join(data):
    """This function allows the user to join a room through the server and
    send the room's message history data to the client to parse and display to the user who made the request. 
    Additionally, the function will emit status messages for all users in the given room to see when a new user joins the room. """
    room_id = data["room_id"]
    join_room(room_id)
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
            """, (room_id,)
        )
        room_history = db_cursor.fetchall()
    if room_history:
        # Serialize Row objects in room_history into a list of dictionaries.
        history = [dict(row) for row in room_history]
        emit("room_history", {"messages": history}, to=request.sid)
   
    # Send a status message to all users in the given room when a new user joins the room.
    emit("status", {"message": f"{current_user.username} has joined the room"}, to=room_id)


@socketio.on("leave")
def on_leave(data):
    """This function allows the user to leave a room through the server and
    emits a status message to all users in the given room that the user left the room."""
    room_id = data["room_id"]
    leave_room(room_id)
    emit("status", {"msg": f"{current_user.username} has left the room."}, to=room_id)


@socketio.on("message")
def send_message(data):
    """Client sends the user's message and room id of origin to the server.
    The server saves the message's data to the database creating a new row
    in the messages table. The server emits the given message and its data
    back to the client to display to all user's in the given room."""
    message_content = data["message_content"]
    room_id = data["room_id"]
    # For the, emit so no need for an extra query since the 
    # DB (SQLite) automatically fills the timestamp column in messages table.
    timestamp = datetime.now().strftime("%d-%m-%Y, %I:%M %p")   
    with get_database_connection() as database_connection:
        db_cursor = database_connection.cursor()
        db_cursor.execute(
            """
            INSERT INTO messages (user_id, room_id, 
            message_content) 
            VALUES (?, ?, ?)
            """, (current_user.user_id, room_id, message_content)
        )
    emit("send_message", 
         {"message_content": message_content, "username": f"{current_user.username}", "timestamp": timestamp}, 
         to=room_id)


# NOTE: Come back to this issue once the frontend interface is working.
# - Client cant emit to the disconnected user because they are already gone.
# - Dont know which room they were in unless you track it explicitly.
@socketio.on("disconnect")
def on_disconnect():
    """This function executes automatically when a user closes the browser or
    loses connection."""
    print(f"{current_user.username} disconnected")