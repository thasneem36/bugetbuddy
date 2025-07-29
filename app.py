from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'yoursecretkey'

# DB Config
app.config.from_pyfile('config.py')
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['name'] = user['name']
            session['is_admin'] = user.get('is_admin', 0)
            return redirect('/dashboard')
        else:
            msg = 'Invalid credentials!'
    return render_template('login.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', name=session['name'])
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif password != confirm_password:
            msg = 'Passwords do not match!'
        elif not name or not email or not password:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect('/login')
    return render_template('register.html', msg=msg)

@app.route('/admin')
def admin():
    print(session)  # Add this line
    if 'loggedin' in session and session.get('is_admin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id, name, email, is_admin FROM users')
        users = cursor.fetchall()
        return render_template('admin.html', users=users, name=session['name'])
    return redirect('/login')

@app.route('/admin/delete/<int:user_id>')
def delete_user(user_id):
    if 'loggedin' in session and session.get('is_admin'):
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s AND is_admin = 0', (user_id,))
        mysql.connection.commit()
    return redirect('/admin')

@app.route('/admin/promote/<int:user_id>')
def promote_user(user_id):
    if 'loggedin' in session and session.get('is_admin'):
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE users SET is_admin = 1 WHERE id = %s', (user_id,))
        mysql.connection.commit()
    return redirect('/admin')

@app.route('/admin/demote/<int:user_id>')
def demote_user(user_id):
    if 'loggedin' in session and session.get('is_admin'):
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE users SET is_admin = 0 WHERE id = %s', (user_id,))
        mysql.connection.commit()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
