from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField

class FormSingle(FlaskForm):
    input_file_single = FileField('')
    button_single = SubmitField('Submit')
    button_example = SubmitField('View Example')

class FormJoint(FlaskForm):
    input_file_joint1 = FileField('Upload Member 1 LES')
    input_file_joint2 = FileField('Upload Member 2 LES')
    button_joint = SubmitField('Submit')
