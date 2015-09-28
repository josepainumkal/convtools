from wtforms import StringField, SubmitField
from flask.ext.wtf import Form


class SearchForm(Form):
    """
    Flask-WTF form for the search page
    """
    model_run_name = StringField('')
    researcher_name = StringField('Researcher Name')
    keywords = StringField('Keyword')
    description = StringField('Description')
    # start_datetime = DateTimeField('Start Date/time')
    # end_datetime = DateTimeField('End Date/time')
    #submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

    def validate(self):
        '''
            At least one field needs to be filled up by user
        '''
        valid = False
        for field in self:
            print 'field', field.data
            if field.data:
                valid = True
                break
        return valid