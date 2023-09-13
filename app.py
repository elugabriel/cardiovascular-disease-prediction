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
        username TEXT,
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
        password = request.form['password'].encode('utf-8')  # Encode password

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()

        if user is not None:
            stored_username = user['username']
            stored_password = user['password'].encode('utf-8')  # Decode stored_password

            # Check if the user is a doctor
            cur.execute('SELECT * FROM doctor WHERE email = ?', (user['email'],))
            doctor = cur.fetchone()

            if doctor is not None:
                user_role = 'doctor'
            else:
                user_role = 'user'

            if bcrypt.checkpw(password, stored_password):  # Use password and stored_password as bytes
                session['username'] = stored_username
                session['role'] = user_role  # Store user's role in session

                # Redirect to the appropriate dashboard based on the role
                if user_role == 'user':
                    return redirect(url_for('user_dashboard'))
                elif user_role == 'doctor':
                    return redirect(url_for('doctor_dashboard'))
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
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        state = request.form['state']
       
        

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cur.fetchone()

        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('signup.html', error=error)
        else:
            cur.execute('INSERT INTO users (firstname, lastname, username, email, password, phone, address, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        (firstname, lastname, username, email, hashed_password, phone, address, state))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))

    return render_template('signup.html')

# ... (other routes remain unchanged)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
