from flask import Blueprint
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user, login_required
from . import socketio

sockets = Blueprint("sockets", __name__)
# Socket event handlers will go here


# THIS IS A STUB FILE.