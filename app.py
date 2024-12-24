from flask import Flask, render_template, redirect, request, url_for, flash, send_file, Response
from models import db, Transaction, User
from datetime import datetime
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import plotly.graph_objects as go
import pandas as pd
import secrets
import io
# from flask_migrate import Migrate


app = Flask(__name__)


# Настройка логина
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# Настройки бд, и др.
app.config['SQLALCHEMY_DATABASE_URI'] = 'Postgre'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.secret_key = secrets.token_hex(16)


db.init_app(app)
# migrate = Migrate(app, db)


# Логин
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Регистрация пользователей
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


# Логин пользователей
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


# Выход из системы
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Главная страница
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


# Таблица
@app.route('/table')
@login_required
def table():
    transactions = Transaction.query.filter_by(user_id = current_user.id).order_by(Transaction.date_added.desc()).all()
    return render_template('table.html', transactions = transactions)


# Страница с диграммами
@app.route('/dashboard')
def chart():
    transactions = Transaction.query.filter_by(user_id = current_user.id).order_by(Transaction.date_added.desc()).all()

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

# Старница экспорта
@app.route('/export')
def export_page():
    return render_template('export.html')


# Функция для экспорта данных в csv
@app.route('/export/csv')
def csv_export():
    transactions = Transaction.query.filter_by(user_id = current_user.id).order_by(Transaction.date_added.desc()).all()

    data = [
        {
            'ID': transaction.id,
            'Category': transaction.category,
            'Status': transaction.status,
            'Name': transaction.name,
            'Amount': transaction.amount,
            'Description': transaction.description,
            'Date': transaction.date_added.strftime('%Y-%m-%d %H:%M:%S'),
        } for transaction in transactions
    ]

    df = pd.DataFrame(data)

    buffer = io.StringIO()
    df.to_csv(buffer, index = False)
    buffer.seek(0)

    return Response(
        buffer,
        mimetype =  'text/csv',
        headers = {'Content-Disposition': f'attachment;filename={current_user.username}_transactions.csv'}
    )

# Функция для импорта данных в Excel
@app.route('/export/xlsx')
def xlsx_export():
    transactions = Transaction.query.filter_by(user_id = current_user.id).order_by(Transaction.date_added.desc()).all()

    try:
        data = [
            {
                'ID': transaction.id,
                'Category': transaction.category,
                'Status': transaction.status,
                'Name': transaction.name,
                'Amount': transaction.amount,
                'Description': transaction.description,
                'Date': transaction.date_added.strftime('%Y-%m-%d %H:%M:%S'),
            } for transaction in transactions
        ]
        
        df = pd.DataFrame(data)

        income = df[df['Status'] == 'Income']
        outcome = df[df['Status'] == 'Outcome']

        categories = db.session.query(Transaction.category).distinct().all()
        categories = [category[0] for category in categories]

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine = 'openpyxl') as writer:
            df.to_excel(writer, index = False, sheet_name = 'Transactions')

            if not income.empty:
                income.to_excel(writer, index = False, sheet_name = 'Доходы')

            if not outcome.empty:
                outcome.to_excel(writer, index = False, sheet_name = 'Расходы')

            if categories != []:
                for category in categories:
                    by_categories = df[df['Category'] == category]
                    by_categories.to_excel(writer, index = False, sheet_name = category)


        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment = True,
            download_name = f'{current_user.username}_transactions.xlsx',
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except:
        return render_template('export.html')


@app.route('/tracking')
def tracking():
    transactions = Transaction.query.filter_by(user_id = current_user.id).order_by(Transaction.date_added.desc()).all()
    
    # Сортировка по категориям
    categories = db.session.query(Transaction.category).distinct().all()
    categories = [category[0] for category in categories]
    
    categories = [
        {
        category: []
        }
        for category in categories
    ]

    for transaction in transactions:
        for category in categories:
            if transaction.category in category:
                category[transaction.category].append(transaction)

    # Сортировка по статусу
    status = {
            'Income': [],
            'Outcome': []
        }

    for transaction in transactions:
        if transaction.status == 'Income':
            status['Income'].append(transaction)
        else:
            status['Outcome'].append(transaction)


    return render_template('tracking.html', categories = categories, status = status)


if __name__ == '__main__':
    app.run(debug = True)
