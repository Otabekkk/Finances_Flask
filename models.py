from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db =SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(100), nullable = False)
    category = db.Column(db.String(100), nullable = False)
    name = db.Column(db.String(100), nullable = False)
    amount = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String, nullable = False)
    date_added = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

 
