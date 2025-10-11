from datetime import datetime
import pandas as pd
import re

from app import flask_app
from app.utils import (
    get_error_context,
    convert_numpy_types,
    add_row,
    add_mv_pair,
    get_row,
    get_row_value,
    set_variable_longs,
    get_military_housing_area,
    get_home_of_record,
    get_months,
    parse_pay_string,
)
from app.calculations import (
    calc_income,
    calc_expenses_net,
    calc_difference,
    calc_ytds,
    calc_base_pay,
    calc_bas,
    calc_bah,
    calc_federal_taxes,
    calc_fica_social_security,
    calc_fica_medicare,
    calc_sgli,
    calc_state_taxes,
)
from app.tsp import (
    init_tsp,
    #update_tsp,
)


# =========================
# get variables and init budget
# =========================

def get_les_variables(les_text):
    try:
        les_month = les_text.get('les_month', None)
        if les_month not in flask_app.config['MONTHS_SHORT']:
            raise ValueError(f"Invalid LES month: {les_month}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining month from LES text"))
    
    les_variables = {}

    try:
        year = int('20' + les_text.get('les_year', None))
        if not year or year < 2021 or year > flask_app.config['CURRENT_YEAR'] + 1:
            raise ValueError(f"Invalid LES year: {year}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining year from LES text"))
    les_variables['Year'] = year

    try:
        pay_date = datetime.strptime(les_text.get('pay_date', None), '%y%m%d')
        if not pay_date:
            raise ValueError(f"Invalid LES pay date: {pay_date}")
        les_date = pd.to_datetime(datetime.strptime((les_text.get('les_year', None) + les_text.get('les_month', None) + "1"), '%y%b%d'))
        if not les_date:
            raise ValueError(f"Invalid LES date: {les_date}")

        months_in_service = ((les_date.year - pay_date.year) * 12) + (les_date.month - pay_date.month)
        if months_in_service < 0:
            raise ValueError(f"Months in service calculated as negative, returned {months_in_service}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining months in service from LES text"))
    les_variables['Months in Service'] = months_in_service

    try:
        text = les_text.get('branch', None)
        if text == "ARMY":
            branch = "USA"
        elif text == "AF":
            branch = "USAF"
        elif text == "SF":
            branch = "USSF"
        elif text == "NAVY":
            branch = "USN"
        elif text == "USMC":
            branch = "USMC"
        else:
            raise ValueError(f"Invalid LES branch: {text}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining branch from LES text"))
    les_variables['Branch'] = branch

    try:
        text = les_text.get('tpc', None)
        if text == "A":
            component = "AGR"
        elif text == "M":
            component = "USAF"
        else:
            component = "AD"
            #raise ValueError(f"Invalid LES grade: {grade}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining component from LES text"))
    les_variables['Component'] = component

    try:
        grade = les_text.get('grade', None)
        if not grade:
            raise ValueError(f"Invalid LES grade: {grade}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining grade from LES text"))
    les_variables['Grade'] = grade

    try:
        zip_code = les_text.get('vha_zip', None)
        if not zip_code or zip_code == "00000":
            raise ValueError(f"Invalid LES zip code: {zip_code}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining zip code from LES text"))
    les_variables['Zip Code'] = zip_code

    try:
        oconus_locality_code = les_text.get('jftr', None)
        if oconus_locality_code is None or oconus_locality_code == "":
            oconus_locality_code = "N/A"
            #raise ValueError(f"Invalid LES OCONUS locality code: {oconus_locality_code}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining OCONUS locality code from LES text"))
    les_variables['OCONUS Locality Code'] = oconus_locality_code

    try:
        home_of_record = les_text.get('state', None)
        if not home_of_record or home_of_record == "98":
            raise ValueError(f"Invalid LES home of record: {home_of_record}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining home of record from LES text"))
    les_variables['Home of Record'] = home_of_record

    try:
        dependents = les_text.get('dependents', None)
        if dependents is None or dependents == "" or dependents < 0:
            raise ValueError(f"Invalid LES dependents: {dependents}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining dependents from LES text"))
    les_variables['Dependents'] = dependents

    try:
        text = les_text.get('federal_filing_status', None)
        if text == "S":
            federal_filing_status = "Single"
        elif text == "M":
            federal_filing_status = "Married"
        elif text == "H":
            federal_filing_status = "Head of Household"
        else:
            raise ValueError(f"Invalid LES federal filing status: {text}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining federal filing status from LES text"))
    les_variables['Federal Filing Status'] = federal_filing_status

    try:
        text = les_text.get('state_filing_status', None)
        if text == "S":
            state_filing_status = "Single"
        elif text == "M":
            state_filing_status = "Married"
        else:
            raise ValueError(f"Invalid LES state filing status: {text}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining state filing status from LES text"))
    les_variables['State Filing Status'] = state_filing_status

    try:
        remarks = les_text.get('remarks', "")
        # search for SGLI coverage amount in the remarks string
        match = re.search(r"SGLI COVERAGE AMOUNT IS\s*\$([\d,]+)", remarks, re.IGNORECASE)
        if match:
            sgli_coverage = f"${match.group(1)}"
            # validate against allowed coverages
            if sgli_coverage not in flask_app.config['SGLI_COVERAGES']:
                raise ValueError(f"SGLI coverage '{sgli_coverage}' not in allowed coverages")
        else:
            raise ValueError("SGLI coverage amount not found in remarks")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining SGLI coverage from LES remarks"))
    les_variables['SGLI Coverage'] = sgli_coverage

    les_variables['Combat Zone'] = "No"

    les_variables['Drills'] = 0

    return les_month, les_variables


def init_budget(les_variables, tsp_variables, month, les_text=None):
    PARAMS_TEMPLATE = flask_app.config['PARAMS_TEMPLATE']

    budget = []
    for _, row in PARAMS_TEMPLATE.iterrows():
        add_row("budget", budget, row['header'], template=PARAMS_TEMPLATE)

    if les_text:
        budget = add_variables(budget, month, les_variables)
        budget = add_les_pay(budget, month, les_text)

        taxable, nontaxable, income = calc_income(budget, month)
        add_mv_pair(budget, 'Taxable Income', month, taxable)
        add_mv_pair(budget, 'Non-Taxable Income', month, nontaxable)
        add_mv_pair(budget, 'Total Income', month, income)

        tsp = init_tsp(tsp_variables, budget, month, les_text)
        
        taxes, expenses, net_pay = calc_expenses_net(budget, month)
        add_mv_pair(budget, 'Taxes', month, taxes)
        add_mv_pair(budget, 'Total Expenses', month, expenses)
        add_mv_pair(budget, 'Net Pay', month, net_pay)

        budget = add_ytds(budget, month, les_text)
    else:
        budget = add_variables(budget, month, les_variables)
        budget = add_pay_rows(budget, month, les_variables, sign=1)

        taxable, nontaxable, income = calc_income(budget, month)
        add_mv_pair(budget, 'Taxable Income', month, taxable)
        add_mv_pair(budget, 'Non-Taxable Income', month, nontaxable)
        add_mv_pair(budget, 'Total Income', month, income)

        tsp = init_tsp(tsp_variables, budget, month)
        budget = add_pay_rows(budget, month, les_variables, sign=-1)

        taxes, expenses, net_pay = calc_expenses_net(budget, month)
        add_mv_pair(budget, 'Taxes', month, taxes)
        add_mv_pair(budget, 'Total Expenses', month, expenses)
        add_mv_pair(budget, 'Net Pay', month, net_pay)

        #budget = calc_ytds(budget, prev_month=month, month=month)

    add_mv_pair(budget, 'Difference', month, 0.00)
    budget = convert_numpy_types(budget)
    tsp = convert_numpy_types(tsp)

    return budget, tsp


def add_variables(budget, month, variables):
    for var, val in variables.items():
        row = get_row(budget, var)
        if row:
            add_mv_pair(budget, row['header'], month, val)
        else:
            raise Exception(f"Variable '{var}' not found in PARAMS_TEMPLATE")
        
    budget = set_variable_longs(budget, month)
    return budget


def add_les_pay(budget, month, les_text):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']

    combined_pay_string = (
        les_text.get('entitlements', '') + ' ' +
        les_text.get('deductions', '') + ' ' +
        les_text.get('allotments', '')
    )

    # parse all pay items into a dict: {lesname: value}
    pay_dict = parse_pay_string(combined_pay_string, PAY_TEMPLATE)

    for lesname, value in pay_dict.items():
        # find the corresponding row in PAY_TEMPLATE
        template_row = PAY_TEMPLATE[PAY_TEMPLATE['lesname'] == lesname]
        if template_row.empty:
            continue  # skip if not found

        header = template_row.iloc[0]['header']
        sign = template_row.iloc[0]['sign']
        value = round(sign * value, 2)

        add_row("budget", budget, header, template=PAY_TEMPLATE)
        add_mv_pair(budget, header, month, value)

    return budget


def add_pay_rows(budget, month, variables, sign):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']
    TRIGGER_CALCULATIONS = flask_app.config['TRIGGER_CALCULATIONS']

    pay_subset = PAY_TEMPLATE[(PAY_TEMPLATE['sign'] == sign) & (PAY_TEMPLATE['trigger'] != "none")]

    for _, row in pay_subset.iterrows():
        header = row['header']
        trigger = row['trigger']
        variable = variables.get(trigger, None)

        if variable not in [0, None, "NOT FOUND"]:
            function = globals().get(TRIGGER_CALCULATIONS[header])
            if callable(function):
                value = round(function(budget, month), 2)
                
                add_row("budget", budget, header, template=PAY_TEMPLATE)
                add_mv_pair(budget, header, month, value)

    return budget


def add_ytds(budget, month, les_text):
    try:
        ytd_entitlements = les_text.get('ytd_entitlements', 0.00)
        if not ytd_entitlements:
            raise ValueError(f"Invalid LES text: {ytd_entitlements}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD entitlements from LES text"))
    add_mv_pair(budget, 'YTD Income', month, round(ytd_entitlements, 2))

    try:
        ytd_deductions = les_text.get('ytd_deductions', 0.00)
        if not ytd_deductions:
            raise ValueError(f"Invalid LES text: {ytd_deductions}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining YTD deductions from LES text"))
    add_mv_pair(budget, 'YTD Expenses', month, round(-ytd_deductions, 2))

    add_mv_pair(budget, 'YTD Net Pay', month, round(ytd_entitlements + ytd_deductions, 2))

    return budget


# =========================
# update budget months and variables
# =========================

def add_months(budget, tsp, latest_month, months_num, init=False):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    months = get_months(budget)

    # calculates how many more months to add, starting from latest_month
    months_num_to_add = months_num - len(months)
    latest_month_idx = MONTHS_SHORT.index(latest_month)

    for i in range(months_num_to_add):
        month = MONTHS_SHORT[(latest_month_idx + 1 + i) % 12]
        budget, tsp = build_month(budget, tsp, month, months[-1], init=init)
        months.append(month)

    return budget, tsp, months


def update_months(budget, tsp, months, cell=None):
    # if cell is provided, start from that month and update from there
    # else, start from the second month to update entire table
    if cell:
        start_idx = months.index(cell.get('month'))
    else:
        start_idx = 1

    for i in range(start_idx, len(months)):
        budget, tsp = build_month(budget, tsp, months[i], months[i-1], cell)

    return budget, tsp


def build_month(budget, tsp, month, prev_month, cell=None, init=False):
    update_variables(budget, month, prev_month, cell)
    set_variable_longs(budget, month)
    update_ent_rows(budget, prev_month, month, cell, init)
    #update_tsp(budget, tsp, prev_month, month, cell_header, cell_month, cell_value, cell_repeat)

    trad_tsp_row = next((r for r in budget if r.get('header') == 'Traditional TSP'), None)
    trad_contrib_row = next((r for r in tsp if r.get('header') == 'Trad TSP Contribution'), None)
    trad_exempt_row = next((r for r in tsp if r.get('header') == 'Trad TSP Exempt Contribution'), None)
    roth_tsp_row = next((r for r in budget if r.get('header') == 'Roth TSP'), None)
    roth_contrib_row = next((r for r in tsp if r.get('header') == 'Roth TSP Contribution'), None)
    trad_tsp_row[month] = trad_contrib_row.get(month, 0) + trad_exempt_row.get(month, 0)
    roth_tsp_row[month] = roth_contrib_row.get(month, 0)

    calc_income(budget, month)
    update_ded_alt_rows(budget, prev_month, month, cell, init)
    calc_expenses_net(budget, month)
    calc_difference(budget, prev_month, month)
    calc_ytds(budget, prev_month, month)
    return budget, tsp


def update_variables(budget, month, prev_month, cell=None):
    variable_rows = [row for row in budget if row.get('type') == 'v']
    for row in variable_rows:
        header = row['header']
        prev_value = row.get(prev_month)

        if header == "Year":
            row[month] = prev_value + 1 if month == "JAN" else prev_value

        elif header == "Months in Service":
            row[month] = prev_value + 1

        elif header == "Military Housing Area":
            continue

        elif cell is not None and header == cell.get('header') and (month == cell.get('month') or cell.get('repeat')):
            row[month] = cell.get('value')

        else:
            row[month] = prev_value


def update_ent_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat, init=False):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']

    SPECIAL_CALCULATIONS = {
        'Base Pay': calc_base_pay,
        'BAS': calc_bas,
        'BAH': calc_bah,
    }
    
    for row in budget:
        if row.get('sign') == 1:
            template_row = PAY_TEMPLATE[PAY_TEMPLATE['header'] == row['header']]
            is_onetime = not template_row.empty and template_row.iloc[0].get('onetime', False)
            if init and is_onetime:
                row[working_month] = 0.00
            if row['header'] in SPECIAL_CALCULATIONS:
                row[working_month] = SPECIAL_CALCULATIONS[row['header']](budget, working_month)
            elif cell_header is not None and row['header'] == cell_header and (working_month == cell_month or cell_repeat):
                row[working_month] = cell_value
            elif working_month not in row or pd.isna(row[working_month]) or row[working_month] == '' or (isinstance(row[working_month], (list, tuple)) and len(row[working_month]) == 0):
                row[working_month] = row[prev_month]


def update_ded_alt_rows(budget, prev_month, working_month, cell_header, cell_month, cell_value, cell_repeat, init=False):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']

    SPECIAL_CALCULATIONS = {
        'Federal Taxes': calc_federal_taxes,
        'FICA - Social Security': calc_fica_social_security,
        'FICA - Medicare': calc_fica_medicare,
        'SGLI Rate': calc_sgli,
        'State Taxes': calc_state_taxes,
    }

    for row in budget:
        if row.get('sign') == -1:
            template_row = PAY_TEMPLATE[PAY_TEMPLATE['header'] == row['header']]
            is_onetime = not template_row.empty and template_row.iloc[0].get('onetime', False)
            if init and is_onetime:
                row[working_month] = 0.00
            if row['header'] in SPECIAL_CALCULATIONS:
                row[working_month] = SPECIAL_CALCULATIONS[row['header']](budget, working_month)
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
