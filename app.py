from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# Helper function to check if logged in
def is_logged_in():
    return 'user_id' in session

# Route: Home (redirect to dashboard or login)
@app.route('/')
def home():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = 'user'  # default role

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        if user:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s,%s,%s,%s)",
                    (name, email, hashed_pw, role))
        mysql.connection.commit()
        cur.close()

        flash('You are registered! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['role'] = user[4]
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out', 'success')
    return redirect(url_for('login'))

# Route: Dashboard
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    # Sum income and expenses
    cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id=%s AND type='income'", (user_id,))
    total_income = cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id=%s AND type='expense'", (user_id,))
    total_expense = cur.fetchone()[0] or 0
    balance = total_income - total_expense
    cur.close()
    return render_template('dashboard.html', income=total_income, expense=total_expense, balance=balance)

# Route: Add Transaction
@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if not is_logged_in():
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        ttype = request.form['type']
        description = request.form['description']
        date = request.form['date']

        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO transactions (user_id, amount, category, type, description, date) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (user_id, amount, category, ttype, description, date))
        mysql.connection.commit()
        cur.close()
        flash('Transaction added', 'success')
        return redirect(url_for('view_transactions'))

    return render_template('add_transaction.html')

# Route: View Transactions
@app.route('/transactions')
def view_transactions():
    if not is_logged_in():
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, amount, category, type, description, date FROM transactions WHERE user_id=%s ORDER BY date DESC", (user_id,))
    transactions = cur.fetchall()
    cur.close()
    return render_template('view_transactions.html', transactions=transactions)

# Route: Edit Transaction
@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        ttype = request.form['type']
        description = request.form['description']
        date = request.form['date']

        cur.execute("""UPDATE transactions SET amount=%s, category=%s, type=%s, description=%s, date=%s
                       WHERE id=%s AND user_id=%s""",
                    (amount, category, ttype, description, date, transaction_id, user_id))
        mysql.connection.commit()
        cur.close()
        flash('Transaction updated', 'success')
        return redirect(url_for('view_transactions'))

    # GET method: show current data
    cur.execute("SELECT id, amount, category, type, description, date FROM transactions WHERE id=%s AND user_id=%s",
                (transaction_id, user_id))
    transaction = cur.fetchone()
    cur.close()
    if not transaction:
        flash('Transaction not found or access denied', 'danger')
        return redirect(url_for('view_transactions'))

    return render_template('edit_transaction.html', transaction=transaction)

# Route: Delete Transaction
@app.route('/delete/<int:transaction_id>')
def delete_transaction(transaction_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM transactions WHERE id=%s AND user_id=%s", (transaction_id, user_id))
    mysql.connection.commit()
    cur.close()
    flash('Transaction deleted', 'success')
    return redirect(url_for('view_transactions'))

if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    app.run(debug=True)
