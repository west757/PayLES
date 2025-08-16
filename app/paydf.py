from datetime import datetime
from decimal import Decimal
from flask import session
import io
import pandas as pd
import re

from app import flask_app
from app.utils import (
    validate_calculate_zip_mha,
    validate_home_of_record,
)
from app.calculations import (
    calculate_taxable_income,
    calculate_total_taxes,
    calculate_gross_net_pay,
    calculate_base_pay,
    calculate_bas,
    calculate_bah,
    calculate_federal_taxes,
    calculate_fica_social_security,
    calculate_fica_medicare,
    calculate_sgli,
    calculate_state_taxes,
    calculate_trad_roth_tsp,
)
from app.forms import (
    OptionsForm,
    EntDedAltRowForm,
)

# =========================
# build paydf
# =========================

def build_paydf(PAYDF_TEMPLATE, les_text):
    remove_custom_template_rows(PAYDF_TEMPLATE)
    initial_month = les_text[8][3]
    session['initial_month'] = initial_month
    core_dict = {}

    core_dict = add_variables(core_dict, les_text)
    core_dict = add_ent_ded_alt_rows(PAYDF_TEMPLATE, core_dict, les_text)
    core_dict["Taxable Income"], core_dict["Non-Taxable Income"] = calculate_taxable_income(PAYDF_TEMPLATE, core_dict)
    core_dict["Total Taxes"] = calculate_total_taxes(PAYDF_TEMPLATE, core_dict)
    core_dict["Gross Pay"], core_dict["Net Pay"] = calculate_gross_net_pay(PAYDF_TEMPLATE, core_dict)
    core_dict["Difference"] = Decimal("0.00")

    core_list = [[header, core_dict[header]] for header in core_dict]
    session['core_list'] = core_list
    paydf = pd.DataFrame(core_list, columns=["header", initial_month])

    return paydf


def add_variables(core_dict, les_text):
    try:
        year = int('20' + les_text[8][4])
    except Exception:
        year = 0
    core_dict["Year"] = year

    try:
        grade = les_text[2][1]
    except Exception:
        grade = "Not Found"
    core_dict["Grade"] = grade

    try:
        pay_date = datetime.strptime(les_text[3][2], '%y%m%d')
        les_date = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
        months_in_service = (les_date.year - pay_date.year) * 12 + les_date.month - pay_date.month
    except Exception:
        months_in_service = 0
    core_dict["Months in Service"] = months_in_service

    try:
        zip_code, military_housing_area = validate_calculate_zip_mha(les_text[48][2])
    except Exception:
        zip_code, military_housing_area = "Not Found", "Not Found"
    core_dict["Zip Code"] = zip_code
    core_dict['Military Housing Area'] = military_housing_area

    try:
        home_of_record = validate_home_of_record(les_text[39][1])
    except Exception:
        home_of_record = "Not Found"
    core_dict["Home of Record"] = home_of_record

    try:
        status = les_text[24][1]
        if status == "S":
            federal_filing_status = "Single"
        elif status == "M":
            federal_filing_status = "Married"
        elif status == "H":
            federal_filing_status = "Head of Household"
        else:
            federal_filing_status = "Not Found"
    except Exception:
        federal_filing_status = "Not Found"
    core_dict["Federal Filing Status"] = federal_filing_status

    try:
        status = les_text[42][1]
        if status == "S":
            state_filing_status = "Single"
        elif status == "M":
            state_filing_status = "Married"
        else:
            state_filing_status = "Not Found"
    except Exception:
        state_filing_status = "Not Found"
    core_dict["State Filing Status"] = state_filing_status

    try:
        dependents = int(les_text[53][1])
    except Exception:
        dependents = 0
    core_dict["Dependents"] = dependents

    combat_zone = "No"
    core_dict["Combat Zone"] = combat_zone

    try:
        sgli_coverage = ""
        remarks = les_text[96]

        #join all remark strings into one string
        remarks_str = " ".join(str(item) for item in remarks if isinstance(item, str))
        #uses regex to find the SGLI coverage amount
        match = re.search(r"SGLI COVERAGE AMOUNT IS\s*(\$\d{1,3}(?:,\d{3})*)", remarks_str, re.IGNORECASE)

        if match:
            sgli_coverage = match.group(1)
        else:
            sgli_coverage = "Not Found"
            
    except Exception:
        sgli_coverage = "Not Found"
    core_dict["SGLI Coverage"] = sgli_coverage

    try:
        core_dict["Trad TSP Base Rate"] = int(les_text[60][3])
    except Exception:
        core_dict["Trad TSP Base Rate"] = 0
    try:
        core_dict["Trad TSP Specialty Rate"] = int(les_text[62][3])
    except Exception:
        core_dict["Trad TSP Specialty Rate"] = 0
    try:
        core_dict["Trad TSP Incentive Rate"] = int(les_text[64][3])
    except Exception:
        core_dict["Trad TSP Incentive Rate"] = 0
    try:
        core_dict["Trad TSP Bonus Rate"] = int(les_text[66][3])
    except Exception:
        core_dict["Trad TSP Bonus Rate"] = 0

    try:
        core_dict["Roth TSP Base Rate"] = int(les_text[69][3])
    except Exception:
        core_dict["Roth TSP Base Rate"] = 0
    try:
        core_dict["Roth TSP Specialty Rate"] = int(les_text[71][3])
    except Exception:
        core_dict["Roth TSP Specialty Rate"] = 0
    try:
        core_dict["Roth TSP Incentive Rate"] = int(les_text[73][3])
    except Exception:
        core_dict["Roth TSP Incentive Rate"] = 0
    try:
        core_dict["Roth TSP Bonus Rate"] = int(les_text[75][3])
    except Exception:
        core_dict["Roth TSP Bonus Rate"] = 0

    return core_dict


def add_ent_ded_alt_rows(PAYDF_TEMPLATE, core_dict, les_text):
    headers = PAYDF_TEMPLATE['header'].values
    shortnames = PAYDF_TEMPLATE['shortname'].values
    signs = PAYDF_TEMPLATE['sign'].values
    requireds = PAYDF_TEMPLATE['required'].values
    ent_sections = [les_text[9]]
    ded_alt_sections = [les_text[10], les_text[11]]

    for idx, header in enumerate(headers):
        shortname = shortnames[idx]
        sign = signs[idx]
        required = requireds[idx]
        value = None
        found = False

        sections_to_search = ent_sections if sign == 1 else ded_alt_sections

        # search each relevant section for the header's shortname
        for section in sections_to_search:
            short_words = shortname.split()
            n = len(short_words)

            # find all indices where the shortname matches a sequence in the section
            match_indices = [
                i + n - 1
                for i in range(len(section) - n + 1)
                if ' '.join(section[i:i+n]) == shortname
            ]

            # for each match, look for the first numeric value after the match
            for match_idx in match_indices:
                for j in range(match_idx + 1, len(section)):
                    s = section[j]
                    
                    is_num = (
                        s.replace('.', '', 1).replace('-', '', 1).isdigit()
                        or (s.startswith('-') and s[1:].replace('.', '', 1).isdigit())
                    )

                    if is_num:
                        value = sign * abs(Decimal(s))
                        found = True
                        break
                if found:
                    break
            if found:
                break

        # if not found, assign 0.00 if required, otherwise skip
        if not found and required:
            value = Decimal("0.00")
        elif not found:
            continue

        core_dict[header] = value

    return core_dict


def build_options_form(PAYDF_TEMPLATE, paydf, col_headers, row_headers):
    TAX_FILING_TYPES_DEDUCTIONS = flask_app.config['TAX_FILING_TYPES_DEDUCTIONS']
    form = OptionsForm()

    form.grade_f.choices = [(g, g) for g in flask_app.config['GRADES']]
    form.home_of_record_f.choices = [(h, h) for h in flask_app.config['HOME_OF_RECORDS']]
    federal_types = list(TAX_FILING_TYPES_DEDUCTIONS.keys())
    form.federal_filing_status_f.choices = [(t, t) for t in federal_types]
    state_types = federal_types[:2]
    form.state_filing_status_f.choices = [(t, t) for t in state_types]
    form.sgli_coverage_f.choices = [(str(row['coverage']), str(row['coverage'])) for _, row in flask_app.config['SGLI_RATES'].iterrows()]
    form.combat_zone_f.choices = [('No', 'No'), ('Yes', 'Yes')]

    month_options = [(m, m) for m in col_headers[2:]]
    for field in [
        form.grade_m, form.zip_code_m, form.home_of_record_m, form.federal_filing_status_m,
        form.state_filing_status_m, form.dependents_m, form.sgli_coverage_m, form.combat_zone_m,
        form.trad_tsp_base_rate_m, form.roth_tsp_base_rate_m, form.trad_tsp_specialty_rate_m,
        form.roth_tsp_specialty_rate_m, form.trad_tsp_incentive_rate_m, form.roth_tsp_incentive_rate_m,
        form.trad_tsp_bonus_rate_m, form.roth_tsp_bonus_rate_m
    ]:
        field.choices = month_options

    #set default values
    form.grade_f.data = paydf.at[row_headers.index("Grade"), col_headers[2]]
    form.zip_code_f.data = paydf.at[row_headers.index("Zip Code"), col_headers[2]]
    form.home_of_record_f.data = paydf.at[row_headers.index("Home of Record"), col_headers[2]]
    form.federal_filing_status_f.data = paydf.at[row_headers.index("Federal Filing Status"), col_headers[2]]
    form.state_filing_status_f.data = paydf.at[row_headers.index("State Filing Status"), col_headers[2]]
    form.dependents_f.data = paydf.at[row_headers.index("Dependents"), col_headers[2]]
    form.sgli_coverage_f.data = paydf.at[row_headers.index("SGLI Coverage"), col_headers[2]]
    form.combat_zone_f.data = paydf.at[row_headers.index("Combat Zone"), col_headers[2]]

    form.trad_tsp_base_rate_f.data = paydf.at[row_headers.index("Trad TSP Base Rate"), col_headers[2]]
    form.trad_tsp_specialty_rate_f.data = paydf.at[row_headers.index("Trad TSP Specialty Rate"), col_headers[2]]
    form.trad_tsp_incentive_rate_f.data = paydf.at[row_headers.index("Trad TSP Incentive Rate"), col_headers[2]]
    form.trad_tsp_bonus_rate_f.data = paydf.at[row_headers.index("Trad TSP Bonus Rate"), col_headers[2]]
    form.roth_tsp_base_rate_f.data = paydf.at[row_headers.index("Roth TSP Base Rate"), col_headers[2]]
    form.roth_tsp_specialty_rate_f.data = paydf.at[row_headers.index("Roth TSP Specialty Rate"), col_headers[2]]
    form.roth_tsp_incentive_rate_f.data = paydf.at[row_headers.index("Roth TSP Incentive Rate"), col_headers[2]]
    form.roth_tsp_bonus_rate_f.data = paydf.at[row_headers.index("Roth TSP Bonus Rate"), col_headers[2]]

    for header in row_headers:
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]
        if not match.empty and bool(match.iloc[0]['option']):

            if header in paydf['header'].values:
                value = paydf.loc[paydf['header'] == header, col_headers[2]].values[0]
            else:
                value = 0
            month = col_headers[2]

            form.ent_ded_alt_rows.append_entry({
                'header': header,
                'value_f': value,
                'value_m': month
            })

    return form







# =========================
# expand paydf
# =========================

def expand_paydf(PAYDF_TEMPLATE, paydf, months_display, form, custom_rows=None):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    initial_month = paydf.columns[1]
    month_idx = MONTHS_SHORT.index(initial_month)
    row_headers = paydf['header'].tolist()
    prev_col_dict = {row_headers[i]: paydf.iloc[i, 1] for i in range(len(row_headers))}

    for i in range(1, months_display):
        month_idx = (month_idx + 1) % 12
        next_month = MONTHS_SHORT[month_idx]
        next_col_dict = {}

        update_variables(next_col_dict, prev_col_dict, next_month, form)
        update_ent_rows(PAYDF_TEMPLATE, next_col_dict, prev_col_dict, next_month, form, paydf, custom_rows, col_index=i)
        next_col_dict["Taxable Income"], next_col_dict["Non-Taxable Income"] = calculate_taxable_income(PAYDF_TEMPLATE, next_col_dict)
        update_ded_alt_rows(PAYDF_TEMPLATE, next_col_dict, prev_col_dict, next_month, form, paydf, custom_rows, col_index=i)
        next_col_dict["Total Taxes"] = calculate_total_taxes(PAYDF_TEMPLATE, next_col_dict)
        next_col_dict["Gross Pay"], next_col_dict["Net Pay"] = calculate_gross_net_pay(PAYDF_TEMPLATE, next_col_dict)
        next_col_dict["Difference"] = next_col_dict["Net Pay"] - prev_col_dict["Net Pay"]

        col_list = [next_col_dict.get(header, 0) for header in row_headers]
        paydf[next_month] = col_list
        prev_col_dict = next_col_dict.copy()

    col_headers = paydf.columns.tolist()
    row_headers = paydf['header'].tolist()

    return paydf, col_headers, row_headers


def update_variables(next_col_dict, prev_col_dict, next_month, form):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    VARIABLES_MODALS = flask_app.config['VARIABLES_MODALS']
    TSP_MODALS = flask_app.config['TSP_MODALS']
    headers = list(VARIABLES_MODALS.keys()) + list(TSP_MODALS.keys())

    for header in headers:
        prev_value = prev_col_dict[header]
        form_value = form.get(f"{header.lower().replace(' ', '_')}_f") if form else None
        form_month = form.get(f"{header.lower().replace(' ', '_')}_m") if form else None

        if header == "Year":
            if MONTHS_SHORT.index(next_month) == 0:
                next_col_dict[header] = prev_value + 1
            else:
                next_col_dict[header] = prev_value

        elif header == "Months in Service":
            next_col_dict[header] = prev_value + 1

        elif header == "Military Housing Area":
            zip_code = next_col_dict["Zip Code"]
            zip_code, military_housing_area = validate_calculate_zip_mha(zip_code)
            next_col_dict[header] = military_housing_area
        
        else:
            if form_month == next_month and form_value is not None and str(form_value).strip() != "":
                try:
                    next_col_dict[header] = int(form_value) if str(form_value).isdigit() else form_value
                except Exception:
                    next_col_dict[header] = prev_value
            else:
                next_col_dict[header] = prev_value

    return next_col_dict


def update_ent_rows(PAYDF_TEMPLATE, next_col_dict, prev_col_dict, next_month, form, paydf, custom_rows=None, col_index=1):
    all_ent_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['sign'] == 1]['header']
    ent_rows = [header for header in all_ent_rows if header in paydf['header'].values]

    special_calculations = {
        'Base Pay': calculate_base_pay,
        'BAS': calculate_bas,
        'BAH': calculate_bah,
    }

    for header in ent_rows:
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]
        if header in special_calculations:
            next_col_dict[header] = special_calculations[header](next_col_dict)
        else:
            update_reg_row(next_col_dict, next_month, prev_col_dict, form, header, match, custom_rows, col_index)

    return next_col_dict


def update_ded_alt_rows(PAYDF_TEMPLATE, next_col_dict, prev_col_dict, next_month, form, paydf, custom_rows=None, col_index=1):
    all_ded_alt_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['sign'] == -1]['header']
    ded_alt_rows = [header for header in all_ded_alt_headers if header in paydf['header'].values]

    special_calculations = {
        'Federal Taxes': calculate_federal_taxes,
        'FICA - Social Security': calculate_fica_social_security,
        'FICA - Medicare': calculate_fica_medicare,
        'SGLI Rate': calculate_sgli,
        'State Taxes': calculate_state_taxes,
    }

    for header in ded_alt_rows:
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if header in special_calculations:
            next_col_dict[header] = special_calculations[header](next_col_dict)
        elif header in ["Traditional TSP", "Roth TSP"]:
            trad, roth = calculate_trad_roth_tsp(PAYDF_TEMPLATE, next_col_dict)
            if header == "Traditional TSP":
                next_col_dict["Traditional TSP"] = trad
            else:
                next_col_dict["Roth TSP"] = roth
        else:
            update_reg_row(next_col_dict, next_month, prev_col_dict, form, header, match, custom_rows, col_index)

    return next_col_dict


def update_reg_row(next_col_dict, next_month, prev_col_dict, form, header, match, custom_rows=None, col_index=1):
    if bool(match.iloc[0]['onetime']):
        next_col_dict[header] = Decimal("0.00")
        return next_col_dict

    if bool(match.iloc[0]['custom']) and custom_rows is not None:
        custom_row = next((row for row in custom_rows if row['header'] == header), None)

        if custom_row:
            values = custom_row.get('values', [])

            if (col_index - 1) < len(values):
                next_col_dict[header] = values[col_index - 1]
            elif values:
                next_col_dict[header] = values[-1]
            else:
                next_col_dict[header] = Decimal("0.00")
            return next_col_dict

    varname = match.iloc[0]['varname']
    form_value = form.get(f"{varname}_f") if form else None
    form_month = form.get(f"{varname}_m") if form else None
    prev_value = prev_col_dict[header]

    if form_value is None or str(form_value).strip() == "":
        next_col_dict[header] = prev_value
        return next_col_dict

    if form_month == next_month:
        try:
            next_col_dict[header] = Decimal(str(form_value))
        except Exception:
            next_col_dict[header] = prev_value
    else:
        next_col_dict[header] = prev_value

    return next_col_dict



# =========================
# update custom rows
# =========================

def remove_custom_template_rows(PAYDF_TEMPLATE):
    PAYDF_TEMPLATE.drop(PAYDF_TEMPLATE[PAYDF_TEMPLATE['custom'] == True].index, inplace=True)


def parse_custom_rows(PAYDF_TEMPLATE, form):
    core_list = session.get('core_list', [])

    #read custom rows and set correct sign for values
    custom_rows_json = form.get('custom_rows', '[]')
    custom_rows = pd.read_json(io.StringIO(custom_rows_json)).to_dict(orient='records')
    for row in custom_rows:
        sign = row['sign']
        row['values'] = [Decimal(f"{sign * float(v):.2f}") for v in row['values']]

    #remove custom rows from template and core_list
    remove_custom_template_rows(PAYDF_TEMPLATE)
    core_custom_list = [row for row in core_list if not any(row[0] == cr['header'] for cr in custom_rows)]

    #add custom rows to template
    for row in custom_rows:
        header = row['header']

        PAYDF_TEMPLATE.loc[len(PAYDF_TEMPLATE)] = {
            'header': header,
            'varname': '',
            'shortname': '',
            'longname': '',
            'sign': row['sign'],
            'required': False,
            'onetime': False,
            'tax': row['tax'],
            'option': False,
            'custom': True,
            'modal': ''
        }

    #add custom rows to core_list inserted above first calculation row
    insert_idx = len(core_custom_list) - 6
    for idx, row in enumerate(custom_rows):
        new_row = [row['header'], Decimal("0.00")]
        core_custom_list = core_custom_list[:insert_idx + idx] + [new_row] + core_custom_list[insert_idx + idx:]

    return core_custom_list, custom_rows
