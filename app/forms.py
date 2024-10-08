from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email (for account recovery purposes only)', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6, max=20), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class GuestForm(FlaskForm):
    pass


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, max=20)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.'),
        Length(min=6, max=20)
    ])
    submit = SubmitField('Reset Password')

class PlayForm(FlaskForm):
    pass

class CheckGuessForm(FlaskForm):
    user_input1 = StringField('First word', validators=[DataRequired()])
    user_input2 = StringField('Second word', validators=[DataRequired()])
    submit = SubmitField('Submit')