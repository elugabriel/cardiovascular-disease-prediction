from flask import Flask, render_template, request, session, redirect, url_for, flash
import sqlite3
import os
import bcrypt
import pickle
import random
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(15)

# Define the ordinal_mapping dictionary here
ordinal_mapping = {
    'Smoking': ['No', 'Yes'],
    'AlcoholDrinking': ['No', 'Yes'],
    'Stroke': ['No', 'Yes'],
    'DiffWalking': ['No', 'Yes'],
    'Diabetic': ['No', 'No, borderline diabetes', 'Yes', 'Yes (during pregnancy)'],
    'PhysicalActivity': ['No', 'Yes'],
    'GenHealth': ['Fair', 'Good', 'Very good', 'Excellent', 'Poor'],
    'Asthma': ['No', 'Yes'],
    'KidneyDisease': ['No', 'Yes'],
    'SkinCancer': ['No', 'Yes'],
    'AgeCategory': ['55-59', '80 or older', '65-69', '75-79', '40-44', '70-74', '60-64', '50-54', '45-49', '18-24', '35-39', '30-34', '25-29']
}

def generate_random_consultation_date():
    # Generate a random date between Monday (0) and Friday (4)
    random_weekday = random.randint(0, 4)

    # Generate a random time between 9am (9) and 3pm (15)
    random_hour = random.randint(9, 15)

    # Create a datetime object for the consultation date and time
    consultation_date = datetime.datetime.now()
    consultation_date = consultation_date.replace(hour=random_hour, minute=0, second=0, microsecond=0)

    # Calculate the date of the next occurrence of the chosen weekday
    days_until_consultation = (random_weekday - consultation_date.weekday()) % 7
    consultation_date += datetime.timedelta(days=days_until_consultation)

    return consultation_date.strftime('%A, %d %B %Y, %I:%M %p')


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

def get_user_data(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user_data = cur.fetchone()
    conn.close()
    return user_data

def get_doctor_data(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM doctor WHERE username = ?',  (username,))
    doctor_data = cur.fetchone()
    conn.close()
    return doctor_data


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        

        # Convert the user input password to bytes
        password_bytes = password.encode('utf-8')

        is_doctor = request.form['is_doctor'].lower()

        conn = get_db_connection()
        cur = conn.cursor()

        if is_doctor == 'yes':
            cur.execute('SELECT * FROM doctor WHERE username = ?', (username,))
            user = cur.fetchone()
            stored_username = user['username']
        else:
            cur.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cur.fetchone()
            stored_username = user['username']

        conn.close()

        if user is not None or bcrypt.checkpw(password_bytes, user['password']):
            # User authentication successful
            if is_doctor == 'yes':
                session['username'] = stored_username
                session['doctor_id'] = user['id']
                session['role'] = 'doctor'
                return redirect(url_for('doctor_dashboard'))
            else:
                session['username'] = stored_username
                session['user_id'] = user['id']
                session['role'] = 'user'
                return redirect(url_for('user_dashboard'))
        else:
            error = 'Invalid username or password.'
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

@app.route('/user_dashboard')
def user_dashboard():
    # Add code to render the user dashboard template
    return render_template('user_dashboard.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
   
    return render_template('doctor_dashboard.html')

@app.route('/logout')
def logout():
    # Add code here to clear the user session or perform any other logout actions
    session.clear()  # Clear the user's session
    return redirect(url_for('login'))  # Redirect to the login page after logout

@app.route('/profile')
def profile():
    # Fetch user information from the user table based on the current user's username
    username = session.get('username')  # Assuming you have stored the username in the session
    user_data = get_user_data(username)  # Replace this with your database query function

    return render_template('profile.html', user_data=user_data)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # Retrieve the edited user data from the form
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        state = request.form['state']

        # Get the current user's ID from the session
        user_id = session.get('user_id')

        # Update the user's data in the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE users SET firstname=?, lastname=?, email=?, phone=?, address=?, state=? WHERE id=?',
                    (firstname, lastname, email, phone, address, state, user_id))
        conn.commit()
        conn.close()

        # Redirect to the profile page after editing
        return redirect(url_for('profile'))

    # Fetch the user's current data for pre-filling the edit form
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cur.fetchone()
    conn.close()

    return render_template('edit_profile.html', user_data=user_data)

@app.route('/assessment_form', methods=['GET', 'POST'])
def assessment_form():
    if request.method == 'GET':
        # Render the assessment_form.html template
        return render_template('assessment_form.html')
    elif request.method == 'POST':
        # Handle the form submission here
        # You can access form data using request.form

        # Get selected dropdown values
        Sex = request.form.get('Sex')
        Smoking = request.form.get('Smoking')
        AlcoholDrinking = request.form.get('AlcoholDrinking')
        Stroke = request.form.get('Stroke')
        DiffWalking = request.form.get("DiffWalking")
        Diabetic = request.form.get("Diabetic")
        PhysicalActivity = request.form.get("PhysicalActivity")
        GenHealth = request.form.get('GenHealth')
        Asthma = request.form.get('Asthma')
        KidneyDisease = request.form.get('KidneyDisease')
        SkinCancer = request.form.get('SkinCancer')
        AgeCategory = request.form.get('AgeCategory')
        BMI = request.form.get('BMI')
        PhysicalHealth = request.form.get('PhysicalHealth')
        MentalHealth = request.form.get('MentalHealth')
        SleepTime = request.form.get('SleepTime')

        # Preprocess the input data as you did during training
        Sex = 1 if Sex == "Male" else 0
        BMI = float(BMI)
        PhysicalHealth = float(PhysicalHealth)
        MentalHealth = float(MentalHealth)
        SleepTime = float(SleepTime)

        # Ordinal encoding for other features
        Smoking = ordinal_mapping['Smoking'].index(Smoking)
        AlcoholDrinking = ordinal_mapping['AlcoholDrinking'].index(AlcoholDrinking)
        Stroke = ordinal_mapping['Stroke'].index(Stroke)
        DiffWalking = ordinal_mapping['DiffWalking'].index(DiffWalking)
        Diabetic = ordinal_mapping['Diabetic'].index(Diabetic)
        PhysicalActivity = ordinal_mapping['PhysicalActivity'].index(PhysicalActivity)
        GenHealth = ordinal_mapping['GenHealth'].index(GenHealth)
        Asthma = ordinal_mapping['Asthma'].index(Asthma)
        KidneyDisease = ordinal_mapping['KidneyDisease'].index(KidneyDisease)
        SkinCancer = ordinal_mapping['SkinCancer'].index(SkinCancer)
        AgeCategory = ordinal_mapping['AgeCategory'].index(AgeCategory)

        # Create a list of transformed features
        transformed_features = [Sex, Smoking, AlcoholDrinking, Stroke, DiffWalking,
                                Diabetic, PhysicalActivity, GenHealth, Asthma, KidneyDisease,
                                SkinCancer, AgeCategory, BMI, PhysicalHealth, MentalHealth, SleepTime]

        # Reshape the list to match the model's input shape (1, 16)
        transformed_features = [transformed_features]

        # Make prediction
        Algorithm = pickle.load(open("model.pkl", "rb"))
        prediction = Algorithm.predict(transformed_features)
        if prediction == 1:
            result = "Cardiovascular Disease predicted"
        else:
            result = "No Cardiovascular Disease predicted"

        return render_template('predict_page.html', prediction=prediction, result=result)

        # After processing, you can redirect or render a different template as needed
        return redirect(url_for('user_dashboard'))





@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'GET':
        return render_template('booking.html')
    elif request.method == 'POST':
        username = session.get('username')
        user_data = get_user_data(username)
        state = request.form.get('state')
        
        # Get a list of doctors from the selected state
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM doctor WHERE state = ?', (state,))
        doctors = cur.fetchall()
        conn.close()

        if not doctors:
            return "No doctors available in the selected state."

        # Choose a random doctor from the list
        random_doctor = random.choice(doctors)
        random_doctor_id = random_doctor['id']

        # Update the user's doctor_id in the database
        user_id = session.get('user_id')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE users SET doctor_id = ? WHERE id = ?', (random_doctor_id, user_id))
        conn.commit()
        
        # Fetch the selected doctor's information for the template context
        cur.execute('SELECT * FROM doctor WHERE id = ?', (random_doctor_id,))
        doctor_data = cur.fetchone()

        conn.close()

        consultation_date = generate_random_consultation_date()

        return render_template('consultation.html', 
                               user_data=user_data, 
                               doctor_data=doctor_data, 
                               state=state, 
                               date=consultation_date)



        # After processing, you can redirect or render a different template as needed
        return redirect(url_for('user_dashboard'))
    
@app.route('/doctor_profile')
def doctor_profile():
    username = session.get('username')
    doctor_data = get_doctor_data(username)
    
    return render_template('doctor_profile.html', doctor_data=doctor_data)

@app.route('/patient_assign')
def patient_assign():
    # Fetch the currently logged in doctor's ID from the session
    doctor_id = session.get('doctor_id')
    print(f"Doctor ID: {doctor_id}")
    
    # Query the users table to get patients assigned to this doctor
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE doctor_id = ?', (doctor_id,))
    patients = cur.fetchall()
    conn.close()

    # Render the patient_assign.html template with the patient data
    return render_template('patient_assign.html', patients=patients)

    


if __name__ == '__main__':
    app.run(debug=True, port=5200)
