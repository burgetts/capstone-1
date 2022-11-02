"""SQLAlchemy models for Capstone 1."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect database to Flask app."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

    records = db.relationship('Record', backref='user')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.first_name} {self.last_name}>"

    @classmethod
    def signup(cls, username, email, password, first_name, last_name):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name = first_name,
            last_name=last_name
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Record(db.Model):
    """Model for user history records."""
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trivia_score = db.Column(db.String, default="Not completed")
    math_score = db.Column(db.String, default="Not completed")
    reading = db.Column(db.String, default="Yes")
    date = db.Column(db.String)

    def __repr__(self):
        return f"<Record #{self.id}: User id:{self.user_id}, Trivia score: {self.trivia_score}, Math score: {self.math_score}, Reading: {self.reading}, Date: {self.date}>"
    

    