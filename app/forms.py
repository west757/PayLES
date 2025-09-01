from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField

class FormSubmitSingle(FlaskForm):
    input_file_single = FileField('')
    button_single = SubmitField('Submit')

class FormSubmitJoint(FlaskForm):
    input_file_joint_1 = FileField('Upload Member 1 LES')
    input_file_joint_2 = FileField('Upload Member 2 LES')
    button_joint = SubmitField('Submit')
