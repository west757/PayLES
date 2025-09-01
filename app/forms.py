from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField, StringField

class FormSubmitSingle(FlaskForm):
    submit_single_input = FileField('Drop LES here')
    submit_single_button = SubmitField('Submit')

class FormSubmitJoint(FlaskForm):
    submit_joint_input_1 = FileField('Upload Member 1 LES')
    submit_joint_input_2 = FileField('Upload Member 2 LES')
    submit_joint_button = SubmitField('Submit')

class FormSubmitCustom(FlaskForm):
    custom_grade = SelectField('Grade', choices=[])
    custom_zip_code = StringField('Zip Code')
    custom_home_of_record = SelectField('Home of Record', choices=[])
    custom_dependents = StringField('Dependents')
    custom_federal_filing_status = SelectField('Federal Filing Status', choices=[
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Head of Household', 'Head of Household')
    ])
    custom_state_filing_status = SelectField('State Filing Status', choices=[
        ('Single', 'Single'),
        ('Married', 'Married')
    ])
    custom_sgli_coverage = SelectField('SGLI Coverage', choices=[])
    custom_combat_zone = SelectField('Combat Zone', choices=[
        ('No', 'No'),
        ('Yes', 'Yes')
    ])
    submit_custom_button = SubmitField('Submit')

