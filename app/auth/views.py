from flask import render_template, flash, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .forms import RegistrationForm, LoginForm
from .. import db
from ..models import User


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
def create_user():
    "Create a new user"
    form = RegistrationForm()

    print form.validate_on_submit()
    if form.validate_on_submit():
        user = User(name=form.name.data,
                    affiliation=form.affiliation.data,
                    state=form.state.data,
                    city=form.city.data,
                    email=form.email.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('You can now log in')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
