import os
from dotenv import load_dotenv
from flask import Blueprint, render_template, request
from flask_socketio import emit
import requests
from sqlalchemy import or_
from . import db
from .models import Book

main = Blueprint('main', __name__)
imageSrc = 'http://syndetics.com/index.aspx/?isbn={0}/LC.gif&client=iiit&type=hw7'


@main.route('/')
def index():
    keyword = request.args.get('keyword', default='', type=str)
    # request.form.get('catagory')
    matchBooks = []
    if len(keyword) > 2:
        matchBooks = db.session.query(Book).filter(
            or_(
                Book.best_title_norm.contains(keyword),
                Book.best_author_norm.contains(keyword)
            )
        ).all()
    for book in matchBooks:
        book.imageSrc = imageSrc.format(book.isbn)
    return render_template(
        'index.html',
        keyword=keyword,
        books=matchBooks
    )


@main.route('/detail')
def detail():
    record_id = request.args.get('record_id', default='', type=str)
    book = db.session.query(Book).filter_by(record_id=record_id).first()
    if book == None:
        return 'Book details not found'
    return render_template(
        'detail.html',
        imageSrc=imageSrc.format(book.isbn),
        book=book,
    )


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
