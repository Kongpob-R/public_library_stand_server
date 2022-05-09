from project import create_app, socketio

application = create_app()

if __name__ == "main":
    socketio.run(application)
