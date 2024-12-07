from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db =SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(100), nullable = False)
    category = db.Column(db.String(100), nullable = False)
    name = db.Column(db.String(100), nullable = False)
    amount = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String, nullable = False)
    date_added = db.Column(db.DateTime, nullable = False, default = datetime.now)

    user_id = db.relationship('User', backref = 'user.id', lazy = True)
 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique = True, nullable = False)
    password = db.Column(db.String(150), nullable = False)

    transactions = db.relationship('Transaction', backref = 'user', lazy = True)