from flask_wtf import FlaskForm
from wtforms import Form, SelectField, DecimalField, IntegerField, StringField, SubmitField, FileField, FieldList, FormField
from wtforms.validators import NumberRange, Length, Regexp

class HomeForm(FlaskForm):
    home_input = FileField('Drop LES here')
    submit_les = SubmitField('Submit LES')
    submit_example = SubmitField('Example LES')


class EntDedAltRowForm(Form):
    header = StringField('Header')
    value_f = DecimalField('Value Future', validators=[NumberRange(min=0, max=9999)])
    value_m = SelectField('Month', choices=[])


class OptionsForm(FlaskForm):
    grade_f = SelectField('Grade Future', choices=[])
    grade_m = SelectField('Grade Month', choices=[])
    zip_code_f = StringField('Zip Code Future', validators=[Length(min=5, max=5), Regexp(r'^\d{5}$', message="Zip code must be 5 digits")])
    zip_code_m = SelectField('Zip Code Month', choices=[])
    home_of_record_f = SelectField('Home of Record Future', choices=[])
    home_of_record_m = SelectField('Home of Record Month', choices=[])
    federal_filing_status_f = SelectField('Federal Filing Status Future', choices=[])
    federal_filing_status_m = SelectField('Federal Filing Status Month', choices=[])
    state_filing_status_f = SelectField('State Filing Status Future', choices=[])
    state_filing_status_m = SelectField('State Filing Status Month', choices=[])
    dependents_f = IntegerField('Dependents Future', validators=[NumberRange(min=0, max=9)])
    dependents_m = SelectField('Dependents Month', choices=[])
    sgli_coverage_f = SelectField('SGLI Coverage Future', choices=[])
    sgli_coverage_m = SelectField('SGLI Coverage Month', choices=[])
    combat_zone_f = SelectField('Combat Zone Future', choices=[])
    combat_zone_m = SelectField('Combat Zone Month', choices=[])

    trad_tsp_base_rate_f = IntegerField('Trad TSP Base Rate Future', validators=[NumberRange(min=0, max=84)])
    trad_tsp_base_rate_m = SelectField('Trad TSP Base Rate Month', choices=[])
    roth_tsp_base_rate_f = IntegerField('Roth TSP Base Rate Future', validators=[NumberRange(min=0, max=60)])
    roth_tsp_base_rate_m = SelectField('Roth TSP Base Rate Month', choices=[])
    trad_tsp_specialty_rate_f = IntegerField('Specialty Rate Future', validators=[NumberRange(min=0, max=100)])
    trad_tsp_specialty_rate_m = SelectField('Specialty Rate Month', choices=[])
    roth_tsp_specialty_rate_f = IntegerField('Specialty Rate Future', validators=[NumberRange(min=0, max=100)])
    roth_tsp_specialty_rate_m = SelectField('Specialty Rate Month', choices=[])
    trad_tsp_incentive_rate_f = IntegerField('Incentive Rate Future', validators=[NumberRange(min=0, max=100)])
    trad_tsp_incentive_rate_m = SelectField('Incentive Rate Month', choices=[])
    roth_tsp_incentive_rate_f = IntegerField('Incentive Rate Future', validators=[NumberRange(min=0, max=100)])
    roth_tsp_incentive_rate_m = SelectField('Incentive Rate Month', choices=[])
    trad_tsp_bonus_rate_f = IntegerField('Bonus Rate Future', validators=[NumberRange(min=0, max=100)])
    trad_tsp_bonus_rate_m = SelectField('Bonus Rate Month', choices=[])
    roth_tsp_bonus_rate_f = IntegerField('Bonus Rate Future', validators=[NumberRange(min=0, max=100)])
    roth_tsp_bonus_rate_m = SelectField('Bonus Rate Month', choices=[])

    ent_ded_alt_rows = FieldList(FormField(EntDedAltRowForm))
    update_les = SubmitField('Update LES')


class SettingsForm(FlaskForm):
    months_display = SelectField('Months Displayed:', choices=[(str(x), str(x)) for x in range(2, 13)])
