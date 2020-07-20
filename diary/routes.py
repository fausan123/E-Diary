from flask import Flask, render_template, url_for, flash, redirect, request
from diary.forms import RegistrationForm, LoginForm, EntryForm, UpdateForm, RequestResetForm, ResetPasswordForm, KinRequestResetForm
from diary import app, db, bcrypt, mail
from diary.models import User, Entry
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
import datetime

@app.route("/")
@app.route("/home")
def home():
    users = User.query.all()
    for user in users:
        today = datetime.datetime.now()
        last_date = Entry.query.filter_by(author=user).order_by(Entry.date.desc()).first()
        if last_date:
            if (today.day - last_date.date.day) > 31:
                send_dead_email(user)
    entries = []
    if current_user.is_authenticated:
        entries = Entry.query.filter_by(author=current_user).order_by(Entry.date.desc()).all()
    return render_template("home.html", title='Home', entries=entries)


@app.route("/entry")
def entry():
    return render_template("entry.html", title='Entries')


@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstname=form.firstname.data, lastname=form.lastname.data,
         username=form.username.data, dob=form.dob.data,
         email=form.email.data, kin_email=form.kin_email.data,
         password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.firstname.data} {form.lastname.data}! You may please login', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have been logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/contact")
def contact():
    return render_template("contact.html", title='Contact')

@app.route("/newentry", methods=['GET', 'POST'])
def newentry():
    form = EntryForm()
    if form.validate_on_submit():
        entry = Entry(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(entry)
        db.session.commit()
        flash('Your entry has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('newentry.html', title='New Entry', form=form)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.kin_email = form.kin_email.data
        db.session.commit()
        flash('Your details has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.kin_email.data = current_user.kin_email
    return render_template('account.html', title='Account', form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('E-Diary - Password Reset Request', sender='fausan.sanu01@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request simply ignore this message and no changes will be made.
'''
    mail.send(msg)

def send_dead_email(user):
    msg = Message(f'E-Diary of { user.firstname } { user.lastname }', sender='fausan.sanu01@gmail.com', recipients=[user.email, user.kin_email])
    msg.body = f'''Since { user.firstname }'s E-Diary account has been inactive for a month,
    we are sending this mail to access his account as he had given your mail id has "mail of kin".

    email = { user.email }
    You can access the account by reseting the password by following this link:
    { url_for('kin_reset_request', _external=True) }

    '''
    mail.send(msg)

def send_kinreset_email(user):
    token = user.get_reset_token()
    msg = Message('E-Diary - Password Reset Request', sender='fausan.sanu01@gmail.com', recipients=[user.kin_email])
    msg.body = f'''To reset your password visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request simply ignore this message and no changes will be made.
'''
    mail.send(msg)

@app.route("/kin_reset_password", methods=['GET', 'POST'])
def kin_reset_request():
    form = KinRequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.user_email.data).first()
        send_kinreset_email(user)
        flash('An email has been sent to your mail with instructions to reset password', 'info')
        return redirect(url_for('login'))
    return render_template('kin_reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('Please logout and try again', 'danger')
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token is invalid or has been expired', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password reset successful, you may login now', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=form)
