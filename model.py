from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(400), nullable=False)
    last_name = db.Column(db.String(400), nullable=False)
    phone = db.Column(db.String(20), nullable=False)  # Adjust the length accordingly
    address = db.Column(db.String(800), nullable=False)
    state = db.Column(db.String(200), nullable=False)  # Adjust the length accordingly

    


# Example Doctor model:
class Doctor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    hospital = db.Column(db.String(400), nullable = False)
    state = db.Column(db.String(400), nullable = False)

