from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Book(db.Model):
    record_id = db.Column(db.String(20), primary_key=True)
    varfield_id = db.Column(db.String(10))
    marc_tag = db.Column(db.String(10))
    marc_ind1 = db.Column(db.String(10))
    marc_ind2 = db.Column(db.String(10))
    occ_num = db.Column(db.Integer)
    display_order = db.Column(db.Integer)
    tag = db.Column(db.String(5))
    content = db.Column(db.String(300))
    id = db.Column(db.Integer(10))
    bib_record_id = db.Column(db.String(20))
    best_title = db.Column(db.String(200))
    bib_level_code = db.Column(db.String(5))
    material_code = db.Column(db.String(5))
    publish_year = db.Column(db.Integer)
    best_title_norm = db.Column(db.String(200))
    best_author = db.Column(db.String(100))
    best_author_norm = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
