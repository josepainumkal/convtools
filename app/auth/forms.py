from flask import redirect, request
from flask.ext.wtf import Form
from wtforms import (StringField,
                     SubmitField,
                     PasswordField,
                     BooleanField,
                     HiddenField,
                     ValidationError)
from wtforms.validators import Required, Length, EqualTo
from urlparse import urlparse, urljoin

from ..models import User


def is_safe_url(target):
    """
    Check if the target has a safe scheme for a page (http or https) and
    that the target's host is identical to the request's host. This assumes
    it's being used within a Flask request context.

    Arguments:
        target (str) URL to inspect
    Returns:
        (bool)
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def get_redirect_target():
    """
    Try to redirect to the 'next' parameter received as a hidden field from
    LoginForm. If that fails, try to redirect to the referrer.

    Returns:
        (str) URL to the redirect target
    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data[1:])

        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class LoginForm(RedirectForm):
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
