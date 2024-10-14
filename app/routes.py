import traceback
import uuid
from urllib import response
import random

from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app, session, make_response, \
    get_flashed_messages
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import func

from app import db
from app.models import User, WordPair, UserWordPair, Guest, GuestUserWordPair, UserStats
from app.forms import RegistrationForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm, CheckGuessForm, GuestForm
from app.utils import send_reset_email, create_token, update_user_streak
import logging
from datetime import datetime
import pytz
from flask_wtf import FlaskForm
from wtforms import SubmitField


bp = Blueprint('auth', __name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# = logging.getLogger(__name__)
class LogoutForm(FlaskForm):
    submit = SubmitField('Logout')

@bp.before_app_request
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)

@bp.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    login_form = LoginForm()
    register_form = RegistrationForm()
    guest_form = GuestForm()

    if guest_form.validate_on_submit():
        # Redirect guest users to the guest play route
        return redirect(url_for('guest_play'))

    return render_template(
        "index.html",
        login_form=login_form,
        register_form=register_form,
        guest_form=guest_form
    )

@bp.route('/test_db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {e}"

@bp.route("/register", methods=['GET', 'POST'])
def register():
    # Retrieve and discard any flash messages to prevent them from showing up
    get_flashed_messages()  # This will discard all flash messages

    form = RegistrationForm()
    if form.validate_on_submit():
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
            logout_user()
            login_user(user, remember=True)

            existing_pairs = {pair.word_pair_id for pair in UserWordPair.query.filter_by(user_id=user.id).all()}
            all_pairs = {pair.id for pair in WordPair.query.all()}

            token = create_token(current_app, user.id)

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
def dashboard():
    user = current_user
    user_stats = UserStats.query.filter_by(user_id=user.id).all()
    form = LogoutForm()

    total_points = sum(stat.points_earned for stat in user.stats)
    current_streak = user.current_streak
    max_streak = user.max_streak

    first_try_successes = sum(stat.first_try_successes for stat in user_stats)
    total_tries = sum(stat.total_tries for stat in user_stats)
    hints_used = sum(stat.hints_used for stat in user_stats)
    total_puzzles_played = sum(stat.total_puzzles_played for stat in user_stats)

    two_tries_count = UserWordPair.query.filter_by(user_id=user.id, attempts=2).count()
    three_tries_count = UserWordPair.query.filter_by(user_id=user.id, attempts=3).count()
    perfect_count = UserWordPair.query.filter_by(user_id=user.id, attempts=1).count()

    perfect_percentage = (perfect_count / total_puzzles_played * 100) if total_puzzles_played > 0 else 0
    two_tries_percentage = (two_tries_count / total_puzzles_played * 100) if total_puzzles_played > 0 else 0
    three_tries_percentage = (three_tries_count / total_puzzles_played * 100) if total_puzzles_played > 0 else 0

    return render_template('dashboard.html',
                           user=user,
                           total_points=total_points,
                           current_streak=current_streak,
                           max_streak=max_streak,
                           first_try_successes=first_try_successes,
                           total_tries=total_tries,
                           hints_used=hints_used,
                           total_puzzles_played=total_puzzles_played,
                           two_tries_count=two_tries_count,
                           three_tries_count=three_tries_count,
                           perfect_count=perfect_count,
                           perfect_percentage=perfect_percentage,
                           two_tries_percentage=two_tries_percentage,
                           three_tries_percentage=three_tries_percentage,
                           form=form)

@bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()

    #session.clear()  # Clears session data
    flash('You have been logged out.', 'success')
    #session.pop('_permanent', None)

    return redirect(url_for('auth.login'))

@bp.route('/get_hint', methods=['GET'])
def get_hint():
    if 'hints_used' not in session:
        session['hints_used'] = 0

    # Increment the hint usage
    session['hints_used'] += 1

    return redirect(url_for('auth.play', hint='yes'))


def update_user_stats(user, attempts, correct_guess, hints_requested):
    # Check if UserStats entry exists for today
    user_stats = UserStats.query.filter_by(user_id=user.id, date=func.current_date()).first()

    if not user_stats:
        # If no stats entry exists for today, create a new one
        user_stats = UserStats(
            user_id=user.id,
            puzzles_solved=0,
            puzzles_failed=0,
            points_earned=0,
            first_try_successes=0,
            total_tries=0,
            hints_used=0,
            total_puzzles_played=0
        )
        db.session.add(user_stats)
        db.session.commit()

    # Update the stats as needed
    user_stats.total_puzzles_played += 1
    if correct_guess:
        user_stats.puzzles_solved += 1
        if attempts == 1 and hints_requested == 0:
            user_stats.first_try_successes += 1
    else:
        user_stats.puzzles_failed += 1

    user_stats.hints_used += hints_requested

    db.session.commit()

@bp.route('/play', methods=['POST', 'GET'])
@login_required
def play():
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        flash('User not found!', 'danger')
        return redirect(url_for('auth.index'))

    timezone = pytz.timezone('America/New_York')
    today = datetime.now(timezone).date()

    word_pair = WordPair.query.filter_by(date_available=today).first()
    if not word_pair:
        return render_template('already_guessed.html')

    if current_user.is_authenticated:
        game_results = UserWordPair.query.filter_by(
            user_id=user_id,
            word_pair_id=word_pair.id,
            used=True
        ).first()

        if game_results:
            word1_status = game_results.word1_status
            word2_status = game_results.word2_status

            attempts_list = [{
                'word1_correct': word1_status == 'correct',
                'word1_synonym_correct': word1_status == 'synonym',
                'word2_correct': word2_status == 'correct',
                'word2_synonym_correct': word2_status == 'synonym'
            }]

            hints_used = game_results.hints_used

            return render_template('already_guessed.html',
                                   attempts_list=attempts_list,
                                   hints_used=hints_used,
                                   word1=word_pair.word1,
                                   word2=word_pair.word2)

        existing_record = UserWordPair.query.filter_by(
            user_id=user_id,
            word_pair_id=word_pair.id
        ).first()

        if not existing_record:
            user_word_pair = UserWordPair(
                user_id=user_id,
                word_pair_id=word_pair.id,
                used=False,
                attempts=0,
                word1_status='wrong',
                word2_status='wrong'
            )
            db.session.add(user_word_pair)
        else:
            user_word_pair = existing_record
            user_word_pair.used = False

        db.session.commit()
        attempts_used = user_word_pair.attempts

    game_results = UserWordPair.query.filter_by(
        user_id=user_id,
        word_pair_id=word_pair.id,
        used=True
    ).first()

    if game_results:
        attempts_list = []
        attempts_list.append({
            'word1_correct': game_results.word1_status == 'correct',
            'word1_synonym_correct': game_results.word1_status == 'synonym',
            'word2_correct': game_results.word2_status == 'correct',
            'word2_synonym_correct': game_results.word2_status == 'synonym'
        })

        hints_used = session.get('hints_used', 0)
        return render_template('already_guessed.html', attempts_list=attempts_list, hints_used=hints_used,
                               word1=word_pair.word1, word2=word_pair.word2)

    existing_record = db.session.query(UserWordPair).filter_by(
        user_id=user_id,
        word_pair_id=word_pair.id
    ).first()

    if not existing_record:
        user_word_pair = UserWordPair(
            user_id=user_id,
            word_pair_id=word_pair.id,
            used=False,
            attempts=0,
            word1_status='wrong',
            word2_status='wrong'
        )
        db.session.add(user_word_pair)
    else:
        user_word_pair = existing_record
        user_word_pair.used = False

    db.session.commit()

    attempts_today = UserWordPair.query.filter_by(
        user_id=user_id,
        word_pair_id=word_pair.id,
        used=True
    ).count()

    attempts_used = user_word_pair.attempts

    if attempts_today < 3:
        remaining_attempts = 3 - attempts_today
    else:
        return render_template('already_guessed.html', word1=word_pair.word1, word2=word_pair.word2)

    word1 = word_pair.word1
    word2 = word_pair.word2

    synonyms_dict = {
        word1: [word_pair.word1_synonym1, word_pair.word1_synonym2],
        word2: [word_pair.word2_synonym1, word_pair.word2_synonym2]
    }

    form = CheckGuessForm()

    if 'hints_used' not in session:
        session['hints_used'] = 0
        session['attempts_list'] = []

    hint_requested = request.args.get('hint', 'no') == 'yes'

    if hint_requested:
        session['hints_used'] += 1

    if form.validate_on_submit():
        user_input1 = form.user_input1.data.strip().lower()
        user_input2 = form.user_input2.data.strip().lower()

        word1_correct = user_input1 == word1
        word2_correct = user_input2 == word2

        word1_synonym_correct = user_input1 in [syn.lower() for syn in synonyms_dict[word1]]
        word2_synonym_correct = user_input2 in [syn.lower() for syn in synonyms_dict[word2]]

        if word1_correct:
            user_word_pair.word1_status = 'correct'
        elif word1_synonym_correct:
            user_word_pair.word1_status = 'synonym'
        else:
            user_word_pair.word1_status = 'wrong'

        if word2_correct:
            user_word_pair.word2_status = 'correct'
        elif word2_synonym_correct:
            user_word_pair.word2_status = 'synonym'
        else:
            user_word_pair.word2_status = 'wrong'

        user_word_pair.attempts += 1
        db.session.commit()

        attempts_used += 1
        session['attempts'] = attempts_used

        attempts_list = session.get('attempts_list', [])
        attempts_list.append({
            'word1_correct': word1_correct,
            'word1_synonym_correct': word1_synonym_correct,
            'word2_correct': word2_correct,
            'word2_synonym_correct': word2_synonym_correct
        })
        session['attempts_list'] = attempts_list

        if word1_correct and word2_correct:
            points = 2 if session['hints_used'] == 0 else 1
            flash('Correct!', 'success')
            user_word_pair.used = True
            db.session.commit()

            if current_user.is_authenticated:
                if attempts_used == 1:
                    update_user_stats(user, attempts=1, correct_guess=True, hints_requested=session['hints_used'])
                else:
                    update_user_stats(user, attempts=attempts_used, correct_guess=True,
                                      hints_requested=session['hints_used'])

                update_user_streak(user_id, success=True)
                user.total_points += points
                user.last_correct_guess_date = today
                db.session.commit()
            else:
                session['last_correct_guess_date'] = today

            hints_used = session.get('hints_used', 0)

            session.pop('hints_used', None)
            session.pop('attempts_list', None)

            return render_template('correct_guess.html', points_awarded=points, attempts=attempts_used,
                                   attempts_list=attempts_list, hints_used=hints_used)

        else:
            if attempts_used >= 3:
                flash('You have used all your attempts!', 'danger')

                if current_user.is_authenticated:
                    update_user_stats(user, attempts=attempts_used, correct_guess=False,
                                      hints_requested=session['hints_used'])
                    update_user_streak(user_id, success=False)
                    user.last_incorrect_guess_date = today
                    user_word_pair.used = True
                    db.session.commit()
                else:
                    session['last_incorrect_guess_date'] = today

                attempts_list = session.get('attempts_list', [])
                hints_used = session.get('hints_used', 0)

                session.pop('hints_used', None)
                session.pop('attempts_list', None)

                return render_template('game_over.html', word1=word1, word2=word2,
                                       hints_used=hints_used,
                                       attempts_list=attempts_list)

            return render_template('incorrect_guess.html',
                                   word1_correct=word1_correct,
                                   word2_correct=word2_correct,
                                   word1_synonym_correct=word1_synonym_correct,
                                   word2_synonym_correct=word2_synonym_correct,
                                   user_input1=user_input1,
                                   user_input2=user_input2,
                                   hints_used=session['hints_used'])

    synonym_word1_1 = synonyms_dict[word1][0]
    synonym_word2_1 = synonyms_dict[word2][0]

    if session['hints_used'] > 0:
        synonym_word1_1 += f" / {synonyms_dict[word1][1]}"
        synonym_word2_1 += f" / {synonyms_dict[word2][1]}"

    remaining_attempts = 3 - attempts_used
    progress_class = f'progress-bar-{remaining_attempts}'

    return render_template(
        'play.html',
        word1=word1,
        word2=word2,
        form=form,
        synonym_word1=synonym_word1_1,
        synonym_word2=synonym_word2_1,
        word1_status=user_word_pair.word1_status,
        word2_status=user_word_pair.word2_status,
        already_guessed=False,
        progress_class=progress_class,
        attempts=remaining_attempts
    )

@bp.route('/check_guess', methods=['POST'])
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

def generate_guest_id():
    last_guest = db.session.query(Guest).order_by(Guest.unique_guest_id.desc()).first()
    return (last_guest.unique_guest_id + 1) if last_guest else 1

@bp.route('/guest_play', methods=['POST'])
def guest_play():
    guest_user = Guest(unique_guest_id=generate_guest_id())
    db.session.add(guest_user)
    db.session.commit()

    # Store guest_id in session
    session['guest_id'] = guest_user.unique_guest_id

    # Redirect to the play route
    return redirect(url_for('auth.play'))

@bp.route('/play_guest', methods=['POST', 'GET'])
def play_guest():
    if 'guest_id' not in session:
        new_guest = Guest()
        db.session.add(new_guest)
        db.session.commit()

        guest_id = new_guest.id
        session['guest_id'] = guest_id
    else:
        guest_id = session['guest_id']

    timezone = pytz.timezone('America/New_York')
    today = datetime.now(timezone).date()

    word_pair = WordPair.query.filter_by(date_available=today).first()
    if not word_pair:
        return render_template('already_guessed_as_guest.html')


    existing_record = GuestUserWordPair.query.filter_by(
        guest_id=guest_id,
        word_pair_id=word_pair.id
    ).first()

    if not existing_record:
        guest_word_pair = GuestUserWordPair(
            guest_id=guest_id,
            word_pair_id=word_pair.id,
            guessed=False,
            used=False,
            attempts=0,
            hints_used=0,
            word1_status='wrong',
            word2_status='wrong'
        )
        db.session.add(guest_word_pair)
    else:
        guest_word_pair = existing_record

    db.session.commit()

    word1 = word_pair.word1
    word2 = word_pair.word2

    synonyms_dict = {
        word1: [word_pair.word1_synonym1, word_pair.word1_synonym2],
        word2: [word_pair.word2_synonym1, word_pair.word2_synonym2]
    }

    form = CheckGuessForm()

    if 'hints_used' not in session:
        session['hints_used'] = 0
        session['attempts_list'] = []

    hint_requested = request.args.get('hint', 'no') == 'yes'
    if hint_requested:
        session['hints_used'] += 1
        guest_word_pair.hints_used += 1
        db.session.commit()

    max_attempts = 3

    if form.validate_on_submit():
        user_input1 = form.user_input1.data.strip().lower()
        user_input2 = form.user_input2.data.strip().lower()

        word1_correct = user_input1 == word1
        word2_correct = user_input2 == word2

        word1_synonym_correct = user_input1 in [syn.lower() for syn in
                                                [word_pair.word1_synonym1, word_pair.word1_synonym2]]
        word2_synonym_correct = user_input2 in [syn.lower() for syn in
                                                [word_pair.word2_synonym1, word_pair.word2_synonym2]]

        #guest_word_pair.word1_status = 'correct' if word1_correct else 'synonym' if word1_synonym_correct else 'wrong'
        #guest_word_pair.word2_status = 'correct' if word2_correct else 'synonym' if word2_synonym_correct else 'wrong'

        attempt_result = {
            'word1_correct': word1_correct,
            'word1_synonym_correct': word1_synonym_correct,
            'word2_correct': word2_correct,
            'word2_synonym_correct': word2_synonym_correct
        }

        # Append to session attempts_list
        attempts_list = session.get('attempts_list', [])
        attempts_list.append(attempt_result)
        session['attempts_list'] = attempts_list

        db.session.commit()
        if word1_correct:
            guest_word_pair.word1_status = 'correct'
        elif word1_synonym_correct:
            guest_word_pair.word1_status = 'synonym'
        else:
            guest_word_pair.word1_status = 'wrong'

        if word2_correct:
            guest_word_pair.word2_status = 'correct'
        elif word2_synonym_correct:
            guest_word_pair.word2_status = 'synonym'
        else:
            guest_word_pair.word2_status = 'wrong'

        guest_word_pair.attempts += 1
        db.session.commit()

        attempts_used = guest_word_pair.attempts

        if word1_correct and word2_correct:
            points = 2 if session['hints_used'] == 0 else 1
            #flash('Correct!', 'success')
            guest_word_pair.used = True
            db.session.commit()

            hints_used = session.get('hints_used', 0)

            session.pop('hints_used', None)

            return render_template('correct_guess_as_guest.html', points_awarded=points, attempts=attempts_used,
                                   hints_used=hints_used, attempts_list=attempts_list)

        if attempts_used >= max_attempts:
            #flash('You have used all your attempts!', 'danger')
            guest_word_pair.used = True
            db.session.commit()

            hints_used = session.get('hints_used', 0)

            attempts_list = session.get('attempts_list', [])  # Get the attempts history

            session.pop('hints_used', None)
            session.pop('attempts_list', None)

            return render_template('game_over_as_guest.html', word1=word_pair.word1, word2=word_pair.word2,
                                   hints_used=hints_used, attempts_list=attempts_list)

        return render_template('incorrect_guess_as_guest.html',
                               hints_used=session['hints_used'],
                               word1_status=guest_word_pair.word1_status,
                               word2_status=guest_word_pair.word2_status,
                               user_input1=user_input1,
                               user_input2=user_input2,
                               word1_synonym1=word_pair.word1_synonym1,
                               word1_synonym2=word_pair.word1_synonym2,
                               word2_synonym1=word_pair.word2_synonym1,
                               word2_synonym2=word_pair.word2_synonym2)

    synonym_word1 = synonyms_dict[word1][0]
    synonym_word2 = synonyms_dict[word2][0]
    if session['hints_used'] > 0:
        synonym_word1 += f" / {synonyms_dict[word1][1]}"
        synonym_word2 += f" / {synonyms_dict[word2][1]}"

    remaining_attempts = max_attempts - guest_word_pair.attempts


    return render_template(
        'play_as_guest.html',
        form=form,
        word1=word_pair.word1,
        word2=word_pair.word2,
        synonym_word1=synonym_word1,
        synonym_word2=synonym_word2,
        word1_status=guest_word_pair.word1_status,
        word2_status=guest_word_pair.word2_status,
        attempts=remaining_attempts,
        hints_used=session.get('hints_used', 0)
    )

@bp.route('/get_hint_as_guest', methods=['GET'])
def get_hint_as_guest():
    if 'hints_used' not in session:
        session['hints_used'] = 0

    # Increment the hint usage
    session['hints_used'] += 1

    return redirect(url_for('auth.play_guest', hint='yes'))

@bp.route('/check_guess_as_guest', methods=['POST'])
def check_guess_as_guest():
    user_input1 = request.form.get('user_input1', '').strip().lower()
    user_input2 = request.form.get('user_input2', '').strip().lower()

    # Fetch the guest ID and retrieve the word pair
    guest_id = session.get('guest_id')
    word_pair = WordPair.query.filter_by(date_available=datetime.now(pytz.timezone('America/New_York')).date()).first()

    # Debugging - Check if word pair is retrieved
    if not word_pair:
        print("No word pair found for today.")
        return render_template('incorrect_guess_as_guest.html', hints_used=session.get('hints_used', 0))

    word1_correct = user_input1 == word_pair.word1.lower()
    word2_correct = user_input2 == word_pair.word2.lower()

    word1_synonyms = [word_pair.word1_synonym1.lower(), word_pair.word1_synonym2.lower()]
    word2_synonyms = [word_pair.word2_synonym1.lower(), word_pair.word2_synonym2.lower()]

    word1_synonym_correct = user_input1 in word1_synonyms
    word2_synonym_correct = user_input2 in word2_synonyms

    guest_word_pair = GuestUserWordPair.query.filter_by(guest_id=guest_id, word_pair_id=word_pair.id).first()

    # Debugging - Check guest word pair status before updating
    print(
        f"Current statuses before update: word1_status: {guest_word_pair.word1_status}, word2_status: {guest_word_pair.word2_status}")

    guest_word_pair.word1_status = 'correct' if word1_correct else 'synonym' if word1_synonym_correct else 'wrong'
    guest_word_pair.word2_status = 'correct' if word2_correct else 'synonym' if word2_synonym_correct else 'wrong'

    # Debugging - Check guest word pair status after updating
    print(
        f"Updated statuses: word1_status: {guest_word_pair.word1_status}, word2_status: {guest_word_pair.word2_status}")

    # Increment the attempts in the database
    guest_word_pair.attempts += 1
    db.session.commit()

    attempts_used = guest_word_pair.attempts
    hints_used = session.get('hints_used', 0)

    if word1_correct and word2_correct:
        points = 2 if hints_used == 0 else 1
        flash('Correct!', 'success')

        guest_word_pair.used = True
        db.session.commit()

        session.pop('hints_used', None)

        return render_template('correct_guess_as_guest.html', points_awarded=points, attempts=attempts_used,
                               hints_used=hints_used)

    max_attempts = 3
    if attempts_used >= max_attempts:
        flash('You have used all your attempts!', 'danger')
        guest_word_pair.used = True
        db.session.commit()

        session.pop('hints_used', None)  # Clear hints used

        return render_template('game_over_as_guest.html', word1=word_pair.word1, word2=word_pair.word2,
                               hints_used=hints_used)

    return render_template('incorrect_guess_as_guest.html',
                           hints_used=hints_used,
                           word1_status=guest_word_pair.word1_status,
                           word2_status=guest_word_pair.word2_status,
                           user_input1=user_input1,
                           user_input2=user_input2,
                           word1_synonym1=word_pair.word1_synonym1,
                           word1_synonym2=word_pair.word1_synonym2,
                           word2_synonym1=word_pair.word2_synonym1,
                           word2_synonym2=word_pair.word2_synonym2)

def init_app(app):
    app.register_blueprint(bp)
