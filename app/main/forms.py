from wtforms import StringField, SubmitField, PasswordField
from flask.ext.wtf import Form
from wtforms.validators import Required, Length, EqualTo

class LoginForm(Form):
    """
    Login form for /login route
    """
    email = StringField('Enter your email address', validators=[Required()])
    password = PasswordField('Enter your password', validators=[Required()])
    submit = SubmitField('Go!')

class CreateUserForm(Form):
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

class SearchForm(Form):
    """
    Flask-WTF form for the search page
    """
    model_run_name = StringField('Model Run Name')
    # start_datetime = DateTimeField('Start Date/time')
    # end_datetime = DateTimeField('End Date/time')
    submit = SubmitField('Submit')
