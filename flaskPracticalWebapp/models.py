from flaskPracticalWebapp import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30), default="")
    surname = db.Column(db.String(30), default="")
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Default user profile picture
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    # Passwords will be hashed to a 60-character string
    password = db.Column(db.String(60), nullable=False)
    practicals = db.relationship("Practical", backref="author", lazy=True)

    def __repr__(self):
        return f"User({self.email}', '{self.image_file}')"

class Practical(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    degStudy = db.Column(db.String(10),  nullable=False)
    subject = db.Column(db.String(10), nullable=False)
    equipment = db.Column(db.Text, nullable=False)
    method = db.Column(db.Text, nullable=False)
    safety = db.Column(db.String, nullable=False, default="Wear safety goggles")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    def __repr__(self):
        return f'''
        {self.degStudy} {self.subject} - {self.title}

        {self.equipment}

        {self.method}'''
