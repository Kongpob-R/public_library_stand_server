from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from . import db


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    ereaderuid = db.Column(db.String(100))
    role = db.Column(db.String(10))

    @classmethod
    def createsuperuser(cls, **kw):
        superuser = cls(**kw)
        superuser.role = 'superuser'
        superuser.password = generate_password_hash(
            superuser.password,
            method='sha256'
        )
        db.session.add(superuser)
        db.session.commit()

    @classmethod
    def createuser(cls, **kw):
        user = cls(**kw)
        user.password = generate_password_hash(
            user.password,
            method='sha256'
        )
        db.session.add(user)
        db.session.commit()


class Ereader(db.Model):
    ereaderuid = db.Column(db.String(30), primary_key=True)
    short_name = db.Column(db.String(20), unique=True)


class Book(db.Model):
    record_id = db.Column(db.String(30), primary_key=True)
    varfield_id = db.Column(db.String(10))
    marc_tag = db.Column(db.String(10))
    marc_ind1 = db.Column(db.String(10))
    marc_ind2 = db.Column(db.String(10))
    occ_num = db.Column(db.Integer)
    display_order = db.Column(db.Integer)
    tag = db.Column(db.String(5))
    content = db.Column(db.String(300))
    id = db.Column(db.Integer)
    bib_record_id = db.Column(db.String(20))
    best_title = db.Column(db.String(200))
    bib_level_code = db.Column(db.String(5))
    material_code = db.Column(db.String(5))
    publish_year = db.Column(db.Integer)
    best_title_norm = db.Column(db.String(200))
    best_author = db.Column(db.String(100))
    best_author_norm = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
    recommend = db.Column(db.Boolean)
    predownload = db.Column(db.Boolean)
