import traceback
from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, WordPair, UserWordPair
from app.forms import RegistrationForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm, PlayForm, CheckGuessForm
from app.game import (load_word_pair, load_synonyms, move_word_pair_to_used, rhyming_game, record_user_guess, get_synonyms)
from flask_mail import Message
from app.utils import send_reset_email
import logging
from app.utils import record_user_guess, update_user_streak
from datetime import datetime, timedelta
import pytz

bp = Blueprint('auth', __name__)
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# = logging.getLogger(__name__)

@bp.before_app_request
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)

@bp.route("/", methods=["GET", "POST"])
def index():
    login_form = LoginForm()
    register_form = RegistrationForm()
    return render_template("index.html", login_form=login_form, register_form=register_form)

@bp.route('/test_db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {e}"

@bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        print("Form is valid. Username and email checks passed.")
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user_by_username = User.query.filter_by(username=username).first()
        if existing_user_by_username:
            flash('Username already taken, please choose another one.', 'danger')
            return render_template('register.html', form=form)

        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash('Email already used, please choose another one.', 'danger')
            return render_template('register.html', form=form)

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)

        try:
            db.session.commit()

            # Initialize user_word_pair records for the new user
            all_word_pairs = WordPair.query.all()
            for pair in all_word_pairs:
                user_word_pair = UserWordPair(user_id=user.id, word_pair_id=pair.id)
                db.session.add(user_word_pair)

            db.session.commit()

            # Optionally, log the user in after registration
            login_user(user)

            return redirect(url_for('auth.confirmation'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("Error while creating user: %s", traceback.format_exc())
            flash('An error occurred while creating the account. Please try again.', 'danger')

    return render_template('register.html', form=form)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    session.permanent = True
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)

            # Initialize user_word_pair records if not already set up
            existing_pairs = {pair.word_pair_id for pair in UserWordPair.query.filter_by(user_id=user.id).all()}
            all_pairs = {pair.id for pair in WordPair.query.all()}

            for pair_id in all_pairs - existing_pairs:
                user_word_pair = UserWordPair(user_id=user.id, word_pair_id=pair_id)
                db.session.add(user_word_pair)

            db.session.commit()

            flash('Logged in successfully!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')

    return render_template('login.html', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user is None:
            flash('No user found with that email address.', 'danger')
            return redirect(url_for('auth.reset_password_request'))

        token = user.generate_reset_token()

        send_reset_email(email, user.username, token)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('reset_password_request.html', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('The reset link is invalid or has expired.')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        new_password = form.password.data

        if user:
            user.set_password(new_password)
            try:
                db.session.commit()
                flash('Your password has been updated.')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while updating the password.')

    return render_template('reset_password.html', form=form, token=token)

@bp.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    user = current_user

    # Calculate total points, current streak, and max streak
    total_points = sum(stat.points_earned for stat in user.stats)
    current_streak = user.current_streak
    max_streak = user.max_streak

    # Pass this data to the template
    return render_template('dashboard.html',
                           user=user,
                           total_points=total_points,
                           current_streak=current_streak,
                           max_streak=max_streak)


@bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))

@bp.route('/get_hint', methods=['GET'])
@login_required
def get_hint():
    if 'hints_used' not in session:
        session['hints_used'] = 0

    # Increment the hint usage
    session['hints_used'] += 1

    return redirect(url_for('auth.play', hint='yes'))

@bp.route('/play', methods=['POST', 'GET'])
def play():
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        flash('User not found!', 'danger')
        return redirect(url_for('auth.index'))

    timezone = pytz.timezone('America/New_York')
    today = datetime.now(timezone).date()

    last_guess_date = user.last_correct_guess_date
    last_incorrect_guess_date = user.last_incorrect_guess_date

    # Prevent playing if the user has already guessed today's word pair
    if last_guess_date == today or last_incorrect_guess_date == today:
        return render_template('already_guessed.html')

    # Fetch only word pairs available today and not yet used
    available_word_pairs = UserWordPair.query.join(WordPair).filter(
        UserWordPair.user_id == user_id,
        UserWordPair.used == False,
        WordPair.date_available == today
    ).all()

    if not available_word_pairs:
        return render_template('already_guessed.html')

    user_word_pair = available_word_pairs[0]
    word_pair = WordPair.query.get(user_word_pair.word_pair_id)

    if not word_pair:
        return render_template('already_guessed.html')

    word1 = word_pair.word1
    word2 = word_pair.word2

    synonyms_dict = {
        word1: [word_pair.word1_synonym1, word_pair.word1_synonym2],
        word2: [word_pair.word2_synonym1, word_pair.word2_synonym2]
    }

    form = CheckGuessForm()

    # Sync session with database for tracking attempts and hints
    if 'attempts' not in session or session.get('word_pair_id') != user_word_pair.word_pair_id:
        session['attempts'] = user_word_pair.attempts
        session['hints_used'] = 0
        session['word_pair_id'] = user_word_pair.word_pair_id

    # Handle hint requests
    hint_requested = request.args.get('hint', 'no') == 'yes'
    if hint_requested:
        session['hints_used'] += 1

    if form.validate_on_submit():
        user_input1 = form.user_input1.data.strip().lower()
        user_input2 = form.user_input2.data.strip().lower()

        if user_input1 == word1 and user_input2 == word2:
            points = 2 if session['hints_used'] == 0 else 1
            flash('Correct!', 'success')
            user_word_pair.used = True
            user_word_pair.attempts = session['attempts']
            db.session.commit()

            # Update streak and points
            if current_user.is_authenticated:
                update_user_streak(user_id, success=True)
                user.total_points += points
                user.last_correct_guess_date = today
                db.session.commit()

            # Clear session variables after successful guess
            session.pop('hints_used', None)
            session.pop('attempts', None)
            session.pop('word_pair_id', None)
            return render_template('correct_guess.html', points_awarded=points)

        else:
            session['attempts'] += 1
            user_word_pair.attempts = session['attempts']
            db.session.commit()

            # Handle game over after 3 attempts
            if session['attempts'] >= 3:
                flash('You have used all your attempts!', 'danger')
                if current_user.is_authenticated:
                    update_user_streak(user_id, success=False)
                    user.last_incorrect_guess_date = today
                    user_word_pair.used = True
                    db.session.commit()

                # Clear session after game over
                session.pop('hints_used', None)
                session.pop('attempts', None)
                session.pop('word_pair_id', None)
                return render_template('game_over.html', word1=word1, word2=word2)

            return render_template('incorrect_guess.html', hints_used=session['hints_used'])

    # Assign synonyms based on whether hints were requested
    synonym_word1_1 = synonyms_dict[word1][0]
    synonym_word2_1 = synonyms_dict[word2][0]
    if session['hints_used'] > 0:
        synonym_word1_1 += f" / {synonyms_dict[word1][1]}"
        synonym_word2_1 += f" / {synonyms_dict[word2][1]}"

    # Determine the progress bar class based on remaining attempts
    remaining_attempts = 3 - session['attempts']
    progress_class = f'progress-bar-{remaining_attempts}'

    return render_template(
        'play.html',
        word1=word1,
        word2=word2,
        form=form,
        synonym_word1=synonym_word1_1,
        synonym_word2=synonym_word2_1,
        already_guessed=False,
        progress_class=progress_class,
        attempts=remaining_attempts
    )




@bp.route('/check_guess', methods=['POST'])
@login_required
def check_guess():
    user_input1 = request.form.get('user_input1', '').strip().lower()
    user_input2 = request.form.get('user_input2', '').strip().lower()
    word1 = request.form.get('word1', '')
    word2 = request.form.get('word2', '')
    hints_used = session.get('hints_used', 0)

    word_pair = WordPair.query.filter_by(word1=word1, word2=word2).first()

    if not word_pair:
        return render_template('incorrect_guess.html', hints_used=hints_used, word1_synonym1='', word1_synonym2='',
                               word2_synonym1='', word2_synonym2='')

    if user_input1 == word_pair.word1 and user_input2 == word_pair.word2:
        points = 2 if hints_used == 0 else 1
        current_user.total_points += points
        current_user.correct_guesses += 1
        current_user.last_correct_guess_date = datetime.today().date()
        db.session.commit()

        user_word_pair = UserWordPair.query.filter_by(user_id=current_user.id, word_pair_id=word_pair.id).first()
        if user_word_pair:
            user_word_pair.used = True
            db.session.commit()

        return render_template('correct_guess.html', points_awarded=points)

    session['attempts'] += 1

    if session['attempts'] >= 3:
        flash('You have used all your attempts!', 'danger')
        update_user_streak(current_user.id, success=False)
        session.pop('attempts', None)
        session.pop('hints_used', None)
        return render_template('game_over.html')

    if hints_used == 2:
        return render_template('incorrect_guess_two_hints.html',
                               word1_synonym1=word_pair.word1_synonym1,
                               word1_synonym2=word_pair.word1_synonym2,
                               word2_synonym1=word_pair.word2_synonym1,
                               word2_synonym2=word_pair.word2_synonym2)

    return render_template('incorrect_guess.html', hints_used=hints_used,
                           word1_synonym1=word_pair.word1_synonym1,
                           word1_synonym2=word_pair.word1_synonym2,
                           word2_synonym1=word_pair.word2_synonym1,
                           word2_synonym2=word_pair.word2_synonym2)



def init_app(app):
    app.register_blueprint(bp)