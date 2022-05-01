import os
from dotenv import load_dotenv
from flask import Blueprint, render_template, request
import requests
from . import db
from .models import Book

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/', methods=['POST'])
def index_post():
    request.form.get('keyword')
    # request.form.get('catagory')
    return render_template('index.html')


@main.route('/details/<bibid>')
def details(bibid):
    book = db.session.query(Book).filter_by(record_id=bibid).first()
    imageSrc = 'http://syndetics.com/index.aspx/?isbn={0}/LC.gif&client=iiit&type=hw7'
    return render_template(
        'details.html',
        imageSrc=imageSrc.format(book.isbn),
        book=book
    )


@main.route('/importbooks')
def importbooks():
    ebookList = requests.get(os.getenv('API_GET_LIST_OF_EBOOK')).json()
    getIsbnByBibidUrl = os.getenv('API_GET_ISBN_BY_BIBID')
    db.session.query(Book).delete()
    for book in ebookList['ListOfEbookAtLocal']:
        isbn = requests.get(getIsbnByBibidUrl + book.record_id).json()
        isbn = isbn['ISBN'][0]['content']
        newBook = Book(
            record_id=book.record_id,
            varfield_id=book.varfield_id,
            marc_tag=book.marc_tag,
            marc_ind1=book.marc_ind1,
            marc_ind2=book.marc_ind2,
            occ_num=book.occ_num,
            display_order=book.display_order,
            tag=book.tag,
            content=book.content,
            id=book.id,
            bib_record_id=book.bib_record_id,
            best_title=book.best_title,
            bib_level_code=book.bib_level_code,
            material_code=book.material_code,
            publish_year=book.publish_year,
            best_title_norm=book.best_title_norm,
            best_author=book.best_author,
            best_author_norm=book.best_author_norm,
            isbn=isbn
        )
        db.session.add(newBook)
    db.session.commit()
    return 'import books finishs'
