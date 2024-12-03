from flask import Flask, render_template, redirect, request, url_for
from models import db, Transaction
from datetime import datetime
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ztw02@localhost:5432/Finances'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)

db.init_app(app)


@app.route('/')
def index() -> render_template:
    transactions = Transaction.query.order_by(Transaction.date_added.desc()).all()
    return render_template('index.html', transactions = transactions)


@app.route('/add', methods = ['POST'])
def add_transaction():
    status = request.form.get('status')
    category = request.form.get('category')
    name = request.form.get('name')
    amount = request.form.get('amount')
    description = request.form.get('description')
    date_added = datetime.utcnow()
    print(f"Name: {name}, Amount: {amount}, Category: {category}, Date Added: {date_added}")
    new_transaction = Transaction(status = status, category = category, name = name, amount = amount, description = description, date_added = date_added)

    db.session.add(new_transaction)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug = True)