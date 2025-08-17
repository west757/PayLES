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


class SettingsForm(FlaskForm):
    months_display = SelectField('Months Displayed:', choices=[(str(x), str(x)) for x in range(2, 13)])


def build_options_form(PAYDF_TEMPLATE, VARIABLE_TEMPLATE, paydf, col_headers, row_headers, GRADES, DEPENDENTS_MAX, HOME_OF_RECORDS, ROTH_TSP_RATE_MAX, SGLI_RATES,TAX_FILING_TYPES_DEDUCTIONS, TRAD_TSP_RATE_MAX):
    fields = {}
    month_fields = []

    # create form with each option
    for _, row in VARIABLE_TEMPLATE.iterrows():
        if not bool(row['option']):
            continue

        header = row['header']
        varname = row['varname']
        field_type = row['field']
        field_f_name = f"{varname}_f"
        field_m_name = f"{varname}_m"
        validators = []

        if field_type == "select":
            fields[field_f_name] = SelectField(f"{header} Future", choices=[])

        elif field_type == "integer":
            if "trad_tsp" in varname:
                validators.append(NumberRange(min=0, max=TRAD_TSP_RATE_MAX))
            elif "roth_tsp" in varname:
                validators.append(NumberRange(min=0, max=ROTH_TSP_RATE_MAX))
            elif "dependents" in varname:
                validators.append(NumberRange(min=0, max=DEPENDENTS_MAX))
            else:
                validators.append(NumberRange(min=0, max=9999))
            fields[field_f_name] = IntegerField(f"{header} Future", validators=validators)

        elif field_type == "string" and "zip_code" in varname:
            validators = [Length(min=5, max=5), Regexp(r'^\d{5}$', message="Zip code must be 5 digits")]
            fields[field_f_name] = StringField(f"{header} Future", validators=validators)

        fields[field_m_name] = SelectField(f"{header} Month", choices=[])
        month_fields.append(field_m_name)

    fields['ent_ded_alt_rows'] = FieldList(FormField(EntDedAltRowForm))
    fields['update_les'] = SubmitField('Update LES')

    OptionsForm = type('OptionsForm', (FlaskForm,), fields)
    form = OptionsForm()

    # set month choices for all month fields
    month_options = [(m, m) for m in col_headers[2:]]
    for field_m_name in month_fields:
        if hasattr(form, field_m_name):
            getattr(form, field_m_name).choices = month_options


    # set values for each option
    for _, row in VARIABLE_TEMPLATE.iterrows():
        if not bool(row['option']):
            continue

        varname = row['varname']
        header = row['header']
        field_type = row['field']
        field_f_name = f"{varname}_f"

        if field_type == "select" and hasattr(form, field_f_name):
            if varname == "grade":
                getattr(form, field_f_name).choices = [(g, g) for g in GRADES]
            elif varname == "home_of_record":
                getattr(form, field_f_name).choices = [(h, h) for h in HOME_OF_RECORDS]
            elif varname == "federal_filing_status":
                federal_types = list(TAX_FILING_TYPES_DEDUCTIONS.keys())
                getattr(form, field_f_name).choices = [(t, t) for t in federal_types]
            elif varname == "state_filing_status":
                state_types = list(TAX_FILING_TYPES_DEDUCTIONS.keys())[:2]
                getattr(form, field_f_name).choices = [(t, t) for t in state_types]
            elif varname == "sgli_coverage":
                getattr(form, field_f_name).choices = [(str(r['coverage']), str(r['coverage'])) for _, r in SGLI_RATES.iterrows()]
            elif varname == "combat_zone":
                getattr(form, field_f_name).choices = [('No', 'No'), ('Yes', 'Yes')]

        # set default for each option future value
        if hasattr(form, field_f_name) and header in row_headers:
            value = paydf.at[row_headers.index(header), col_headers[2]]
            getattr(form, field_f_name).data = value


    for i in range(19, len(row_headers) - 6):
        header = row_headers[i]
        template_row = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if not template_row.empty and bool(template_row.iloc[0]['option']):
            value = paydf.at[i, col_headers[2]]
            month = col_headers[2]
            
            form.ent_ded_alt_rows.append_entry({
                'header': header,
                'value_f': value,
                'value_m': month
            })

            subform = form.ent_ded_alt_rows[-1]
            subform.value_m.choices = month_options

    return form
