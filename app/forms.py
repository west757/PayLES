from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField

class HomeForm(FlaskForm):
    home_input = FileField('Drop LES here')
    submit_les = SubmitField('Submit LES')
    submit_example = SubmitField('Example LES')
