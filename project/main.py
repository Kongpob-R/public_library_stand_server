import os
from re import T
from dotenv import load_dotenv
from flask import Flask, Blueprint, render_template, request
from flask_sock import Sock
import requests
from sqlalchemy import or_
from . import db
from .models import Book

main = Blueprint('main', __name__)
imageSrc = 'http://syndetics.com/index.aspx/?isbn={0}/LC.gif&client=iiit&type=hw7'
app = Flask(__name__)
sock = Sock(app)


@main.route('/')
def index():
    keyword = request.args.get('keyword', default='', type=str)
    # request.form.get('catagory')
    books = []
    if len(keyword) > 2:
        matchBooks = db.session.query(Book).filter(
            or_(
                Book.best_title_norm.like(keyword),
                Book.best_author_norm.like(keyword)
            )
        )
    for book in matchBooks.all():
        books.append({'book': book, 'imageSrc': imageSrc.format(book.isbn)})
    return render_template(
        'index.html',
        books=books
    )


@main.route('/details/<bibidVerify>')
def details(bibidVerify):
    book = db.session.query(Book).filter_by(bib_record_id=bibidVerify).first()
    return render_template(
        'details.html',
        imageSrc=imageSrc.format(book.isbn),
        book=book
    )


@sock.route('/connection/<ereaderuid>')
def connection(ws):
    while True:
        data = ws.receive()
        ws.send(data)


@main.route('/download/<bibidVerify>')
def download(bibidVerify):
    book = db.session.query(Book).filter_by(record_id=bibidVerify).first()
    return 'start downloading'


@main.route('/importbooks')
def importbooks():
    ebookList = requests.get(
        os.getenv('API_GET_LIST_OF_EBOOK'),
        proxies={'http': os.getenv('PROXY_HTTP')}
    ).json()
    db.session.query(Book).delete()
    for book in ebookList['ListOfEbookAtLocal']:
        newBook = Book(
            record_id=book["record_id"]+book["varfield_id"],
            varfield_id=book["varfield_id"],
            marc_tag=book["marc_tag"],
            marc_ind1=book["marc_ind1"],
            marc_ind2=book["marc_ind2"],
            occ_num=book["occ_num"],
            display_order=book["display_order"],
            tag=book["tag"],
            content=book["content"],
            id=book["id"],
            bib_record_id=book["bib_record_id"],
            best_title=book["best_title"],
            bib_level_code=book["bib_level_code"],
            material_code=book["material_code"],
            publish_year=book["publish_year"],
            best_title_norm=book["best_title_norm"],
            best_author=book["best_author"],
            best_author_norm=book["best_author_norm"],
        )
        db.session.add(newBook)
    db.session.commit()
    return 'import books finishs'


@main.route('/importisbn')
def importisbn():
    getIsbnByBibidUrl = os.getenv('API_GET_ISBN_BY_BIBID')
    for book in db.session.query(Book).filter_by(isbn=None).all():
        isbn = requests.get(
            getIsbnByBibidUrl + book.bib_record_id,
            proxies={'http': os.getenv('PROXY_HTTP')}
        ).json()
        if len(isbn['ISBN']) > 0:
            isbn = isbn['ISBN'][0]['content']
        else:
            isbn = None
        book.isbn = isbn
    db.session.commit()
    return 'import books isbn finishs'
