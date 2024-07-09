from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db  # Import the Flask app and the SQLAlchemy db object
from .models import User  # Import the User model
from main import load_word_pair, load_synonyms, move_word_pair_to_used, move_synonyms_to_used, remove_synonyms_from_file, remove_word_pair_from_file
from .forms import RegistrationForm, LoginForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken, please choose another one.', 'danger')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/get_hint')
def get_hint():
    word_pair = load_word_pair()

    if not word_pair:
        return render_template('game_over.html')

    word1, word2 = word_pair
    synonyms_dict = load_synonyms()

    # Get both synonyms for the chosen words
    synonyms_word1 = synonyms_dict.get(word1, ["No synonyms found"])
    synonyms_word2 = synonyms_dict.get(word2, ["No synonyms found"])

    return render_template('second_play.html', word1=word1, word2=word2, synonyms_word1=synonyms_word1, synonyms_word2=synonyms_word2)

@app.route('/play', methods=['POST', 'GET'])
@login_required
def play():
    word_pair = load_word_pair()

    if not word_pair:
        return render_template('game_over.html')

    word1, word2 = word_pair
    synonyms_dict = load_synonyms()

    # Get the first synonym of each word
    synonym_word1 = synonyms_dict.get(word1, ["No synonyms found"])[0]
    synonym_word2 = synonyms_dict.get(word2, ["No synonyms found"])[0]

    return render_template('play.html', word1=word1, word2=word2, synonym_word1=synonym_word1, synonym_word2=synonym_word2)

@app.route('/check_guess', methods=['POST'])
def check_guess():
    user_input1 = request.form.get('user_input1', '').strip().lower()
    user_input2 = request.form.get('user_input2', '').strip().lower()
    word1 = request.form.get('word1', '')
    word2 = request.form.get('word2', '')

    word_pair = (word1, word2)  # Define word_pair here

    if user_input1 == word1 and user_input2 == word2:
        move_word_pair_to_used((word1, word2))
        move_synonyms_to_used(word_pair, load_synonyms())  # Move synonyms to used_synonyms.txt
        remove_synonyms_from_file(word_pair)
        remove_word_pair_from_file((word1, word2))
        return render_template('correct_guess.html')
    else:
        return render_template('incorrect_guess.html')

