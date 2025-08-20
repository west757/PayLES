from datetime import datetime
from decimal import Decimal
from flask import session
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

# =========================
# build budget
# =========================

def build_budget(les_text):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']

    try:
        month = les_text[8][3]
        if month not in MONTHS_SHORT:
            raise ValueError(f"Error: les_text[8][3], '{month}', is not in MONTHS_SHORT")
    except Exception as e:
        raise Exception(f"Error determining initial month: {e}")

    budget_core = []
    budget_core = add_variables(budget_core, les_text, month)
    budget_core = add_ent_ded_alt_rows(budget_core, les_text, month)

    budget_core = calculate_taxable_income(budget_core, month, init=True)
    budget_core = calculate_total_taxes(budget_core, month, init=True)
    budget_core = calculate_gross_net_pay(budget_core, month, init=True)
    budget_core.append({'header': 'Difference', month: Decimal("0.00")})

    return budget_core


def add_variables(budget_core, les_text, month):
    VARIABLE_TEMPLATE = flask_app.config['VARIABLE_TEMPLATE']

    try:
        year = int('20' + les_text[8][4])
    except Exception:
        year = 0
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Year', year, month))

    try:
        pay_date = datetime.strptime(les_text[3][2], '%y%m%d')
        les_date = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
        months_in_service = (les_date.year - pay_date.year) * 12 + les_date.month - pay_date.month
    except Exception:
        months_in_service = 0
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Months in Service', months_in_service, month))

    try:
        grade = les_text[2][1]
    except Exception:
        grade = "Not Found"
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Grade', grade, month))

    try:
        zip_code, military_housing_area = validate_calculate_zip_mha(les_text[48][2])
    except Exception:
        zip_code, military_housing_area = "Not Found", "Not Found"
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Zip Code', zip_code, month))
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Military Housing Area', military_housing_area, month))

    try:
        home_of_record = validate_home_of_record(les_text[39][1])
    except Exception:
        home_of_record = "Not Found"
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Home of Record', home_of_record, month))

    try:
        dependents = int(les_text[53][1])
    except Exception:
        dependents = 0
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Dependents', dependents, month))

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
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Federal Filing Status', federal_filing_status, month))

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
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'State Filing Status', state_filing_status, month))


    #POSSIBLY SIMPLIFY AND UPDATE AFTER CAPTURING SGLI
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
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'SGLI Coverage', sgli_coverage, month))

    combat_zone = "No"
    budget_core.append(add_row(VARIABLE_TEMPLATE, 'Combat Zone', combat_zone, month))

    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'TSP YTD Deductions', Decimal(str(les_text[78][2])), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'TSP YTD Deductions', Decimal("0.00"), month))

    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Trad TSP Base Rate', int(les_text[60][3]), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Trad TSP Base Rate', 0, month))
    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Trad TSP Specialty Rate', int(les_text[62][3]), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Trad TSP Specialty Rate', 0, month))
    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Trad TSP Incentive Rate', int(les_text[64][3]), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Trad TSP Incentive Rate', 0, month))
    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Trad TSP Bonus Rate', int(les_text[66][3]), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Trad TSP Bonus Rate', 0, month))

    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Roth TSP Base Rate', int(les_text[69][3]), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Roth TSP Base Rate', 0, month))
    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Roth TSP Specialty Rate', int(les_text[71][3]), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Roth TSP Specialty Rate', 0, month))
    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Roth TSP Incentive Rate', int(les_text[73][3]), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Roth TSP Incentive Rate', 0, month))
    try:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Roth TSP Bonus Rate', int(les_text[75][3]), month))
    except Exception:
        budget_core.append(add_row(VARIABLE_TEMPLATE, 'Roth TSP Bonus Rate', 0, month))

    return budget_core


def add_ent_ded_alt_rows(budget_core, les_text, month):
    BUDGET_TEMPLATE = flask_app.config['BUDGET_TEMPLATE']

    print(les_text[9])
    ents = parse_pay_section(les_text[9])
    deds = parse_pay_section(les_text[10])
    alts = parse_pay_section(les_text[11])

    #combine ents, deds, and alts into a single dictionary and apply sign
    ent_ded_alt_dict = {}
    for section, sign in zip([ents, deds, alts], [1, -1, -1]):
        for item in section:
            ent_ded_alt_dict[item['header'].upper()] = sign * item['value']

    for _, row in BUDGET_TEMPLATE.iterrows():
        header = row['header']
        required = row['required']
        lesname = row['lesname']

        if lesname in ent_ded_alt_dict:
            value = ent_ded_alt_dict[lesname]
        elif required:
            value = Decimal("0.00")
        else:
            continue

        budget_core.append(add_row(BUDGET_TEMPLATE, header, value, month))

    return budget_core


def parse_pay_section(les_text):
    text_list = les_text[3:-1] 
    results = []
    i = 0

    def is_number(s):
        return bool(re.match(r"^-?\d+(\.\d{1,2})?$", s))

    while i < len(text_list):
        header_parts = []
        # Collect header parts, skipping single-character labels
        while i < len(text_list) and not is_number(text_list[i]):
            if len(text_list[i]) == 1 and text_list[i].isalpha():
                i += 1
                continue
            header_parts.append(text_list[i])
            i += 1

        if not header_parts or i >= len(text_list):
            break

        value_str = text_list[i]
        try:
            value = Decimal(value_str)
        except Exception:
            value = Decimal("0.00")

        header = " ".join(header_parts)
        if header.upper() != "TOTAL" and header != "":
            results.append({"header": header, "value": value})
        i += 1

    return results


def is_number(s):
    return bool(re.match(r"^-?\d+(\.\d{1,2})?$", s))


def add_row(TEMPLATE, header, value, month):
    ROW_METADATA = flask_app.config['ROW_METADATA']
    row_data = TEMPLATE[TEMPLATE['header'] == header]
    metadata = {}
    
    for col in ROW_METADATA:
        if col in row_data.columns:
            metadata[col] = row_data.iloc[0][col]

    row = {'header': header}
    row.update(metadata)
    row[month] = value
    return row


# =========================
# expand budget
# =========================

def expand_budget(BUDGET_TEMPLATE, VARIABLE_TEMPLATE, budget, months_display, form):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    initial_month = budget.columns[1]
    month_idx = MONTHS_SHORT.index(initial_month)
    row_headers = budget['header'].tolist()
    prev_col_dict = {row_headers[i]: budget.iloc[i, 1] for i in range(len(row_headers))}

    for i in range(1, months_display):
        month_idx = (month_idx + 1) % 12
        next_month = MONTHS_SHORT[month_idx]
        next_col_dict = {}

        update_variables(VARIABLE_TEMPLATE, next_col_dict, prev_col_dict, next_month, form)
        update_ent_rows(BUDGET_TEMPLATE, next_col_dict, prev_col_dict, next_month, form, budget, col_index=i)
        next_col_dict["Taxable Income"], next_col_dict["Non-Taxable Income"] = calculate_taxable_income(BUDGET_TEMPLATE, next_col_dict)
        update_ded_alt_rows(BUDGET_TEMPLATE, VARIABLE_TEMPLATE, next_col_dict, prev_col_dict, next_month, form, budget, col_index=i)
        next_col_dict["TSP YTD Deductions"] = calculate_tsp_ytd_deductions(next_col_dict, prev_col_dict)
        next_col_dict["Total Taxes"] = calculate_total_taxes(BUDGET_TEMPLATE, next_col_dict)
        next_col_dict["Gross Pay"], next_col_dict["Net Pay"] = calculate_gross_net_pay(BUDGET_TEMPLATE, next_col_dict)
        next_col_dict["Difference"] = next_col_dict["Net Pay"] - prev_col_dict["Net Pay"]

        col_list = [next_col_dict.get(header, 0) for header in row_headers]
        budget[next_month] = col_list
        prev_col_dict = next_col_dict.copy()

    col_headers = budget.columns.tolist()
    row_headers = budget['header'].tolist()

    return budget, col_headers, row_headers


def update_variables(VARIABLE_TEMPLATE, next_col_dict, prev_col_dict, next_month, form):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    variable_tsp_rows = VARIABLE_TEMPLATE[VARIABLE_TEMPLATE['type'].isin(['v', 't'])]

    for _, row in variable_tsp_rows.iterrows():
        header = row['header']
        varname = row['varname']
        field_f = f"{varname}_f"
        field_m = f"{varname}_m"

        prev_value = prev_col_dict.get(header)
        form_value = form.get(field_f) if form else None
        form_month = form.get(field_m) if form else None

        if header == "Year":
            if MONTHS_SHORT.index(next_month) == 0:
                next_col_dict[header] = prev_value + 1
            else:
                next_col_dict[header] = prev_value

        elif header == "Months in Service":
            next_col_dict[header] = prev_value + 1

        elif header == "Military Housing Area":
            zip_code = next_col_dict.get("Zip Code", "")
            zip_code, military_housing_area = validate_calculate_zip_mha(zip_code)
            next_col_dict[header] = military_housing_area

        elif header == "TSP YTD Deductions":
            next_col_dict[header] = Decimal("0.00")

        else:
            if form_month == next_month and form_value is not None and str(form_value).strip() != "":
                try:
                    if str(form_value).isdigit() and header != "Zip Code":
                        next_col_dict[header] = int(form_value)
                    else:
                        next_col_dict[header] = form_value
                except Exception:
                    next_col_dict[header] = prev_value
            else:
                next_col_dict[header] = prev_value

    if next_col_dict["Trad TSP Base Rate"] == 0:
        next_col_dict["Trad TSP Specialty Rate"] = 0
        next_col_dict["Trad TSP Incentive Rate"] = 0
        next_col_dict["Trad TSP Bonus Rate"] = 0
    if next_col_dict["Roth TSP Base Rate"] == 0:
        next_col_dict["Roth TSP Specialty Rate"] = 0
        next_col_dict["Roth TSP Incentive Rate"] = 0
        next_col_dict["Roth TSP Bonus Rate"] = 0

    return next_col_dict


def update_ent_rows(BUDGET_TEMPLATE, next_col_dict, prev_col_dict, next_month, form, budget, col_index=1):
    all_ent_rows = BUDGET_TEMPLATE[BUDGET_TEMPLATE['sign'] == 1]['header']
    ent_rows = [header for header in all_ent_rows if header in budget['header'].values]

    special_calculations = {
        'Base Pay': calculate_base_pay,
        'BAS': calculate_bas,
        'BAH': calculate_bah,
    }

    for header in ent_rows:
        match = BUDGET_TEMPLATE[BUDGET_TEMPLATE['header'] == header]
        if header in special_calculations:
            next_col_dict[header] = special_calculations[header](next_col_dict)
        else:
            update_reg_row(next_col_dict, next_month, prev_col_dict, form, header, match, col_index)

    return next_col_dict


def update_ded_alt_rows(BUDGET_TEMPLATE, VARIABLE_TEMPLATE, next_col_dict, prev_col_dict, next_month, form, budget, col_index=1):
    all_ded_alt_headers = BUDGET_TEMPLATE[BUDGET_TEMPLATE['sign'] == -1]['header']
    ded_alt_rows = [header for header in all_ded_alt_headers if header in budget['header'].values]

    special_calculations = {
        'Federal Taxes': calculate_federal_taxes,
        'FICA - Social Security': calculate_fica_social_security,
        'FICA - Medicare': calculate_fica_medicare,
        'SGLI Rate': calculate_sgli,
        'State Taxes': calculate_state_taxes,
    }

    for header in ded_alt_rows:
        match = BUDGET_TEMPLATE[BUDGET_TEMPLATE['header'] == header]

        if header in special_calculations:
            next_col_dict[header] = special_calculations[header](next_col_dict)
        elif header in ["Traditional TSP", "Roth TSP"]:
            trad, roth = calculate_trad_roth_tsp(BUDGET_TEMPLATE, VARIABLE_TEMPLATE, next_col_dict)
            if header == "Traditional TSP":
                next_col_dict["Traditional TSP"] = trad
            else:
                next_col_dict["Roth TSP"] = roth
        else:
            update_reg_row(next_col_dict, next_month, prev_col_dict, form, header, match, col_index)

    return next_col_dict


def update_reg_row(next_col_dict, next_month, prev_col_dict, form, header, match, col_index=1):
    if bool(match.iloc[0]['onetime']):
        next_col_dict[header] = Decimal("0.00")
        return next_col_dict

    varname = match.iloc[0]['varname']
    form_value = form.get(f"{varname}_f") if form else None
    form_month = form.get(f"{varname}_m") if form else None
    prev_value = prev_col_dict[header]
    sign = match.iloc[0]['sign']

    if form_value is None or str(form_value).strip() == "":
        next_col_dict[header] = prev_value
        return next_col_dict

    if form_month == next_month:
        try:
            value = sign * Decimal(str(form_value))
            next_col_dict[header] = value.quantize(Decimal("0.00"))
        except Exception:
            next_col_dict[header] = prev_value
    else:
        next_col_dict[header] = prev_value

    return next_col_dict


def calculate_tsp_ytd_deductions(next_col_dict, prev_col_dict):
    trad = abs(next_col_dict["Traditional TSP"])
    roth = abs(next_col_dict["Roth TSP"])
    is_new_year = next_col_dict["Year"] != prev_col_dict["Year"]

    if is_new_year:
        return trad + roth
    else:
        prev_ytd = prev_col_dict["TSP YTD Deductions"]
        return prev_ytd + trad + roth
    