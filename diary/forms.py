from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from diary.models import User, Entry


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=4, max=25)])
    dob = DateTimeField('Date of Birth', format='%d/%m/%Y')
    email = StringField('Email', validators=[DataRequired(), Email()])
    kin_email = StringField('Email of Kin', validators=[
                            DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_kin_email(self, kin_email):
        if kin_email.data == self.email.data:
            raise ValidationError('You are not your own kin!')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered!')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EntryForm(FlaskForm):
    title = StringField('Title', validators=[Optional()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Done')

class UpdateForm(FlaskForm):
    kin_email = StringField('Email of Kin', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    submit = SubmitField('Update')

    def validate_kin_email(self, kin_email):
        if kin_email.data == current_user.email:
            raise ValidationError('You are not your own kin!')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already taken!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is already registered!')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account in this email. Please register!')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class KinRequestResetForm(FlaskForm):
    user_email = StringField('User Email', validators=[DataRequired(), Email()])
    kin_email = StringField('Kin Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_kin_email(self, kin_email):
        user = User.query.filter_by(kin_email=kin_email.data).first()
        if user is None:
            raise ValidationError('There is no account with the given mail as "mail of kin". Please try again!')

    def validate_user_email(self, user_email):
        user = User.query.filter_by(email=user_email.data).first()
        if user is None:
            raise ValidationError('There is no account in this email. Please check the user email!')
