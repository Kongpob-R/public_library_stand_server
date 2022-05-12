from flask import json
from . import sock, db
from .models import Book


@sock.route('/socket')
def socket(ws):
    while True:
        data = ws.receive()
        data = json.loads(data)
        if data['event'] == 'get_download_url':
            book = db.session.query(Book).filter_by(
                record_id=data['record_id']).first()
            data = {
                'event': 'download',
                'ereaderuid': data['ereaderuid'],
                'url': book.content
            }
        print(data)
        ws.send(json.dumps(data))
