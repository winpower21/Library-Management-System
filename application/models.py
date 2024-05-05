from .database import *
from datetime import date, timedelta

class User(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(), nullable = False, unique = True)
    name = db.Column(db.String(), default="")
    password = db.Column(db.String(), nullable = False)
    type = db.Column(db.String(), default = 'user')
    u_request = db.relationship('Requests', cascade="all,delete", backref = 'user')
    u_purchase = db.relationship('Purchases', cascade="all,delete", backref = 'user')
    
@whooshee.register_model('name','author','description','section')
class Books(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique = True)
    author = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    section = db.Column(db.String(), db.ForeignKey('sections.name'))
    price = db.Column(db.Integer(), default=0)
    cover = db.Column(db.String(), nullable = False)
    location = db.Column(db.String(), nullable = False, unique = True)
    requests = db.relationship('Requests',cascade="all,delete", backref = 'book')
    b_reviews = db.relationship('Reviews',cascade="all,delete", backref = 'book')

class Sections(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(), nullable = False, unique = True)
    date_created = db.Column(db.Date(), default = date.today())
    description = db.Column(db.String())

class Requests(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer(), db.ForeignKey('books.id'))
    from_date = db.Column(db.Date(), default=date.today())
    to_date = db.Column(db.Date(), nullable = True, default = date.today()+timedelta(7))
    status = db.Column(db.String(), default='To be Updated')
    
class Reviews (db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer(), db.ForeignKey('books.id'))
    rating = db.Column(db.Integer(), nullable = False)
    review = db.Column(db.String(), nullable = False)
    
class Purchases(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer(), db.ForeignKey('books.id'))
    purchase_date = db.Column(db.Date(), default=date.today())
    
