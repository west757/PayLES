from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField

class FormSingleLES(FlaskForm):
    les_input = FileField('Drop LES here')
    submit_single_les = SubmitField('Submit LES')

class FormJointLES(FlaskForm):
    joint_les_1 = FileField('Drop Member 1 LES')
    joint_les_2 = FileField('Drop Member 2 LES')
    submit_joint_les = SubmitField('Submit Both LES')

class FormWithoutLES(FlaskForm):
    grade = SelectField('Grade', choices=[('E1', 'E1'), ('E2', 'E2')])
    submit_without_les = SubmitField('Submit Without LES')

class FormExampleLES(FlaskForm):
    submit_example_les = SubmitField('Submit Example LES')
