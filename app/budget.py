from datetime import datetime
import pandas as pd
import re

from app import flask_app
from app.utils import (
    validate_calculate_zip_mha,
    validate_home_of_record,
    get_month_headers,
)
from app.calculations import (
    calculate_taxable_income,
    calculate_total_taxes,
    calculate_gross_net_pay,
    calculate_difference,
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
        initial_month = les_text[8][3]
        if initial_month not in MONTHS_SHORT:
            raise ValueError(f"Error: les_text[8][3], '{initial_month}', is not in MONTHS_SHORT")
    except Exception as e:
        raise Exception(f"Error determining initial month: {e}")

    budget = []
    budget = add_variables(budget, les_text, initial_month)
    budget = add_ent_ded_alt_rows(budget, les_text, initial_month)
    budget = calculate_taxable_income(budget, initial_month, init=True)
    budget = calculate_total_taxes(budget, initial_month, init=True)
    budget = calculate_gross_net_pay(budget, initial_month, init=True)
    budget.append({'header': 'Difference', initial_month: 0.00})

    return budget, initial_month


def add_variables(budget, les_text, month):
    VARIABLE_TEMPLATE = flask_app.config['VARIABLE_TEMPLATE']

    try:
        year = int('20' + les_text[8][4])
    except Exception:
        year = 0
    budget.append(add_row(VARIABLE_TEMPLATE, 'Year', year, month))

    try:
        pay_date = datetime.strptime(les_text[3][2], '%y%m%d')
        les_date = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
        months_in_service = (les_date.year - pay_date.year) * 12 + les_date.month - pay_date.month
    except Exception:
        months_in_service = 0
    budget.append(add_row(VARIABLE_TEMPLATE, 'Months in Service', months_in_service, month))

    try:
        grade = les_text[2][1]
    except Exception:
        grade = "Not Found"
    budget.append(add_row(VARIABLE_TEMPLATE, 'Grade', grade, month))

    try:
        zip_code, military_housing_area = validate_calculate_zip_mha(les_text[48][2])
    except Exception:
        zip_code, military_housing_area = "Not Found", "Not Found"
    budget.append(add_row(VARIABLE_TEMPLATE, 'Zip Code', zip_code, month))
    budget.append(add_row(VARIABLE_TEMPLATE, 'Military Housing Area', military_housing_area, month))

    try:
        home_of_record = validate_home_of_record(les_text[39][1])
    except Exception:
        home_of_record = "Not Found"
    budget.append(add_row(VARIABLE_TEMPLATE, 'Home of Record', home_of_record, month))

    try:
        dependents = int(les_text[53][1])
    except Exception:
        dependents = 0
    budget.append(add_row(VARIABLE_TEMPLATE, 'Dependents', dependents, month))

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
    budget.append(add_row(VARIABLE_TEMPLATE, 'Federal Filing Status', federal_filing_status, month))

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
    budget.append(add_row(VARIABLE_TEMPLATE, 'State Filing Status', state_filing_status, month))


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
    budget.append(add_row(VARIABLE_TEMPLATE, 'SGLI Coverage', sgli_coverage, month))

    combat_zone = "No"
    budget.append(add_row(VARIABLE_TEMPLATE, 'Combat Zone', combat_zone, month))

    tsp_rows = [
        #("TSP YTD Deductions", 78, 2),
        ("Trad TSP Base Rate", 60, 3),
        ("Trad TSP Specialty Rate", 62, 3),
        ("Trad TSP Incentive Rate", 64, 3),
        ("Trad TSP Bonus Rate", 66, 3),
        ("Roth TSP Base Rate", 69, 3),
        ("Roth TSP Specialty Rate", 71, 3),
        ("Roth TSP Incentive Rate", 73, 3),
        ("Roth TSP Bonus Rate", 75, 3),
    ]

    for header, idx, idx2 in tsp_rows:
        try:
            value = int(les_text[idx][idx2])
        except Exception:
            value = 0
        budget.append(add_row(VARIABLE_TEMPLATE, header, value, month))

    return budget


def add_ent_ded_alt_rows(budget, les_text, month):
    BUDGET_TEMPLATE = flask_app.config['BUDGET_TEMPLATE']

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
            value = 0.00
        else:
            continue

        budget.append(add_row(BUDGET_TEMPLATE, header, value, month))

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
# add and remove months
# =========================

def remove_month(budget, month):
    for row in budget:
        if month in row:
            del row[month]


def build_months(all_rows, budget, prev_month, months_num, row_header=None, col_month=None, value=None, repeat=False):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    month_headers = get_month_headers(budget)
    month_idx_headers = month_headers.index(prev_month)
    month_idx_short = MONTHS_SHORT.index(prev_month)

    for i in range(months_num):
        if all_rows:
            month_idx_short = (month_idx_short + 1) % 12
            next_month = MONTHS_SHORT[month_idx_short]
            month_headers.append(next_month)
        else:
            if month_idx_headers + i >= len(month_headers):
                break
            next_month = month_headers[month_idx_headers + i]

        update_variables(all_rows, budget, prev_month, next_month, row_header=row_header, col_month=col_month, value=value, repeat=repeat)
        update_ent_rows(all_rows, budget, prev_month, next_month, row_header=row_header, col_month=col_month, value=value, repeat=repeat)
        calculate_taxable_income(budget, next_month)
        update_ded_alt_rows(all_rows, budget, prev_month, next_month, row_header=row_header, col_month=col_month, value=value, repeat=repeat)
        calculate_total_taxes(budget, next_month)
        calculate_gross_net_pay(budget, next_month)
        calculate_difference(budget, month_headers, month_headers.index(next_month))

        prev_month = next_month

    return budget, month_headers


def update_variables(all_rows, budget, prev_month, next_month, row_header, col_month, value, repeat):
    for row in budget:
        if row.get('type') in ('v', 't'):

            if row['header'] == "Military Housing Area":
                zip_row = next((r for r in budget if r['header'] == "Zip Code"), None)
                zip_code = zip_row.get(next_month)
                _, military_housing_area = validate_calculate_zip_mha(zip_code)
                row[next_month] = military_housing_area
                continue

            if not all_rows:
                if row_header and (row['header'] == row_header):
                    if next_month == col_month or repeat:
                        row[next_month] = value
                continue

            prev_value = row.get(prev_month)
            if row['header'] == "Year":
                row[next_month] = prev_value + 1 if next_month == "JAN" else prev_value
            elif row['header'] == "Months in Service":
                row[next_month] = prev_value + 1
            else:
                row[next_month] = prev_value


def update_ent_rows(all_rows, budget, prev_month, next_month, row_header, col_month, value, repeat):
    special_calculations = {
        'Base Pay': calculate_base_pay,
        'BAS': calculate_bas,
        'BAH': calculate_bah,
    }
    for row in budget:
        if row.get('type') == 'e':
            if row['header'] in special_calculations:
                row[next_month] = special_calculations[row['header']](budget, next_month)
                continue

            if not all_rows:
                if row_header and (row['header'] == row_header):
                    if next_month == col_month or repeat:
                        row[next_month] = value
                continue

            prev_value = row.get(prev_month)
            row[next_month] = prev_value


def update_ded_alt_rows(all_rows, budget, prev_month, next_month, row_header, col_month, value, repeat):
    special_calculations = {
        'Federal Taxes': calculate_federal_taxes,
        'FICA - Social Security': calculate_fica_social_security,
        'FICA - Medicare': calculate_fica_medicare,
        'SGLI Rate': calculate_sgli,
        'State Taxes': calculate_state_taxes,
        'Traditional TSP': lambda b, m: calculate_trad_roth_tsp(b, m)[0],
        'Roth TSP': lambda b, m: calculate_trad_roth_tsp(b, m)[1],
    }

    for row in budget:
        if row.get('type') in ('d', 'a'):

            if row['header'] in special_calculations:
                row[next_month] = special_calculations[row['header']](budget, next_month)
                continue

            if not all_rows:
                if row_header and (row['header'] == row_header):
                    if next_month == col_month or repeat:
                        row[next_month] = value
                continue

            prev_value = row.get(prev_month)
            row[next_month] = prev_value
