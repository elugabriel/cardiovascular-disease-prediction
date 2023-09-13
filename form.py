from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, validators

# Define your login and signup forms using WTForms.
# Example login form:
class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('doctor', 'Doctor')])
    submit = SubmitField('Login')

# Example signup form:
class SignupForm(FlaskForm):
    id = StringField('ID', [validators.DataRequired()])
    name = StringField('Name', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    phone = StringField('Phone', [validators.DataRequired()])
    address = StringField('Address', [validators.DataRequired()])
    state = StringField('State', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('doctor', 'Doctor')])
    submit = SubmitField('Sign Up')