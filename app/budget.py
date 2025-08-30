from datetime import datetime
import pandas as pd
import re

from app import flask_app
from app.utils import (
    add_row,
    validate_calculate_zip_mha,
    validate_home_of_record,
    get_months,
)
from app.calculations import (
    calculate_income,
    calculate_tax_exp_net,
    calculate_difference,
    calculate_ytd_rows,
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
    try:
        init_month = les_text[8][3]
        if init_month not in flask_app.config['MONTHS_SHORT']:
            raise ValueError(f"Error: les_text[8][3], '{init_month}', is not in MONTHS_SHORT")
    except Exception as e:
        raise Exception(f"Error determining initial month: {e}")

    budget = []
    budget = add_variables(VARIABLE_TEMPLATE, budget, les_text, init_month)
    budget = add_ent_ded_alt_rows(BUDGET_TEMPLATE, budget, les_text, init_month)
    budget = calculate_income(budget, init_month, init=True, VARIABLE_TEMPLATE=VARIABLE_TEMPLATE)
    budget = calculate_tax_exp_net(budget, init_month, init=True, VARIABLE_TEMPLATE=VARIABLE_TEMPLATE)
    budget = calculate_difference(budget, init_month, init_month, init=True, VARIABLE_TEMPLATE=VARIABLE_TEMPLATE)
    budget = add_ytd_rows(VARIABLE_TEMPLATE, budget, les_text, init_month)

    return budget, init_month


def add_variables(VARIABLE_TEMPLATE, budget, les_text, month):
    try:
        year = int('20' + les_text[8][4])
    except Exception:
        year = 0
    budget.append(add_row(VARIABLE_TEMPLATE, 'Year', month, year))

    try:
        pay_date = datetime.strptime(les_text[3][2], '%y%m%d')
        les_date = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
        months_in_service = (les_date.year - pay_date.year) * 12 + les_date.month - pay_date.month
    except Exception:
        months_in_service = 0
    budget.append(add_row(VARIABLE_TEMPLATE, 'Months in Service', month, months_in_service))

    try:
        grade = les_text[2][1]
    except Exception:
        grade = "Not Found"
    budget.append(add_row(VARIABLE_TEMPLATE, 'Grade', month, grade))

    try:
        zip_code, military_housing_area = validate_calculate_zip_mha(les_text[48][2])
    except Exception:
        zip_code, military_housing_area = "Not Found", "Not Found"
    budget.append(add_row(VARIABLE_TEMPLATE, 'Zip Code', month, zip_code))
    budget.append(add_row(VARIABLE_TEMPLATE, 'Military Housing Area', month, military_housing_area))

    try:
        home_of_record = validate_home_of_record(les_text[39][1])
    except Exception:
        home_of_record = "Not Found"
    budget.append(add_row(VARIABLE_TEMPLATE, 'Home of Record', month, home_of_record))

    try:
        dependents = int(les_text[53][1])
    except Exception:
        dependents = 0
    budget.append(add_row(VARIABLE_TEMPLATE, 'Dependents', month, dependents))

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
    budget.append(add_row(VARIABLE_TEMPLATE, 'Federal Filing Status', month, federal_filing_status))

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
    budget.append(add_row(VARIABLE_TEMPLATE, 'State Filing Status', month, state_filing_status))

    try:
        sgli_coverage = ""
        remarks = les_text[96]

        # join all remark strings into one string
        remarks_str = " ".join(str(item) for item in remarks if isinstance(item, str))
        # uses regex to find the SGLI coverage amount
        match = re.search(r"SGLI COVERAGE AMOUNT IS\s*(\$\d{1,3}(?:,\d{3})*)", remarks_str, re.IGNORECASE)

        if match:
            sgli_coverage = match.group(1)
        else:
            sgli_coverage = "Not Found"
            
    except Exception:
        sgli_coverage = "Not Found"
    budget.append(add_row(VARIABLE_TEMPLATE, 'SGLI Coverage', month, sgli_coverage))

    combat_zone = "No"
    budget.append(add_row(VARIABLE_TEMPLATE, 'Combat Zone', month, combat_zone))

    tsp_rate_rows = [
        ("Trad TSP Base Rate", 60),
        ("Trad TSP Specialty Rate", 62),
        ("Trad TSP Incentive Rate", 64),
        ("Trad TSP Bonus Rate", 66),
        ("Roth TSP Base Rate", 69),
        ("Roth TSP Specialty Rate", 71),
        ("Roth TSP Incentive Rate", 73),
        ("Roth TSP Bonus Rate", 75),
    ]

    for header, idx in tsp_rate_rows:
        try:
            value = int(les_text[idx][3])
        except Exception:
            value = 0
        budget.append(add_row(VARIABLE_TEMPLATE, header, month, value))

    return budget


def add_ent_ded_alt_rows(BUDGET_TEMPLATE, budget, les_text, month):
    ents = parse_pay_section(les_text[9])
    deds = parse_pay_section(les_text[10])
    alts = parse_pay_section(les_text[11])

    # combine all ents/deds/alts into a single dictionary
    ent_ded_alt_dict = {}
    for item in ents + deds + alts:
        ent_ded_alt_dict[item['header'].upper()] = item['value']

    for _, row in BUDGET_TEMPLATE.iterrows():
        header = row['header']
        sign = row['sign']
        required = row['required']
        lesname = row['lesname']

        if lesname in ent_ded_alt_dict:
            value = round(sign * ent_ded_alt_dict[lesname], 2)
        elif required:
            value = 0.00
        else:
            continue

        budget.append(add_row(BUDGET_TEMPLATE, header, month, value))

    return budget


def parse_pay_section(les_text):
    text_list = les_text[3:-1] 
    results = []
    i = 0

    def is_number(s):
        return bool(re.match(r"^-?\d+(\.\d{1,2})?$", s))

    while i < len(text_list):
        header_parts = []
        # collect header parts, skipping single-character labels
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
            value = float(value_str)
        except Exception:
            value = 0.00

        value = round(value, 2)

        header = " ".join(header_parts)
        if header.upper() != "TOTAL" and header != "":
            results.append({"header": header, "value": value})
        i += 1

    return results


def add_ytd_rows(VARIABLE_TEMPLATE, budget, les_text, month):
    remarks = les_text[96]
    remarks_str = " ".join(str(item) for item in remarks if isinstance(item, str))

    ent_match = re.search(r"YTD ENTITLE\s*(\d+\.\d{2})", remarks_str)
    ytd_entitlement = float(ent_match.group(1)) if ent_match else 0.00
    budget.append(add_row(VARIABLE_TEMPLATE, 'YTD Income', month, ytd_entitlement))

    ded_match = re.search(r"YTD DEDUCT\s*(\d+\.\d{2})", remarks_str)
    ytd_deduction = -float(ded_match.group(1)) if ded_match else 0.00
    budget.append(add_row(VARIABLE_TEMPLATE, 'YTD Expenses', month, ytd_deduction))

    try:
        ytd_tsp = float(les_text[78][2])
    except Exception:
        ytd_tsp = 0.00
    budget.append(add_row(VARIABLE_TEMPLATE, 'YTD TSP Contribution', month, ytd_tsp))

    try:
        ytd_charity = float(les_text[56][2])
    except Exception:
        ytd_charity = 0.00
    budget.append(add_row(VARIABLE_TEMPLATE, 'YTD Charity', month, ytd_charity))

    ytd_net_pay = round(ytd_entitlement + ytd_deduction, 2)
    budget.append(add_row(VARIABLE_TEMPLATE, 'YTD Net Pay', month, ytd_net_pay))

    return budget


def init_onetime_rows(BUDGET_TEMPLATE, budget, months):
    for row in budget:
        if row.get('type') in ('e', 'd', 'a'):
            template_row = BUDGET_TEMPLATE[BUDGET_TEMPLATE['header'] == row['header']]
            if template_row.iloc[0]['onetime']:
                for m in months[1:]:
                    row[m] = 0.00
    return budget



# =========================
# update budget months and variables
# =========================

def remove_months(budget, months_num):
    months = get_months(budget)
    months_to_remove = months[months_num:]

    for row in budget:
        for month in months_to_remove:
            if month in row:
                del row[month]
    months = months[:months_num]

    return budget, months


def add_months(budget, latest_month, months_num):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    months = get_months(budget)
    current_num = len(months)
    months_to_add = months_num - current_num
    latest_month_idx = MONTHS_SHORT.index(latest_month)

    for i in range(months_to_add):
        working_month = MONTHS_SHORT[(latest_month_idx + 1 + i) % 12]
        months.append(working_month)
        budget = build_month(budget, months[-2], working_month)  # months[-2] is previous month

    return budget, months


def update_months(budget, months, cell_header=None, cell_month=None, cell_value=None, cell_repeat=False):
    if cell_header is None:
        start_idx = 1
    else:
        start_idx = months.index(cell_month)


    for i in range(start_idx, len(months)):
        prev_month = months[i - 1]
        working_month = months[i]
        budget = build_month(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat)

    return budget


def build_month(budget, prev_month, working_month, cell_header=None, cell_month=None, cell_value=None, cell_repeat=False):
    update_variables(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat)
    update_ent_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat)
    calculate_trad_roth_tsp(budget, working_month)
    calculate_income(budget, working_month)
    update_ded_alt_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat)
    calculate_tax_exp_net(budget, working_month)
    calculate_difference(budget, prev_month, working_month)
    calculate_ytd_rows(budget, prev_month, working_month)
    return budget


def update_variables(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat):
    for row in budget:
        if row.get('type') not in ('v', 't'):
            continue

        prev_value = row.get(prev_month)

        if row['header'] == "Year":
            row[working_month] = prev_value + 1 if working_month == "JAN" else prev_value

        elif row['header'] == "Months in Service":
            row[working_month] = prev_value + 1

        elif row['header'] == "Military Housing Area":
            zip_row = next((r for r in budget if r['header'] == "Zip Code"), None)
            zip_code = zip_row.get(working_month)
            _, military_housing_area = validate_calculate_zip_mha(zip_code)
            row[working_month] = military_housing_area

        elif cell_header is not None and row['header'] == cell_header and (working_month == cell_month or cell_repeat):
            row[working_month] = cell_value

        elif working_month not in row or pd.isna(row[working_month]) or row[working_month] == '' or (isinstance(row[working_month], (list, tuple)) and len(row[working_month]) == 0):
            row[working_month] = row[prev_month]

    # TSP specialty/incentive/bonus zeroing
    tsp_types = [
        ("Trad TSP Base Rate", ["Trad TSP Specialty Rate", "Trad TSP Incentive Rate", "Trad TSP Bonus Rate"]),
        ("Roth TSP Base Rate", ["Roth TSP Specialty Rate", "Roth TSP Incentive Rate", "Roth TSP Bonus Rate"])
    ]
    for base_header, specialty_headers in tsp_types:
        base_row = next((r for r in budget if r['header'] == base_header), None)
        if base_row and base_row.get(working_month, 0) == 0:
            for header in specialty_headers:
                rate_row = next((r for r in budget if r['header'] == header), None)
                if rate_row:
                    rate_row[working_month] = 0


def update_ent_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat):
    special_calculations = {
        'Base Pay': calculate_base_pay,
        'BAS': calculate_bas,
        'BAH': calculate_bah,
    }
    
    for row in budget:
        if row.get('sign') == 1:
            if row['header'] in special_calculations:
                row[working_month] = special_calculations[row['header']](budget, working_month)
            elif cell_header is not None and row['header'] == cell_header and (working_month == cell_month or cell_repeat):
                row[working_month] = cell_value
            elif working_month not in row or pd.isna(row[working_month]) or row[working_month] == '' or (isinstance(row[working_month], (list, tuple)) and len(row[working_month]) == 0):
                row[working_month] = row[prev_month]


def update_ded_alt_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat):
    special_calculations = {
        'Federal Taxes': calculate_federal_taxes,
        'FICA - Social Security': calculate_fica_social_security,
        'FICA - Medicare': calculate_fica_medicare,
        'SGLI Rate': calculate_sgli,
        'State Taxes': calculate_state_taxes,
    }

    for row in budget:
        if row.get('sign') == -1:
            if row['header'] in special_calculations:
                row[working_month] = special_calculations[row['header']](budget, working_month)
            elif row['header'] in ['Traditional TSP', 'Roth TSP']:
                continue
            elif cell_header is not None and row['header'] == cell_header and (working_month == cell_month or cell_repeat):
                row[working_month] = cell_value
            elif working_month not in row or pd.isna(row[working_month]) or row[working_month] == '' or (isinstance(row[working_month], (list, tuple)) and len(row[working_month]) == 0):
                row[working_month] = row[prev_month]
