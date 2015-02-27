from wtforms import (StringField, SubmitField, PasswordField, ValidationError,
                     BooleanField)
from ..models import User
from flask.ext.wtf import Form
from wtforms.validators import Required, Length, EqualTo


class LoginForm(Form):
    """
    Login form for /login route
    """
    email = StringField('Enter your email address', validators=[Required()])
    password = PasswordField('Enter your password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    """
    Create a new user at /create
    """
    name = StringField('Full Name', validators=[Required()])
    affiliation = StringField('Academic institution', validators=[Required()])
    state = StringField('State', validators=[Required()])
    city = StringField('City', validators=[Required()])
    email = StringField('e-mail', validators=[Required()])

    password = \
        PasswordField('Password',
                      validators=[Length(min=6),
                                  Required(),
                                  EqualTo('confirm',
                                          message='Passwords must match')])

    confirm = PasswordField('Repeat Password')

    submit = SubmitField('Finish')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
