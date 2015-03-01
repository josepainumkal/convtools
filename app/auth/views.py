from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import RegistrationForm, LoginForm
from .. import db
from ..models import User
from ..email import send_email

@auth.before_app_request
def before_request():
    """
    Make sure that an unconfirmed person does not log in
    """
    if current_user.is_authenticated() \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':

        print "in before_app_request"
        print current_user.confirmed

        return redirect(url_for('auth.unconfirmed'))



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print type(user)
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.index'))

    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    "Create a new user"

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(name=form.name.data,
                    affiliation=form.affiliation.data,
                    state=form.state.data,
                    city=form.city.data,
                    email=form.email.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm',
                   user=user, token=token)

        flash('A confirmation email has been sent to you. Please click the '
              'link to be confirm your account and log in.')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your account',
               'auth/email/confirm',
               user=current_user,
               token=token)

    flash('A new confirmation email has been sent to you.')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        print "user is confirmed"
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        print "been confirmed"
        flash('You have confirmed your account. Thanks!')
    else:
        print "invalid!"
        flash('The confirmation link is invalid or has expired')

    return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():

    if current_user.is_anonymous() or current_user.confirmed:
        return redirect('main.index')

    return render_template('auth/unconfirmed.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
