# Copyright (c) 2024 Jason Wicks
# All rights reserved.
#
# Copyright pending.

from flask_mail import Message
from flask import url_for
from app import mail, db
from app.models import User, UserStats
from datetime import date, datetime, timedelta
import jwt


def send_reset_email(to_email, username, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)

    # Create the email body including the username
    msg = Message('Password Reset Request', recipients=[to_email])
    msg.body = f'''Hello there, fellow rhymer!

Your username is: {username}.

To reset your password, visit the following link:
{reset_url}

If you did not make this request, please ignore this email and no changes will be made.

Thanks, and make sure to smile at least once today!

Rhyme It
'''

    mail.send(msg)


def load_synonyms():
    synonyms_dict = {}
    try:
        synonyms = db.session.query(Synonym).all()
        for synonym in synonyms:
            synonyms_dict[synonym.word] = synonym.synonyms.split(",")
    except Exception as e:
        print(f"Error loading synonyms from database: {e}")
    return synonyms_dict

def record_user_guess(user_id, word_pair_id, points):
    user = User.query.get(user_id)
    user.total_points += points

    today_stats = UserStats.query.filter_by(user_id=user_id, date=date.today()).first()

    if not today_stats:
        today_stats = UserStats(user_id=user_id, puzzles_solved=1, points_earned=points)
        db.session.add(today_stats)
    else:
        today_stats.puzzles_solved += 1
        today_stats.points_earned += points

    db.session.commit()

def update_user_streak(user_id, success):
    user = User.query.get(user_id)
    user.update_streak(success)
    db.session.commit()

def create_token(app, user_id):
    expiration = datetime.utcnow() + timedelta(days=21)
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(app, token):
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return decoded['user_id']
    except jwt.ExpiredSignatureError:
        return None