from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    max_streak = db.Column(db.Integer, default=0)
    correct_guesses = db.Column(db.Integer, default=0)
    last_correct_guess_date = db.Column(db.Date, nullable=True)
    last_incorrect_guess_date = db.Column(db.Date, nullable=True)
    stats = db.relationship('UserStats', back_populates='user')
    user_word_pairs = db.relationship('UserWordPair', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def verify_reset_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        except:
            return None
        return User.query.filter_by(email=email).first()

    def update_streak(self, success):
        today = datetime.today().date()

        # Check if this is a new day and the streak was not continued
        if self.last_correct_guess_date and (today - self.last_correct_guess_date).days > 1:
            # Reset current streak if they missed a day
            if self.current_streak > self.max_streak:
                self.max_streak = self.current_streak
            self.current_streak = 0

        if success:
            self.current_streak += 1
            self.last_correct_guess_date = today
            if self.current_streak > self.max_streak:
                self.max_streak = self.current_streak
        else:
            if self.current_streak > self.max_streak:
                self.max_streak = self.current_streak
            self.current_streak = 0
            self.last_incorrect_guess_date = today

        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class WordPair(db.Model):
    __tablename__ = 'word_pair'
    id = db.Column(db.Integer, primary_key=True)
    word1 = db.Column(db.String(100), nullable=False)
    word1_synonym1 = db.Column(db.String(100), nullable=False)
    word1_synonym2 = db.Column(db.String(100), nullable=False)
    word2 = db.Column(db.String(100), nullable=False)
    word2_synonym1 = db.Column(db.String(100), nullable=False)
    word2_synonym2 = db.Column(db.String(100), nullable=False)
    used = db.Column(db.Boolean, default=False)
    date_available = db.Column(db.Date, nullable=False)

    user_word_pairs = db.relationship('UserWordPair', back_populates='word_pair', lazy=True)
    guest_word_pairs = db.relationship('GuestUserWordPair', back_populates='word_pair', lazy=True)

    def __repr__(self):
        return f'<WordPair {self.word1} - {self.word2}>'

class Guest(db.Model):
    __tablename__ = 'guest'
    id = db.Column(db.Integer, primary_key=True)
    guest_word_pairs = db.relationship('GuestUserWordPair', back_populates='guest', lazy=True)

    def __repr__(self):
        return f"<Guest id={self.id}>"


class UserWordPair(db.Model):
    __tablename__ = 'user_word_pair'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    word_pair_id = db.Column(db.Integer, db.ForeignKey('word_pair.id'), primary_key=True)
    guessed = db.Column(db.Boolean, default=False)
    used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    hints_used = db.Column(db.Integer, default=0, nullable=False)

    word1_status = db.Column(db.String(10), default='wrong')
    word2_status = db.Column(db.String(10), default='wrong')

    user = db.relationship('User', back_populates='user_word_pairs')
    word_pair = db.relationship('WordPair', back_populates='user_word_pairs')


class GuestUserWordPair(db.Model):
    __tablename__ = 'guest_user_word_pair'
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), primary_key=True)
    word_pair_id = db.Column(db.Integer, db.ForeignKey('word_pair.id'), primary_key=True)
    guessed = db.Column(db.Boolean, default=False)
    used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    hints_used = db.Column(db.Integer, default=0, nullable=False)

    word1_status = db.Column(db.String(10), default='wrong')
    word2_status = db.Column(db.String(10), default='wrong')

    guest = db.relationship('Guest', back_populates='guest_word_pairs')
    word_pair = db.relationship('WordPair', back_populates='guest_word_pairs')

    def __repr__(self):
        return f"<GuestUserWordPair guest_id={self.guest_id}, word_pair_id={self.word_pair_id}>"


class UserStats(db.Model):
    __tablename__ = 'user_stats'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=func.current_date())
    puzzles_solved = db.Column(db.Integer, default=0)
    puzzles_failed = db.Column(db.Integer, default=0)
    points_earned = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='stats')

    first_try_successes = db.Column(db.Integer, default=0)
    total_tries = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    total_puzzles_played = db.Column(db.Integer, default=0)
