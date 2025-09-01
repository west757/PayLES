from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField

class FormSingleLES(FlaskForm):
    single_les_input = FileField('Drop LES here')
    submit_single_les = SubmitField('Submit')

class FormJointLES(FlaskForm):
    joint_les_input_1 = FileField('Upload Member 1 LES')
    joint_les_input_2 = FileField('Upload Member 2 LES')
    submit_joint_les = SubmitField('Submit')

class FormWithoutLES(FlaskForm):
    grade = SelectField('Grade', choices=[('E1', 'E1'), ('E2', 'E2')])
    submit_without_les = SubmitField('Submit')

