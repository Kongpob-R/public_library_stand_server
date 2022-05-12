from queue import Queue
from threading import Thread
import time
from flask import json
from . import sock, db
from .models import Book


queues = []


@sock.route('/socket')
def socket(ws):
    global queues
    queues.append(Queue())
    localQueue = queues[-1]

    def listenBoardcast():
        while True:
            if not localQueue.empty():
                data = localQueue.get()
                print('emit', data)
                ws.send(json.dumps(data))

    t1 = Thread(target=listenBoardcast)
    t1.start()

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
            print('add to queues', data)
            for q in queues:
                q.put(data)
        else:
            print('add to queues', data)
            for q in queues:
                q.put(data)
