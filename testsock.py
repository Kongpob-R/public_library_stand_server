from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)


@app.route('/')
def index():
    return 'hello index'


@sock.route('/echo')
def echo(ws):
    while True:
        data = ws.receive()
        ws.send(data)


application = app
