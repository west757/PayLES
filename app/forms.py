from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField, StringField

class FormSubmitSingle(FlaskForm):
    submit_single_input = FileField('')
    submit_single_button = SubmitField('Submit')

class FormSubmitJoint(FlaskForm):
    submit_joint_input_1 = FileField('Upload Member 1 LES')
    submit_joint_input_2 = FileField('Upload Member 2 LES')
    submit_joint_button = SubmitField('Submit')
