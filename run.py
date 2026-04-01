from app import socketio, app

# Entry point for the application. Runs the Flask app with SocketIO support in debug mode.
if __name__ == '__main__':
    socketio.run(app, debug=True)