from datetime import datetime
from flask import session
import pandas as pd
import re

from app import flask_app
from app.utils import (
    add_row,
    add_mv_pair,
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
# init and build budget
# =========================

def init_budget(les_text=None, initials=None):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']
    PARAMS_TEMPLATE = flask_app.config['PARAMS_TEMPLATE']
    headers = PAY_TEMPLATE[['header', 'type', 'tooltip']].to_dict(orient='records') + PARAMS_TEMPLATE[['header', 'type', 'tooltip']].to_dict(orient='records')

    # get initial month
    if les_text:
        try:
            init_month = les_text[8][3]
        except Exception as e:
            raise Exception(f"Error determining initial month: {e}")
    elif initials:
        init_month = initials['current_month']


    # initialize budget with all parameter rows
    budget = []
    for _, row in PARAMS_TEMPLATE.iterrows():
        add_row(budget, row['header'], template=PARAMS_TEMPLATE)

    add_variables(budget, init_month, les_text, initials)
    if les_text:
        add_ent_ded_alt_rows(PAY_TEMPLATE, budget, init_month, les_text)
        calculate_income(budget, init_month, init=True, PARAMS_TEMPLATE=PARAMS_TEMPLATE)
    elif initials:
        add_ent_rows(PAY_TEMPLATE, budget, init_month)
        calculate_trad_roth_tsp(budget, init_month, init=True, PAY_TEMPLATE=PAY_TEMPLATE)
        calculate_income(budget, init_month, init=True, PARAMS_TEMPLATE=PARAMS_TEMPLATE)
        add_ded_alt_rows(PAY_TEMPLATE, budget, init_month)
    calculate_tax_exp_net(budget, init_month, init=True, PARAMS_TEMPLATE=PARAMS_TEMPLATE)
    calculate_difference(budget, init_month, init_month, init=True, PARAMS_TEMPLATE=PARAMS_TEMPLATE)
    add_ytd_rows(PARAMS_TEMPLATE, budget, init_month, les_text, initials)

    return budget, init_month, headers


def add_variables(budget, month, les_text, initials):
    values = {}

    if les_text:
        try:
            values['Year'] = int('20' + les_text[8][4])
        except Exception:
            values['Year'] = 0

        try:
            pay_date = datetime.strptime(les_text[3][2], '%y%m%d')
            les_date = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
            months_in_service = (les_date.year - pay_date.year) * 12 + les_date.month - pay_date.month
        except Exception:
            months_in_service = 0
        values['Months in Service'] = months_in_service

        years = months_in_service // 12
        months = months_in_service % 12
        if years > 0 and months > 0:
            values['Time in Service Long'] = f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''}"
        elif years > 0:
            values['Time in Service Long'] = f"{years} year{'s' if years != 1 else ''}"
        else:
            values['Time in Service Long'] = f"{months} month{'s' if months != 1 else ''}"

        try:
            values['Grade'] = les_text[2][1]
        except Exception:
            values['Grade'] = "Not Found"

        try:
            zip_code, military_housing_area = validate_calculate_zip_mha(les_text[48][2])
        except Exception:
            zip_code, military_housing_area = "Not Found", "Not Found"
        values['Zip Code'] = zip_code
        values['Military Housing Area'] = military_housing_area

        try:
            values['Home of Record'] = validate_home_of_record(les_text[39][1])
        except Exception:
            values['Home of Record'] = "Not Found"

        try:
            values['Dependents'] = int(les_text[53][1])
        except Exception:
            values['Dependents'] = 0

        try:
            status = les_text[24][1]
            if status == "S":
                values['Federal Filing Status'] = "Single"
            elif status == "M":
                values['Federal Filing Status'] = "Married"
            elif status == "H":
                values['Federal Filing Status'] = "Head of Household"
            else:
                values['Federal Filing Status'] = "Not Found"
        except Exception:
            values['Federal Filing Status'] = "Not Found"

        try:
            status = les_text[42][1]
            if status == "S":
                values['State Filing Status'] = "Single"
            elif status == "M":
                values['State Filing Status'] = "Married"
            else:
                values['State Filing Status'] = "Not Found"
        except Exception:
            values['State Filing Status'] = "Not Found"

        try:
            sgli_coverage = ""
            remarks = les_text[96]
            remarks_str = " ".join(str(item) for item in remarks if isinstance(item, str))
            match = re.search(r"SGLI COVERAGE AMOUNT IS\s*(\$\d{1,3}(?:,\d{3})*)", remarks_str, re.IGNORECASE)
            if match:
                sgli_coverage = match.group(1)
            else:
                sgli_coverage = "Not Found"
        except Exception:
            sgli_coverage = "Not Found"
        values['SGLI Coverage'] = sgli_coverage

        values['Combat Zone'] = "No"

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
                values[header] = int(les_text[idx][3])
            except Exception:
                values[header] = 0

    elif initials:
        values['Year'] = initials['current_year']
        months_in_service = initials['months_in_service']
        values['Months in Service'] = months_in_service

        years = months_in_service // 12
        months = months_in_service % 12
        if years > 0 and months > 0:
            values['Time in Service Long'] = f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''}"
        elif years > 0:
            values['Time in Service Long'] = f"{years} year{'s' if years != 1 else ''}"
        else:
            values['Time in Service Long'] = f"{months} month{'s' if months != 1 else ''}"

        values['Grade'] = initials['grade']
        zip_code = initials['zip_code']
        values['Zip Code'] = zip_code
        _, military_housing_area = validate_calculate_zip_mha(zip_code)
        values['Military Housing Area'] = military_housing_area
        values['Home of Record'] = initials['home_of_record']
        values['Dependents'] = initials['dependents']
        values['Federal Filing Status'] = initials['federal_filing_status']
        values['State Filing Status'] = initials['state_filing_status']
        values['SGLI Coverage'] = initials['sgli_coverage']
        values['Combat Zone'] = initials['combat_zone']

        tsp_rate_rows = [
            "trad_tsp_base_rate",
            "trad_tsp_specialty_rate",
            "trad_tsp_incentive_rate",
            "trad_tsp_bonus_rate",
            "roth_tsp_base_rate",
            "roth_tsp_specialty_rate",
            "roth_tsp_incentive_rate",
            "roth_tsp_bonus_rate",
        ]
        headers = [
            "Trad TSP Base Rate",
            "Trad TSP Specialty Rate",
            "Trad TSP Incentive Rate",
            "Trad TSP Bonus Rate",
            "Roth TSP Base Rate",
            "Roth TSP Specialty Rate",
            "Roth TSP Incentive Rate",
            "Roth TSP Bonus Rate",
        ]
        for key, header in zip(tsp_rate_rows, headers):
            values[header] = initials[key]

    # Now set all values in the budget
    for header, value in values.items():
        add_mv_pair(budget, header, month, value)

    return budget


def add_ent_ded_alt_rows(PAY_TEMPLATE, budget, month, les_text=None):
    ent_ded_alt_dict = {}
    
    if les_text:
        ents = parse_pay_section(les_text[9])
        deds = parse_pay_section(les_text[10])
        alts = parse_pay_section(les_text[11])

        for item in ents + deds + alts:
            ent_ded_alt_dict[item['header'].upper()] = item['value']

    # Define special calculation functions for ent/ded/alt rows
    special_calculations = {
        'Base Pay': calculate_base_pay,
        'BAS': calculate_bas,
        'BAH': calculate_bah,
        'Federal Taxes': calculate_federal_taxes,
        'FICA - Social Security': calculate_fica_social_security,
        'FICA - Medicare': calculate_fica_medicare,
        'SGLI Rate': calculate_sgli,
        'State Taxes': calculate_state_taxes,
    }

    for _, row in PAY_TEMPLATE.iterrows():
        header = row['header']
        sign = row['sign']
        required = row['required']
        lesname = row['lesname']

        if lesname in ent_ded_alt_dict:
            value = round(sign * ent_ded_alt_dict[lesname], 2)
        elif required:
            if header in special_calculations:
                value = special_calculations[header](budget, month)
            else:
                value = 0.00
        else:
            continue

        budget.append(add_row(PAY_TEMPLATE, header, month, value))

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


def add_ent_rows(PAY_TEMPLATE, budget, month):
    special_calculations = {
        'Base Pay': calculate_base_pay,
        'BAS': calculate_bas,
        'BAH': calculate_bah,
    }
    for _, row in PAY_TEMPLATE.iterrows():
        header = row['header']
        sign = row['sign']
        required = row['required']
        if sign == 1 and required:
            if header in special_calculations:
                value = special_calculations[header](budget, month)
            else:
                value = 0.00
            budget.append(add_row(PAY_TEMPLATE, header, month, value))
    return budget


def add_ded_alt_rows(PAY_TEMPLATE, budget, month):
    special_calculations = {
        'Federal Taxes': calculate_federal_taxes,
        'FICA - Social Security': calculate_fica_social_security,
        'FICA - Medicare': calculate_fica_medicare,
        'SGLI Rate': calculate_sgli,
        'State Taxes': calculate_state_taxes,
    }
    for _, row in PAY_TEMPLATE.iterrows():
        header = row['header']
        sign = row['sign']
        required = row['required']
        if sign == -1 and required:
            if header in special_calculations:
                value = special_calculations[header](budget, month)
            else:
                value = 0.00
            budget.append(add_row(PAY_TEMPLATE, header, month, value))
    return budget


def add_ytd_rows(PARAMS_TEMPLATE, budget, month, les_text=None, initials=None):
    if les_text:
        remarks = les_text[96]
        remarks_str = " ".join(str(item) for item in remarks if isinstance(item, str))

    if les_text:
        ent_match = re.search(r"YTD ENTITLE\s*(\d+\.\d{2})", remarks_str)
        ytd_income = float(ent_match.group(1)) if ent_match else 0.00
    elif initials:
        ytd_income = initials['ytd_income']
    budget.append(add_row(PARAMS_TEMPLATE, 'YTD Income', month, ytd_income))

    if les_text:
        ded_match = re.search(r"YTD DEDUCT\s*(\d+\.\d{2})", remarks_str)
        ytd_expenses = -float(ded_match.group(1)) if ded_match else 0.00
    elif initials:
        ytd_expenses = initials['ytd_expenses']
    budget.append(add_row(PARAMS_TEMPLATE, 'YTD Expenses', month, ytd_expenses))

    if les_text:
        try:
            ytd_tsp = float(les_text[78][2])
        except Exception:
            ytd_tsp = 0.00
    elif initials:
        ytd_tsp = initials['ytd_tsp']
    budget.append(add_row(PARAMS_TEMPLATE, 'YTD TSP Contribution', month, ytd_tsp))

    if les_text:
        try:
            ytd_charity = float(les_text[56][2])
        except Exception:
            ytd_charity = 0.00
    elif initials:
        ytd_charity = initials['ytd_charity']
    budget.append(add_row(PARAMS_TEMPLATE, 'YTD Charity', month, ytd_charity))

    ytd_net_pay = round(ytd_income + ytd_expenses, 2)
    budget.append(add_row(PARAMS_TEMPLATE, 'YTD Net Pay', month, ytd_net_pay))

    return budget



# =========================
# update budget months and variables
# =========================

def add_months(budget, latest_month, months_num, init=False):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    months = get_months(budget)
    current_num = len(months)
    months_to_add = months_num - current_num
    latest_month_idx = MONTHS_SHORT.index(latest_month)

    for i in range(months_to_add):
        working_month = MONTHS_SHORT[(latest_month_idx + 1 + i) % 12]
        months.append(working_month)
        budget = build_month(budget, months[-2], working_month, init=init)  # months[-2] is previous month

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


def build_month(budget, prev_month, working_month, cell_header=None, cell_month=None, cell_value=None, cell_repeat=False, init=False):
    update_variables(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat)
    update_ent_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat, init)
    calculate_trad_roth_tsp(budget, working_month)
    calculate_income(budget, working_month)
    update_ded_alt_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat, init)
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


def update_ent_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat, init=False):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']

    special_calculations = {
        'Base Pay': calculate_base_pay,
        'BAS': calculate_bas,
        'BAH': calculate_bah,
    }
    
    for row in budget:
        if row.get('sign') == 1:
            template_row = PAY_TEMPLATE[PAY_TEMPLATE['header'] == row['header']]
            is_onetime = not template_row.empty and template_row.iloc[0].get('onetime', False)
            if init and is_onetime:
                row[working_month] = 0.00
            if row['header'] in special_calculations:
                row[working_month] = special_calculations[row['header']](budget, working_month)
            elif cell_header is not None and row['header'] == cell_header and (working_month == cell_month or cell_repeat):
                row[working_month] = cell_value
            elif working_month not in row or pd.isna(row[working_month]) or row[working_month] == '' or (isinstance(row[working_month], (list, tuple)) and len(row[working_month]) == 0):
                row[working_month] = row[prev_month]


def update_ded_alt_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat, init=False):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']

    special_calculations = {
        'Federal Taxes': calculate_federal_taxes,
        'FICA - Social Security': calculate_fica_social_security,
        'FICA - Medicare': calculate_fica_medicare,
        'SGLI Rate': calculate_sgli,
        'State Taxes': calculate_state_taxes,
    }

    for row in budget:
        if row.get('sign') == -1:
            template_row = PAY_TEMPLATE[PAY_TEMPLATE['header'] == row['header']]
            is_onetime = not template_row.empty and template_row.iloc[0].get('onetime', False)
            if init and is_onetime:
                row[working_month] = 0.00
            if row['header'] in special_calculations:
                row[working_month] = special_calculations[row['header']](budget, working_month)
            elif row['header'] in ['Traditional TSP', 'Roth TSP']:
                continue
            elif cell_header is not None and row['header'] == cell_header and (working_month == cell_month or cell_repeat):
                row[working_month] = cell_value
            elif working_month not in row or pd.isna(row[working_month]) or row[working_month] == '' or (isinstance(row[working_month], (list, tuple)) and len(row[working_month]) == 0):
                row[working_month] = row[prev_month]


def remove_months(budget, months_num):
    months = get_months(budget)
    months_to_remove = months[months_num:]

    for row in budget:
        for month in months_to_remove:
            if month in row:
                del row[month]
    months = months[:months_num]

    return budget, months


def insert_row(budget, months, headers, row_data):
    if row_data['type'] == 'd' or row_data['type'] == 'a':
        sign = -1
    else:
        sign = 1

    value = round(sign * float(row_data['value']), 2)
    insert_idx = len(budget)

    if row_data['method'] == 'template':
        if row_data['type'] == 'e':
            insert_idx = max([i for i, r in enumerate(budget) if r.get('type') == 'e'], default=-1) + 1
        elif row_data['type'] == 'd':
            insert_idx = max([i for i, r in enumerate(budget) if r.get('type') == 'd'], default=-1) + 1
        elif row_data['type'] == 'a':
            a_indices = [i for i, r in enumerate(budget) if r.get('type') == 'a']
            if a_indices:
                insert_idx = max(a_indices) + 1
            else:
                d_indices = [i for i, r in enumerate(budget) if r.get('type') == 'd']
                insert_idx = max(d_indices, default=-1) + 1

        row = add_row(flask_app.config['PAY_TEMPLATE'], row_data['header'], months[0], 0.00)
        for idx, m in enumerate(months[1:]):
            row[m] = value

    elif row_data['method'] == 'custom':
        c_indices = [i for i, r in enumerate(budget) if r.get('type') == 'c']
        a_indices = [i for i, r in enumerate(budget) if r.get('type') == 'a']
        d_indices = [i for i, r in enumerate(budget) if r.get('type') == 'd']
        if c_indices:
            insert_idx = max(c_indices) + 1
        elif a_indices:
            insert_idx = max(a_indices) + 1
        elif d_indices:
            insert_idx = max(d_indices) + 1

        row = {'header': row_data['header']}
        for meta in flask_app.config['ROW_METADATA']:
            if meta == 'type':
                row['type'] = 'c'
            elif meta == 'sign':
                row['sign'] = sign
            elif meta == 'field':
                row['field'] = 'float'
            elif meta == 'tax':
                row['tax'] = row_data['tax']
            elif meta == 'editable':
                row['editable'] = True
            elif meta == 'modal':
                row['modal'] = ''

        for idx, m in enumerate(months):
            row[m] = 0.00 if idx == 0 else value

        if not any(h['header'].lower() == row_data['header'].lower() for h in headers):
            headers.append({
                'header': row_data['header'],
                'type': 'c',
                'tooltip': 'Custom row added by user',
            })

    elif row_data['method'] == 'account':
        row = {'header': row_data['header']}
        for meta in flask_app.config['ROW_METADATA']:
            if meta == 'type':
                row['type'] = 'z'
            elif meta == 'sign':
                row['sign'] = 0
            elif meta == 'field':
                row['field'] = 'float'
            elif meta == 'tax':
                row['tax'] = False
            elif meta == 'editable':
                row['editable'] = True
            elif meta == 'modal':
                row['modal'] = ''

        percent = float(row_data['percent']) / 100
        interest = float(row_data['interest']) / 100

        for idx, m in enumerate(months):
            month_sum = 0.0
            for rh in row_data['rows']:
                source_row = next((r for r in budget if r['header'] == rh), None)
                if source_row:
                    month_sum += (source_row[m] * percent)

            if row_data['type'] == 'm':
                val = month_sum
            elif row_data['type'] == 'c':
                prev_val = row.get(months[idx-1], value) if idx > 0 else value
                val = prev_val + month_sum
            elif row_data['type'] == 'y':
                if idx == 0 or (m == 'JAN' and idx > 0):
                    val = month_sum
                else:
                    prev = row.get(months[idx-1], value)
                    val = prev + month_sum if months[idx-1] != 'DEC' else month_sum
            else:
                val = month_sum

            val = val * (1 + interest)
            row[m] = round(val, 2)
        
        if not any(h['header'].lower() == row_data['header'].lower() for h in headers):
            headers.append({
                'header': row_data['header'],
                'type': 'z',
                'tooltip': 'Custom account row added by user',
            })

    budget.insert(insert_idx, row)

    return budget, headers


def remove_row(budget, headers, header):
    row = next((r for r in budget if r.get('header').lower() == header.lower()), None)
    budget = [r for r in budget if r.get('header').lower() != header.lower()]
    
    if row.get('type') == 'c':
        headers = [h for h in headers if h.get('header').lower() != header.lower()]

    return budget, headers