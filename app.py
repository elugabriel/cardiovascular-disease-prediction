from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os
import bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(15)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT,
        lastname TEXT,
        email TEXT,
        password TEXT,
        phone TEXT,
        address TEXT,
        state TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS doctor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT,
        lastname TEXT,
        email TEXT,
        password TEXT,
        phone TEXT,
        hospital TEXT,
        state TEXT
    )''')
    conn.commit()
    conn.close()

create_tables()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        
        if user is not None:
            stored_username = user['username']
            stored_password = user['password']

            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session['username'] = stored_username
                return redirect(url_for('main'))
            else:
                error = 'Invalid password.'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        address = request.form['address']
        ssname = request.form['ssname']
        purpose = request.form['purpose']
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cur.fetchone()

        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('signup.html', error=error)
        else:
            cur.execute('INSERT INTO users (firstname, lastname, username, email, address, ssname, purpose, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        (firstname, lastname, username, email, address, ssname, purpose, hashed_password))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))

    return render_template('signup.html')

# ... (other routes remain unchanged)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
