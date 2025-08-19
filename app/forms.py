from flask_wtf import FlaskForm
from wtforms import Form, SelectField, DecimalField, IntegerField, StringField, SubmitField, FileField, FieldList, FormField
from wtforms.validators import NumberRange, Length, Regexp

class HomeForm(FlaskForm):
    home_input = FileField('Drop LES here')
    submit_les = SubmitField('Submit LES')
    submit_example = SubmitField('Example LES')


class SettingsForm(FlaskForm):
    months_display = SelectField('Months Displayed:', choices=[(str(x), str(x)) for x in range(2, 13)])
