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

def build_budget(BUDGET_TEMPLATE, VARIABLE_TEMPLATE, les_text):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']

    try:
        initial_month = les_text[8][3]
        if initial_month not in MONTHS_SHORT:
            raise ValueError(f"Error: les_text[8][3], '{initial_month}', is not in MONTHS_SHORT")
    except Exception as e:
        raise Exception(f"Error determining initial month: {e}")

    months = [initial_month]

    budget_core = add_variables(budget_core, les_text)
    budget_core = add_ent_ded_alt_rows(BUDGET_TEMPLATE, budget_core, les_text)
    budget_core["Taxable Income"], budget_core["Non-Taxable Income"] = calculate_taxable_income(BUDGET_TEMPLATE, budget_core)
    budget_core["Total Taxes"] = calculate_total_taxes(BUDGET_TEMPLATE, budget_core)
    budget_core["Gross Pay"], budget_core["Net Pay"] = calculate_gross_net_pay(BUDGET_TEMPLATE, budget_core)
    budget_core["Difference"] = Decimal("0.00")

    return budget_core


def populate_metadata(BUDGET_TEMPLATE, VARIABLE_TEMPLATE, header):
    meta = {}

    budget_row = BUDGET_TEMPLATE[BUDGET_TEMPLATE['header'] == header]
    if not budget_row.empty:
        for col in budget_row.columns:
            meta[col] = budget_row.iloc[0][col]

    var_row = VARIABLE_TEMPLATE[VARIABLE_TEMPLATE['header'] == header]
    if not var_row.empty:
        for col in var_row.columns:
            meta[col] = var_row.iloc[0][col]
    return meta


def add_variables(budget_core, les_text):
    try:
        year = int('20' + les_text[8][4])
    except Exception:
        year = 0
    budget_core["Year"] = year

    try:
        pay_date = datetime.strptime(les_text[3][2], '%y%m%d')
        les_date = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
        months_in_service = (les_date.year - pay_date.year) * 12 + les_date.month - pay_date.month
    except Exception:
        months_in_service = 0
    budget_core["Months in Service"] = months_in_service

    try:
        grade = les_text[2][1]
    except Exception:
        grade = "Not Found"
    budget_core["Grade"] = grade

    try:
        zip_code, military_housing_area = validate_calculate_zip_mha(les_text[48][2])
    except Exception:
        zip_code, military_housing_area = "Not Found", "Not Found"
    budget_core["Zip Code"] = zip_code
    budget_core['Military Housing Area'] = military_housing_area

    try:
        home_of_record = validate_home_of_record(les_text[39][1])
    except Exception:
        home_of_record = "Not Found"
    budget_core["Home of Record"] = home_of_record

    try:
        dependents = int(les_text[53][1])
    except Exception:
        dependents = 0
    budget_core["Dependents"] = dependents

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
    budget_core["Federal Filing Status"] = federal_filing_status

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
    budget_core["State Filing Status"] = state_filing_status

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
    budget_core["SGLI Coverage"] = sgli_coverage

    combat_zone = "No"
    budget_core["Combat Zone"] = combat_zone

    try:
        budget_core["TSP YTD Deductions"] = Decimal(str(les_text[78][2]))
    except Exception:
        budget_core["TSP YTD Deductions"] = Decimal("0.00")

    try:
        budget_core["Trad TSP Base Rate"] = int(les_text[60][3])
    except Exception:
        budget_core["Trad TSP Base Rate"] = 0
    try:
        budget_core["Trad TSP Specialty Rate"] = int(les_text[62][3])
    except Exception:
        budget_core["Trad TSP Specialty Rate"] = 0
    try:
        budget_core["Trad TSP Incentive Rate"] = int(les_text[64][3])
    except Exception:
        budget_core["Trad TSP Incentive Rate"] = 0
    try:
        budget_core["Trad TSP Bonus Rate"] = int(les_text[66][3])
    except Exception:
        budget_core["Trad TSP Bonus Rate"] = 0

    try:
        budget_core["Roth TSP Base Rate"] = int(les_text[69][3])
    except Exception:
        budget_core["Roth TSP Base Rate"] = 0
    try:
        budget_core["Roth TSP Specialty Rate"] = int(les_text[71][3])
    except Exception:
        budget_core["Roth TSP Specialty Rate"] = 0
    try:
        budget_core["Roth TSP Incentive Rate"] = int(les_text[73][3])
    except Exception:
        budget_core["Roth TSP Incentive Rate"] = 0
    try:
        budget_core["Roth TSP Bonus Rate"] = int(les_text[75][3])
    except Exception:
        budget_core["Roth TSP Bonus Rate"] = 0

    return budget_core


def add_ent_ded_alt_rows(BUDGET_TEMPLATE, budget_core, les_text):
    headers = BUDGET_TEMPLATE['header'].values
    shortnames = BUDGET_TEMPLATE['shortname'].values
    signs = BUDGET_TEMPLATE['sign'].values
    requireds = BUDGET_TEMPLATE['required'].values
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

        budget_core[header] = value

    return budget_core



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
    