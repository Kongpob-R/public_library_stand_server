import os
from flask import Blueprint, current_app, render_template, request
from flask_login import current_user
import requests
from sqlalchemy import or_
from . import db
from .models import Book, Ereader
from .lccCode import lccCode, lccCodelong

main = Blueprint('main', __name__)
imageSrc = 'http://syndetics.com/index.aspx/?isbn={0}/LC.gif&client=iiit&type=hw7'


@main.route('/')
def index():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    keyword = request.args.get('keyword', default='', type=str)
    category = request.args.get('category', default='', type=str)
    matchBooks = []
    booksCount = 0

    if len(keyword) > 2 and len(category) == 0:
        matchBooks = db.session.query(Book).filter(
            Book.best_title_norm.contains(keyword) |
            Book.best_author_norm.contains(keyword) |
            Book.subject.contains(keyword)
        )
        booksCount = matchBooks.count()
        matchBooks = matchBooks.all()

    elif len(keyword) == 0 and len(category) > 0:
        matchCode = []
        for code, meaning in lccCodelong.items():
            if meaning == category:
                matchCode.append(code)
        for code in matchCode:
            booksCount += db.session.query(Book).filter(
                Book.lc_callno.startswith(code)
            ).count()
            matchBooks += db.session.query(Book).filter(
                Book.lc_callno.startswith(code)
            ).limit(500).all()

    elif len(keyword) > 2 and len(category) > 2:
        matchCode = []
        for code, meaning in lccCodelong.items():
            if meaning == category:
                matchCode.append(code)
        for code in matchCode:
            match = db.session.query(Book).filter(
                Book.best_title_norm.contains(keyword) |
                Book.best_author_norm.contains(keyword) |
                Book.subject.contains(keyword)
            ).filter(
                Book.lc_callno.startswith(code)
            )
            booksCount += match.count()
            matchBooks += match.all()

    for book in matchBooks:
        book.imageSrc = imageSrc.format(book.isbn)

    return render_template(
        'index.html',
        navbar=True,
        lccCode=lccCode,
        ereaders=Ereader.query.all(),
        keyword=keyword,
        category=category,
        books=matchBooks,
        booksCount=booksCount
    )


@main.route('/detail')
def detail():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    record_id = request.args.get('record_id', default='', type=str)
    book = db.session.query(Book).filter_by(record_id=record_id).first()
    if book == None:
        return 'Book details not found'
    return render_template(
        'detail.html',
        navbar=True,
        lccCode=lccCode,
        ereaders=Ereader.query.all(),
        imageSrc=imageSrc.format(book.isbn),
        book=book,
    )


@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if current_user.role != 'superuser':
        return current_app.login_manager.unauthorized()
    if request.method == 'POST':
        selectBooks = (request.form.getlist('select-book'))
        selectAction = (request.form.get('select-action'))
        print(selectAction)
        for selectbook in selectBooks:
            book = db.session.query(Book).filter_by(
                record_id=selectbook).first()
            if selectAction == 'addPredownload':
                book.predownload = True
            elif selectAction == 'removePredownload':
                book.predownload = False
            elif selectAction == 'addRecommend':
                book.recommend = True
            elif selectAction == 'removeRecommend':
                book.recommend = False
        if selectAction == 'clearPredownload':
            Book.query.update({Book.predownload: False})
        elif selectAction == 'clearRecommend':
            Book.query.update({Book.recommend: False})
        db.session.commit()
    ereader = Ereader.query.all()
    books = Book.query.limit(50).all()
    return render_template(
        'dashboard.html',
        dashboard=True,
        ereader=(ereader),
        books=books
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


@main.route('/import_missing_detail')
def importlccallno():
    getMarc21ByBibid = os.getenv('API_GET_MARC21_BY_BIBID')
    missingDetailBooks = db.session.query(Book).filter(
        or_(
            Book.isbn == None,
            Book.edition == None,
            Book.summary == None,
            Book.subject == None,
            Book.lc_callno == None,
            Book.imprint == None
        )
    ).all()
    for book in missingDetailBooks:
        marc21 = requests.get(
            getMarc21ByBibid + book.bib_record_id,
            proxies={'http': os.getenv('PROXY_HTTP')}
        ).json()
        if len(marc21['BibMarc21']) > 0:
            imprint = []
            subject = []
            for marc in marc21['BibMarc21']:
                if marc['marc_tag'] == '020' and marc['occ_num'] == 0:
                    book.isbn = marc['content']
                if marc['marc_tag'] == '050' and marc['display_order'] == 0:
                    book.lc_callno = marc['content']
                if marc['marc_tag'] == '250' and marc['display_order'] == 0:
                    book.imprint = marc['content']
                if marc['marc_tag'] == '260':
                    imprint.append(marc['content'])
                if marc['marc_tag'] == '520' and marc['display_order'] == 0:
                    book.summary = marc['content']
                if marc['marc_tag'] == '650':
                    subject.append(marc['content'])

            book.imprint = ' '.join(imprint)
            book.subject = ' '.join(subject)
    db.session.commit()
    return 'import books details from MARC21 finishs'
