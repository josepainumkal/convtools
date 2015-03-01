from wtforms import StringField, SubmitField
from wtforms.validators import Required, url
from flask_wtf import Form
from flask_wtf.html5 import URLField


class ResourceForm(Form):
    """
    Resource contribution form. Info from this is passed to the VW
    adaptor and creates a new model run in the virtual watershed.
    Scientist name is also required, but handled using current_user
    since share blueprint requires login.
    """
    title = StringField('Unique resource title (ex. Dry Creek iSNOBAL '
            'Data)', validators=[Required()])

    description = StringField('Describe your new data resource',
                              validators=[Required()])

    keywords = StringField('Keywords, separated by commas',
                           validators=[Required()])

    url = URLField('Resource URL. Leave blank if you will upload to the '
                   'virtual watershed.',
                   validators=[url()])

    submit = SubmitField('Share your resource!')
