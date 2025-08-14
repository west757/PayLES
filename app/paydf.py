from datetime import datetime
from decimal import Decimal
from flask import session
import json
import pandas as pd
import re

from app import flask_app
from app.utils import (
    calculate_months_in_service,
    find_multiword_matches,
    validate_calculate_zip_mha,
    validate_home_of_record,
)
from app.calculations import (
    calculate_taxable_income,
    calculate_total_taxes,
    calculate_gross_pay,
    calculate_net_pay,
    calculate_difference,
    calculate_base_pay,
    calculate_bas,
    calculate_bah,
    calculate_federal_taxes,
    calculate_fica_social_security,
    calculate_fica_medicare,
    calculate_sgli,
    calculate_state_taxes,
    calculate_traditional_tsp,
    calculate_roth_tsp,
)


# =========================
# build paydf
# =========================

def build_paydf(PAYDF_TEMPLATE, les_text):
    initial_month = les_text[8][3]
    core_dict = {}

    core_dict = add_variables(core_dict, les_text)
    core_dict = add_pay_rows(PAYDF_TEMPLATE, core_dict, les_text)
    core_dict["Taxable Income"], core_dict["Non-Taxable Income"] = calculate_taxable_income(PAYDF_TEMPLATE, core_dict)
    core_dict["Total Taxes"] = calculate_total_taxes(PAYDF_TEMPLATE, core_dict)
    core_dict["Gross Pay"] = calculate_gross_pay(PAYDF_TEMPLATE, core_dict)
    core_dict["Net Pay"] = calculate_net_pay(PAYDF_TEMPLATE, core_dict)
    core_dict["Difference"] = Decimal(0)

    #convert core from dict to ordered list of lists for session variable and dataframe initializing
    core_list = [[header, core_dict[header]] for header in core_dict]
    session['paydf_core'] = core_list
    paydf = pd.DataFrame(core_list, columns=["header", initial_month])

    return paydf, core_list, initial_month


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
        months_in_service = calculate_months_in_service(les_date, pay_date)
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
        ttsp_fields = [int(les_text[60][3]), int(les_text[62][3]), int(les_text[64][3]), int(les_text[66][3])]
        traditional_tsp_rate = next((val for val in ttsp_fields if val > 0), 0)
    except Exception:
        traditional_tsp_rate = 0
    core_dict["Traditional TSP Rate"] = traditional_tsp_rate

    try:
        rtsp_fields = [int(les_text[69][3]), int(les_text[71][3]), int(les_text[73][3]), int(les_text[75][3])]
        roth_tsp_rate = next((val for val in rtsp_fields if val > 0), 0)
    except Exception:
        roth_tsp_rate = 0
    core_dict["Roth TSP Rate"] = roth_tsp_rate

    return core_dict



def add_pay_rows(PAYDF_TEMPLATE, core_dict, les_text):
    for _, row in PAYDF_TEMPLATE.iterrows():
        header = row['header']
        shortname = str(row['shortname'])
        sign = row['sign']
        required = row['required']
        value = None
        found = False

        # entitlements in les_text[9], deductions/allotments in les_text[10] and les_text[11]
        if sign == 1:
            sections = [les_text[9]]
        else:
            sections = [les_text[10], les_text[11]]

        # search to see if shortname is in the section
        for section in sections:
            matches = find_multiword_matches(section, shortname)

            for idx in matches:
                for j in range(idx + 1, len(section)):
                    s = section[j]
                    is_num = s.replace('.', '', 1).replace('-', '', 1).isdigit() or (s.startswith('-') and s[1:].replace('.', '', 1).isdigit())
                    if is_num:
                        value = sign * abs(Decimal(section[j]))
                        found = True
                        break
                if found:
                    break
            if found:
                break

        if not found:
            if required:
                value = 0
            else:
                continue

        core_dict[header] = value

    return core_dict



# =========================
# build options
# =========================

def build_options(PAYDF_TEMPLATE, core_list, initial_month):
    template_options = PAYDF_TEMPLATE[PAYDF_TEMPLATE['option'] == True]
    row_dict = {header: value for header, value in core_list}
    options = []

    # Loop through template options and add to options array if header is in rows
    for _, row in template_options.iterrows():
        header = row['header']
        if header in row_dict:
            value = row_dict[header]
            options.append([header, value, initial_month])

    return options


def update_options(PAYDF_TEMPLATE, paydf, form, initial_month=None):
    """
    Update the options array based on form input.
    This function will be responsible for handling form values and updating options accordingly.
    """
    # Implementation will depend on your form structure and requirements
    pass



# =========================
# expand paydf
# =========================

def expand_paydf(PAYDF_TEMPLATE, paydf, options, months_display, form=None, custom_rows=None):
    if form is None:
        form = {}

    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    initial_month = paydf.columns[1]
    month_idx = MONTHS_SHORT.index(initial_month)
    row_headers = paydf['header'].tolist()

    prev_col_dict = {row_headers[i]: paydf.iloc[i, 1] for i in range(len(row_headers))}

    for i in range(1, months_display):
        month_idx = (month_idx + 1) % 12
        new_month = MONTHS_SHORT[month_idx]
        prev_month = paydf.columns[-1]
        col_dict = {}

        update_variables(paydf, col_dict, new_month, prev_month, form)
        update_entitlements(PAYDF_TEMPLATE, paydf, new_month, form, col_dict, prev_month)

        taxable, nontaxable = calculate_taxable_income(PAYDF_TEMPLATE, col_dict)
        col_dict["Taxable Income"] = taxable
        col_dict["Non-Taxable Income"] = nontaxable

        update_da(PAYDF_TEMPLATE, paydf, new_month, form, col_dict, prev_month)

        col_dict["Total Taxes"] = calculate_total_taxes(PAYDF_TEMPLATE, col_dict)
        col_dict["Gross Pay"] = calculate_gross_pay(PAYDF_TEMPLATE, col_dict)
        col_dict["Net Pay"] = calculate_net_pay(PAYDF_TEMPLATE, col_dict)
        col_dict["Difference"] = calculate_difference(col_dict, prev_col_dict)

        # Assemble col in correct order
        col = [col_dict.get(header, 0) for header in row_headers]
        paydf[new_month] = col

        # Update prev_col_dict for next iteration
        prev_col_dict = col_dict.copy()

    col_headers = paydf.columns.tolist()
    row_headers = paydf['header'].tolist()

    return paydf, col_headers, row_headers, options, months_display




def update_variables(paydf, col_dict, month, prev_month, form):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']

    variable_specs = [
        ("Year", "year_f", "year_m", int, "year"),
        ("Grade", "grade_f", "grade_m", str, None),
        ("Months in Service", "months_in_service_f", "months_in_service_m", int, "mis"),
        ("Zip Code", "zip_code_f", "zip_code_m", str, None),
        ("Military Housing Area", "military_housing_area_f", "military_housing_area_m", str, "mha"),
        ("Home of Record", "home_of_record_f", "home_of_record_m", str, None),
        ("Federal Filing Status", "federal_filing_status_f", "federal_filing_status_m", str, None),
        ("State Filing Status", "state_filing_status_f", "state_filing_status_m", str, None),
        ("Dependents", "dependents_f", "dependents_m", int, None),
        ("Combat Zone", "combat_zone_f", "combat_zone_m", str, None),
        ("SGLI Coverage", "sgli_coverage_f", "sgli_coverage_m", int, None),
        ("Traditional TSP Rate", "traditional_tsp_rate_f", "traditional_tsp_rate_m", int, None),
        ("Roth TSP Rate", "roth_tsp_rate_f", "roth_tsp_rate_m", int, None),
    ]

    def get_prev(header):
        return paydf.at[paydf[paydf['header'] == header].index[0], prev_month]

    for idx, (header, f_field, m_field, cast, special) in enumerate(variable_specs):
        prev = get_prev(header)
        val = form.get(f_field)
        mval = form.get(m_field)
        
        if special == "year":
            if mval == month and val is not None:
                try:
                    col_dict[header] = int(val)
                except Exception:
                    col_dict[header] = prev
            else:
                if MONTHS_SHORT.index(month) == 0 and MONTHS_SHORT.index(prev_month) == 11:
                    col_dict[header] = int(prev) + 1
                else:
                    col_dict[header] = prev

        elif special == "mis":
            if mval == month and val is not None:
                try:
                    col_dict[header] = int(val)
                except Exception:
                    col_dict[header] = prev
            else:
                col_dict[header] = int(prev) + 1

        elif special == "mha":
            # Always recalculate MHA based on current Zip Code
            zip_code = col_dict.get("Zip Code", get_prev("Zip Code"))
            zip_code, military_housing_area = validate_calculate_zip_mha(zip_code)
            col_dict["Zip Code"] = zip_code
            col_dict[header] = military_housing_area

        else:
            if mval == month and val is not None:
                try:
                    col_dict[header] = cast(val)
                except Exception:
                    col_dict[header] = prev
            else:
                col_dict[header] = prev

    return col_dict




def update_entitlements(PAYDF_TEMPLATE, paydf, month, form, col_dict, prev_month):
    paydf_headers = set(paydf['header'].tolist())
    ent_rows = [h for h in PAYDF_TEMPLATE[PAYDF_TEMPLATE['sign'] == 1]['header'].tolist() if h in paydf_headers]
    for header in ent_rows:
        row_match = paydf[paydf['header'] == header]
        if row_match.empty:
            continue

        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]
        if header == 'Base Pay':
            col_dict[header] = calculate_base_pay(col_dict)
        elif header == 'BAS':
            col_dict[header] = calculate_bas(col_dict)
        elif header == 'BAH':
            col_dict[header] = calculate_bah(col_dict)
        else:
            update_eda_rows(paydf, header, match, month, prev_month, form, col_dict)

    return col_dict


def update_da(PAYDF_TEMPLATE, paydf, month, form, col_dict, prev_month):
    da_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['sign'] == -1]['header'].tolist()

    for header in da_rows:
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]
        if header == 'Federal Taxes':
            col_dict[header] = calculate_federal_taxes(col_dict)
        elif header == 'FICA - Social Security':
            col_dict[header] = calculate_fica_social_security(col_dict)
        elif header == 'FICA - Medicare':
            col_dict[header] = calculate_fica_medicare(col_dict)
        elif header == 'SGLI':
            col_dict[header] = calculate_sgli(col_dict)
        elif header == 'State Taxes':
            col_dict[header] = calculate_state_taxes(col_dict)
        elif header == 'Traditional TSP':
            col_dict[header] = calculate_traditional_tsp(col_dict)
        elif header == 'Roth TSP':
            col_dict[header] = calculate_roth_tsp(col_dict)
        else:
            update_eda_rows(paydf, header, match, month, prev_month, form, col_dict)

    return col_dict



def update_eda_rows(paydf, header, match, month, prev_month, form, col_dict):
    if bool(match.iloc[0].get('onetime', False)):
        col_dict[header] = 0
        return col_dict

    varname = match.iloc[0]['varname']
    checkbox_field = f"{varname}_f"
    month_field = f"{varname}_m"
    checked = form.get(checkbox_field)
    checked_month = form.get(month_field)

    # Use previous value from paydf for this header and prev_month
    prev_row = paydf[paydf['header'] == header]
    if not prev_row.empty:
        prev_value = prev_row[prev_month].values[0]
    else:
        prev_value = 0

    if checked_month == month and checked:
        col_dict[header] = prev_value
    else:
        col_dict[header] = 0

    return col_dict


# =========================
# update custom rows
# =========================

def remove_custom_template_rows(PAYDF_TEMPLATE):
    PAYDF_TEMPLATE.drop(PAYDF_TEMPLATE[PAYDF_TEMPLATE['custom'] == True].index, inplace=True)


def parse_custom_rows(custom_rows_json):
    custom_rows = []

    if custom_rows_json:
        custom_rows = json.loads(custom_rows_json)

        if isinstance(custom_rows, dict):
            custom_rows = [custom_rows]

        for row in custom_rows:
            row['values'] = [Decimal(v) if v not in [None, ""] else Decimal(0) for v in row['values']]

            if row.get('type') == 'D':
                row['values'] = [-abs(v) for v in row['values']]

            row['tax'] = row.get('tax', False)
    return custom_rows


def add_custom_template_rows(PAYDF_TEMPLATE, custom_rows):
    existing_headers = set(PAYDF_TEMPLATE['header'].values)
    
    for row in custom_rows:
        header = row['header']

        if header in existing_headers:
            header = f"{header}_unique"

        PAYDF_TEMPLATE.loc[len(PAYDF_TEMPLATE)] = {
            'header': header,
            'varname': '',
            'shortname': '',
            'longname': '',
            'sign': row.get('sign', 1),
            'required': False,
            'onetime': False,
            'tax': row['tax'],
            'option': False,
            'custom': True,
            'modal': ''
        }
        row['header'] = header
        existing_headers.add(header)


def add_custom_row(paydf, custom_rows):
    first_month_col = paydf.columns[1]

    for row in custom_rows:
        if first_month_col:
            paydf.loc[len(paydf)] = [row['header'], 0]
        else:
            paydf.loc[len(paydf)] = [row['header']]
    return paydf