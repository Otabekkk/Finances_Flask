from flask import Flask, render_template, redirect, request, url_for, flash
from models import db, Transaction, User
from datetime import datetime
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import plotly.graph_objects as go
# from flask_migrate import Migrate


app = Flask(__name__)

# Настройка логина
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Настройки бд, и др.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ztw02@localhost:5432/Finances'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.secret_key = secrets.token_hex(16)

db.init_app(app)
# migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method = 'pbkdf2:sha256', salt_length=16)

        if User.query.filter_by(username = username).first():
            flash('Такой ник уже занят!')
            return redirect(url_for('register'))
        
        new_user = User(username = username, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')

        user = User.query.filter_by(username = username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Неправильный логин или пароль!')
            return redirect(url_for('login'))
    
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/')
@login_required
def index() -> render_template:
    transactions = Transaction.query.filter_by(user_id = current_user.id).order_by(Transaction.date_added.desc()).all()
    income = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.status == 'Income', Transaction.user_id == current_user.id).scalar() or 0
    outcome = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.status == 'Outcome', Transaction.user_id == current_user.id).scalar() or 0
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
        new_transaction = Transaction(status = status, category = category, name = name, amount = float(amount), description = description, date_added = date_added, user_id = current_user.id)
        
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


@app.route('/table')
@login_required
def table():
    transactions = Transaction.query.filter_by(user_id = current_user.id).order_by(Transaction.date_added.desc()).all()
    return render_template('table.html', transactions = transactions)


@app.route('/dashboard')
def chart():
    transactions = Transaction.query.all()

    categories = {}

    for transaction in transactions:
        if transaction.category not in categories:
            categories[transaction.category] = 0
        categories[transaction.category] += transaction.amount if transaction.status == 'Income' else -transaction.amount

    labels = list(categories.keys())
    values = list(categories.values())
    colors = ['#00FA9A' if value >= 0 else 'red' for value in values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x = labels,
        marker_color = colors,
        y = values,
        text = values,
        textposition = 'auto'
    ))

    fig.update_layout(
        title = "Income/Outcome by Category",
        xaxis_title = 'Categories',
        yaxis_title = 'Amount',
        template = 'plotly_white'
    )

    graph_html = fig.to_html(full_html = False)

    return render_template('dashboard.html', graph_html = graph_html)

if __name__ == '__main__':
    app.run(debug = True)