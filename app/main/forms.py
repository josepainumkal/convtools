from wtforms import StringField, SubmitField
from flask.ext.wtf import Form


class SearchForm(Form):
    """
    Flask-WTF form for the search page
    """
    model_run_name = StringField('Model Run Name')
    # start_datetime = DateTimeField('Start Date/time')
    # end_datetime = DateTimeField('End Date/time')
    submit = SubmitField('Submit')
