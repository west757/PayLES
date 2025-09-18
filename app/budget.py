from datetime import datetime
import pandas as pd
import re

from app import flask_app
from app.utils import (
    add_row,
    add_mv_pair,
    get_mha,
    get_hor,
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

    if les_text:
        try:
            init_month = les_text[8][3]
            if not init_month:
                raise ValueError()
        except Exception as e:
            raise Exception(f"Error determining initial month: {e}")
    else:
        init_month = flask_app.config['CURRENT_MONTH']

    budget = []
    for _, row in PARAMS_TEMPLATE.iterrows():
        add_row(budget, row['header'], template=PARAMS_TEMPLATE)

    add_var_tsp(budget, init_month, les_text, initials)
    if les_text:
        add_ent_ded_alt_rows(PAY_TEMPLATE, budget, init_month, les_text)
        calculate_income(budget, init_month)
    elif initials:
        add_ent_rows(PAY_TEMPLATE, budget, init_month)
        calculate_trad_roth_tsp(budget, init_month, init_month)
        calculate_income(budget, init_month)
        add_ded_alt_rows(PAY_TEMPLATE, budget, init_month)
    calculate_tax_exp_net(budget, init_month)
    add_mv_pair(budget, 'Difference', init_month, 0.00)
    add_ytd_rows(budget, init_month, les_text)

    return budget, init_month, headers


def add_var_tsp(budget, month, les_text, initials):
    values = {}

    if les_text:
        try:
            year = int('20' + les_text[8][4])
            if not year:
                raise ValueError()
        except Exception:
            year = flask_app.config['CURRENT_YEAR']
        values['Year'] = year

        try:
            pay_date = datetime.strptime(les_text[3][2], '%y%m%d')
            les_date = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
            months_in_service = (les_date.year - pay_date.year) * 12 + les_date.month - pay_date.month
            if months_in_service < 0:
                raise ValueError()
        except Exception:
            months_in_service = 0
        values['Months in Service'] = months_in_service

        #try:
        #    component = les_text[57][1]
        #    if not component:
        #        raise ValueError()
        #except Exception:
        #    component = "Not Found"
        component = "AD"
        values['Component'] = component

        try:
            grade = les_text[2][1]
            if not grade:
                raise ValueError()
        except Exception:
            grade = "Not Found"
        values['Grade'] = grade

        try:
            zip_code = les_text[48][2]
            if not zip_code or zip_code == "00000":
                raise ValueError()
        except Exception:
            zip_code = "Not Found"
        values['Zip Code'] = zip_code

        try:
            home_of_record = les_text[39][1]
            if not home_of_record or home_of_record == "98":
                raise ValueError()
        except Exception:
            home_of_record = "Not Found"
        values['Home of Record'] = home_of_record

        try:
            dependents = int(les_text[53][1])
            if not dependents or dependents not in range(0, 99):
                raise ValueError()
        except Exception:
            dependents = 0
        values['Dependents'] = dependents

        try:
            status = les_text[24][1]
            if status == "S":
                federal_filing_status = "Single"
            elif status == "M":
                federal_filing_status = "Married"
            elif status == "H":
                federal_filing_status = "Head of Household"
            else:
                raise ValueError()
        except Exception:
            federal_filing_status = "Not Found"
        values['Federal Filing Status'] = federal_filing_status

        try:
            status = les_text[42][1]
            if status == "S":
                state_filing_status = "Single"
            elif status == "M":
                state_filing_status = "Married"
            else:
                raise ValueError()
        except Exception:
            state_filing_status = "Not Found"
        values['State Filing Status'] = state_filing_status

        try:
            sgli_coverage = ""
            remarks = les_text[96]
            remarks_str = " ".join(str(item) for item in remarks if isinstance(item, str))
            match = re.search(r"SGLI COVERAGE AMOUNT IS\s*(\$\d{1,3}(?:,\d{3})*)", remarks_str, re.IGNORECASE)
            if match:
                sgli_coverage = match.group(1)
            else:
                raise ValueError()
        except Exception:
            sgli_coverage = "Not Found"
        values['SGLI Coverage'] = sgli_coverage

        values['Combat Zone'] = "No"

        values['Drills'] = 0

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
                rate = int(les_text[idx][3])
                if not rate:
                    raise ValueError()
            except Exception:
                rate = 0
            values[header] = rate

        try:
            tsp_matching = int(les_text[85][1]) + int(les_text[86][1])
            if not tsp_matching:
                raise ValueError()
        except Exception:
            tsp_matching = 0
        values['TSP Matching'] = tsp_matching

    elif initials:
        print(initials)
        values = initials

    for header, value in values.items():
        add_mv_pair(budget, header, month, value)


    add_mv_pair(budget, 'Component Long', month, flask_app.config['COMPONENTS'][values.get('Component')])

    mha_code, mha_name = get_mha(values.get('Zip Code'))
    add_mv_pair(budget, 'Military Housing Area', month, mha_code)
    add_mv_pair(budget, 'MHA Long', month, mha_name)

    longname, abbr = get_hor(values.get('Home of Record'))
    add_mv_pair(budget, 'Home of Record', month, abbr)
    add_mv_pair(budget, 'Home of Record Long', month, longname)

    return budget


def add_ent_ded_alt_rows(PAY_TEMPLATE, budget, month, les_text=None):
    ent_ded_alt_dict = {}
    
    if les_text:
        ents = parse_pay_section(les_text[9])
        deds = parse_pay_section(les_text[10])
        alts = parse_pay_section(les_text[11])

        for item in ents + deds + alts:
            ent_ded_alt_dict[item['header'].upper()] = item['value']

    for _, row in PAY_TEMPLATE.iterrows():
        header = row['header']
        sign = row['sign']
        required = row['required']
        lesname = row['lesname']

        # only add if lesname in ent_ded_alt_dict or required
        if lesname in ent_ded_alt_dict or required:
            add_row(budget, header, template=PAY_TEMPLATE)

            if lesname in ent_ded_alt_dict:
                value = round(sign * ent_ded_alt_dict[lesname], 2)
            else:
                value = 0.00

            add_mv_pair(budget, header, month, value)

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
                add_row(budget, header, template=PAY_TEMPLATE)
                value = special_calculations[header](budget, month)
            else:
                value = 0.00
            add_mv_pair(budget, header, month, value)
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
                add_row(budget, header, template=PAY_TEMPLATE)
                value = special_calculations[header](budget, month)
            else:
                value = 0.00
            add_mv_pair(budget, header, month, value)
    return budget


def add_ytd_rows(budget, month, les_text):
    values = {}

    remarks = les_text[96]
    remarks_str = " ".join(str(item) for item in remarks if isinstance(item, str))

    ent_match = re.search(r"YTD ENTITLE\s*(\d+\.\d{2})", remarks_str)
    ytd_income = float(ent_match.group(1)) if ent_match else 0.00
    values['YTD Income'] = ytd_income

    ded_match = re.search(r"YTD DEDUCT\s*(\d+\.\d{2})", remarks_str)
    ytd_expenses = -float(ded_match.group(1)) if ded_match else 0.00
    values['YTD Expenses'] = ytd_expenses

    try:
        ytd_tsp = float(les_text[78][2])
        if not ytd_tsp or ytd_tsp < 0:
            raise ValueError()
    except Exception:
        ytd_tsp = 0.00
    values['YTD TSP Contribution'] = ytd_tsp

    try:
        ytd_charity = float(les_text[56][2])
        if not ytd_charity or ytd_charity < 0:
            raise ValueError()
    except Exception:
        ytd_charity = 0.00
    values['YTD Charity'] = ytd_charity

    ytd_net_pay = round(ytd_income + ytd_expenses, 2)
    values['YTD Net Pay'] = ytd_net_pay

    try:
        ytd_trad_tsp = float(les_text[79][3])
        if not ytd_trad_tsp or ytd_trad_tsp < 0:
            raise ValueError()
    except Exception:
        ytd_trad_tsp = 0.00
    values['YTD Trad TSP'] = ytd_trad_tsp

    try:
        ytd_trad_tsp_exempt = float(les_text[80][3])
        if not ytd_trad_tsp_exempt or ytd_trad_tsp_exempt < 0:
            raise ValueError()
    except Exception:
        ytd_trad_tsp_exempt = 0.00
    values['YTD Trad TSP Exempt'] = ytd_trad_tsp_exempt

    try:
        ytd_roth_tsp = float(les_text[81][2])
        if not ytd_roth_tsp or ytd_roth_tsp < 0:
            raise ValueError()
    except Exception:
        ytd_roth_tsp = 0.00
    values['YTD Roth TSP'] = ytd_roth_tsp

    try:
        ytd_tsp_matching = float(les_text[83][3])
        if not ytd_tsp_matching or ytd_tsp_matching < 0:
            raise ValueError()
    except Exception:
        ytd_tsp_matching = 0.00
    values['YTD TSP Matching'] = ytd_tsp_matching


    for header, value in values.items():
        add_mv_pair(budget, header, month, value)

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
    update_var_tsp(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat)
    update_ent_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat, init)
    calculate_trad_roth_tsp(budget, prev_month, working_month)
    calculate_income(budget, working_month)
    update_ded_alt_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat, init)
    calculate_tax_exp_net(budget, working_month)
    calculate_difference(budget, prev_month, working_month)
    calculate_ytd_rows(budget, prev_month, working_month)
    return budget


def update_var_tsp(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat):
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
            mha_code, mha_name = get_mha(zip_code)
            row[working_month] = mha_code

            mha_long_row = next((r for r in budget if r['header'] == "MHA Long"), None)
            mha_long_row[working_month] = mha_name

        elif cell_header is not None and row['header'] == cell_header and (working_month == cell_month or cell_repeat):
            row[working_month] = cell_value

        elif working_month not in row or pd.isna(row[working_month]) or row[working_month] == '' or (isinstance(row[working_month], (list, tuple)) and len(row[working_month]) == 0):
            row[working_month] = row[prev_month]


        if row['header'] == "Component":
            component_row = next((r for r in budget if r['header'] == "Component"), None)
            component_val = component_row.get(working_month)
            component_long_row = next((r for r in budget if r['header'] == "Component Long"), None)
            component_long_row[working_month] = flask_app.config['COMPONENTS'][component_val]

        if row['header'] == "Home of Record":
            longname, abbr = get_hor(row[working_month])
            home_of_record_long = next((r for r in budget if r['header'] == "Home of Record Long"), None)
            home_of_record_long[working_month] = longname

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

    if row_data['method'] == 'template':
        row = add_row(budget, row_data['header'], flask_app.config['PAY_TEMPLATE'])
        for idx, m in enumerate(months):
            row[m] = value

    elif row_data['method'] == 'custom':
        row_meta = {'header': row_data['header']}
        for meta in flask_app.config['ROW_METADATA']:
            if meta == 'type':
                row_meta['type'] = 'c'
            elif meta == 'sign':
                row_meta['sign'] = sign
            elif meta == 'field':
                row_meta['field'] = 'float'
            elif meta == 'tax':
                row_meta['tax'] = row_data['tax']
            elif meta == 'editable':
                row_meta['editable'] = True
            elif meta == 'modal':
                row_meta['modal'] = 'none'

        row = add_row(budget, row_data['header'], metadata=row_meta)

        for idx, m in enumerate(months):
            row[m] = 0.00 if idx == 0 else value

        if not any(h['header'].lower() == row_data['header'].lower() for h in headers):
            headers.append({
                'header': row_data['header'],
                'type': 'c',
                'tooltip': 'Custom row added by user',
            })

    elif row_data['method'] in ['tsp', 'bank', 'special']:
        row_meta = {'header': row_data['header']}
        for meta in flask_app.config['ROW_METADATA']:
            if meta == 'type':
                row_meta['type'] = 'z'
            elif meta == 'sign':
                row_meta['sign'] = 0
            elif meta == 'field':
                row_meta['field'] = 'float'
            elif meta == 'tax':
                row_meta['tax'] = False
            elif meta == 'editable':
                row_meta['editable'] = True
            elif meta == 'modal':
                row_meta['modal'] = 'none'

        row = add_row(budget, row_data['header'], metadata=row_meta)

        percent = float(row_data.get('percent', 0)) / 100
        interest = float(row_data.get('interest', 0)) / 100

        if row_data['method'] == 'tsp':
            trad_row = next((r for r in budget if r['header'] == 'Traditional TSP'), None)
            roth_row = next((r for r in budget if r['header'] == 'Roth TSP'), None)
            prev_val = value

            for idx, m in enumerate(months):
                trad_val = abs(trad_row[m]) if trad_row and m in trad_row else 0.0
                roth_val = abs(roth_row[m]) if roth_row and m in roth_row else 0.0
                month_sum = trad_val + roth_val

                if idx == 0:
                    val = prev_val + month_sum
                else:
                    val = prev_val + month_sum

                val = val * (1 + interest)
                row[m] = round(val, 2)
                prev_val = val

        elif row_data['method'] == 'bank':
            net_pay_row = next((r for r in budget if r['header'] == 'Net Pay'), None)
            prev_val = value

            for idx, m in enumerate(months):
                net_pay = net_pay_row[m] if net_pay_row and m in net_pay_row else 0.0
                month_sum = net_pay * percent

                if idx == 0:
                    val = prev_val + month_sum
                else:
                    val = prev_val + month_sum

                val = val * (1 + interest)
                row[m] = round(val, 2)
                prev_val = val

        elif row_data['method'] == 'special':
            for idx, m in enumerate(months):
                row[m] = value

        if not any(h['header'].lower() == row_data['header'].lower() for h in headers):
            headers.append({
                'header': row_data['header'],
                'type': 'z',
                'tooltip': 'Custom account added by user',
            })

    return budget, headers


def remove_row(budget, headers, header):
    row = next((r for r in budget if r.get('header').lower() == header.lower()), None)
    budget = [r for r in budget if r.get('header').lower() != header.lower()]
    
    if row.get('type') == 'c':
        headers = [h for h in headers if h.get('header').lower() != header.lower()]

    return budget, headers