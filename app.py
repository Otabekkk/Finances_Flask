from flask import Flask, render_template, redirect, request, url_for
from models import db, Transaction, User
from datetime import datetime
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import secrets


app = Flask(__name__)

# Настройка логина
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Настройки бд
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ztw02@localhost:5432/Finances'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def index() -> render_template:
    transactions = Transaction.query.order_by(Transaction.date_added.desc()).all()
    income = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.status == 'Income').scalar() or 0
    outcome = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.status == 'Outcome').scalar() or 0
    balance = income - outcome
    return render_template('index.html', transactions = transactions, balance = balance, income = income, outcome = outcome)



# Добавление транзакции
@app.route('/add', methods = ['GET', 'POST'])
def add_transaction():
    if request.method  == 'POST':
        status = request.form.get('status')
        category = request.form.get('category')
        name = request.form.get('name')
        amount = request.form.get('amount')
        description = request.form.get('description')
        date_added = datetime.now()
        new_transaction = Transaction(status = status, category = category, name = name, amount = float(amount), description = description, date_added = date_added)
        
        db.session.add(new_transaction)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('index.html')



# Редактирование транзакции
@app.route('/edit_transaction/<int:id>', methods = ['POST'])
def edit_transaction(id):
    transaction = Transaction.query.get(id)

    if not transaction:
        return 'Transaction not found!', 404
    
    transaction.status = request.form['status']
    transaction.category = request.form['category']
    transaction.name = request.form['name']
    transaction.amount = request.form['amount']
    transaction.description = request.form['description']
    transaction.date_added = datetime.now()

    db.session.commit()
    return redirect('/')
    


# Удаление транзакции
@app.route('/delete_transaction/<int:id>', methods = ['GET', 'POST', 'DELETE'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug = True)