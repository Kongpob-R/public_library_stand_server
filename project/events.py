from flask_socketio import emit
from . import socketio, db
from .models import Book


@socketio.on('get_download_url')
def handle_get_download_url(json):
    book = db.session.query(Book).filter_by(
        record_id=json['record_id']).first()
    json = {
        'ereaderuid': json['ereaderuid'],
        'url': book.content
    }
    print(json)
    emit('download', json)


@socketio.on('status_req')
def status_req():
    emit('status_req')


@socketio.on('status_res')
def status_res(json):
    emit('status_res', json)
