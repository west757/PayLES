from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField, StringField

class FormSingleLES(FlaskForm):
    single_les_input = FileField('Drop LES here')
    submit_single_les = SubmitField('Submit')

class FormJointLES(FlaskForm):
    joint_les_input_1 = FileField('Upload Member 1 LES')
    joint_les_input_2 = FileField('Upload Member 2 LES')
    submit_joint_les = SubmitField('Submit')

class FormWithoutLES(FlaskForm):
    month = SelectField('Month', choices=[])
    year = SelectField('Year', choices=[])
    grade = SelectField('Grade', choices=[])
    zip_code = StringField('Zip Code')
    home_of_record = SelectField('Home of Record', choices=[])
    dependents = StringField('Dependents')
    federal_filing_status = SelectField('Federal Filing Status', choices=[
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Head of Household', 'Head of Household')
    ])
    state_filing_status = SelectField('State Filing Status', choices=[
        ('Single', 'Single'),
        ('Married', 'Married')
    ])
    sgli_coverage = SelectField('SGLI Coverage', choices=[])
    submit_without_les = SubmitField('Submit')

