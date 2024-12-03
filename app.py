from flask import Flask, render_template, redirect, request, url_for
from models import db, Transaction
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finances.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/')
def index() -> render_template:
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('index.html', transactions = transactions)


if __name__ == '__main__':
    app.run(debug = True)