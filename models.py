from flask_sqlalchemy import SQLAlchemy
import datetime

db =SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    category = db.Column(db.String(100), nullable = False)
    date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    description = db.Column(db.String, nullable = False)
    status = db.Column(db.String(100), nullable = False)
    amount = db.Column(db.Integer, nullable = False)
