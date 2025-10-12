from datetime import datetime
import pandas as pd
import re

from app import flask_app
from app.utils import (
    get_error_context,
    convert_numpy_types,
    get_row_value,
    add_row,
    add_mv_pair,
    set_variable_longs,
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
    calc_conus_cola,
    calc_oconus_cola,
    calc_oha,
    calc_miha_m,
    calc_federal_taxes,
    calc_fica_social_security,
    calc_fica_medicare,
    calc_sgli,
    calc_state_taxes,
)
from app.tsp import (
    init_tsp,
    update_tsp,
)


# =========================
# get variables and init budget
# =========================

def get_les_variables(les_text):
    try:
        month = les_text.get('les_month', None)
        if month not in flask_app.config['MONTHS_SHORT']:
            raise ValueError(f"Invalid LES month: {month}")
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

    return month, les_variables


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
        budget = add_pays(budget, month, sign=1)

        taxable, nontaxable, income = calc_income(budget, month)
        add_mv_pair(budget, 'Taxable Income', month, taxable)
        add_mv_pair(budget, 'Non-Taxable Income', month, nontaxable)
        add_mv_pair(budget, 'Total Income', month, income)

        tsp = init_tsp(tsp_variables, budget, month)

        budget = add_pays(budget, month, sign=-1)
        add_mv_pair(budget, 'Traditional TSP', month, -(get_row_value(tsp, 'Trad TSP Contribution', month) + get_row_value(tsp, 'Trad TSP Exempt Contribution', month)))
        add_mv_pair(budget, 'Roth TSP', month, -(get_row_value(tsp, 'Roth TSP Contribution', month)))

        taxes, expenses, net_pay = calc_expenses_net(budget, month)
        add_mv_pair(budget, 'Taxes', month, taxes)
        add_mv_pair(budget, 'Total Expenses', month, expenses)
        add_mv_pair(budget, 'Net Pay', month, net_pay)

        ytd_income, ytd_expenses, ytd_net_pay = calc_ytds(budget, month)
        add_mv_pair(budget, 'YTD Income', month, ytd_income)
        add_mv_pair(budget, 'YTD Expenses', month, ytd_expenses)
        add_mv_pair(budget, 'YTD Net Pay', month, ytd_net_pay)

    add_mv_pair(budget, 'Difference', month, 0.00)
    budget = convert_numpy_types(budget)
    tsp = convert_numpy_types(tsp)

    return budget, tsp


def add_variables(budget, month, variables):
    for var, val in variables.items():
        row = next((row for row in budget if row.get('header') == var), None)
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


def add_pays(budget, month, sign):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']
    TRIGGER_CALCULATIONS = flask_app.config['TRIGGER_CALCULATIONS']

    pay_subset = PAY_TEMPLATE[(PAY_TEMPLATE['sign'] == sign) & (PAY_TEMPLATE['trigger'] != "none")]

    for _, row in pay_subset.iterrows():
        header = row['header']
        trigger = row['trigger']
        variable = get_row_value(budget, trigger, month)

        if variable not in [0, None, "NOT FOUND"]:
            function = globals().get(TRIGGER_CALCULATIONS[header])
            if callable(function):
                value = function(budget, month)
                
                add_row("budget", budget, header, template=PAY_TEMPLATE)
                add_mv_pair(budget, header, month, value)

    if sign == -1:
        add_row("budget", budget, 'Traditional TSP', template=PAY_TEMPLATE)
        add_row("budget", budget, 'Roth TSP', template=PAY_TEMPLATE)

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

def add_months(budget, tsp, month, months_num, init=False):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    months = get_months(budget)

    # calculates how many more months to add, starting from latest_month
    months_num_to_add = months_num - len(months)
    latest_month_idx = MONTHS_SHORT.index(month)

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
        budget, tsp = build_month(budget, tsp, months[i], months[i-1], cell=cell)

    return budget, tsp


def build_month(budget, tsp, month, prev_month, cell=None, init=False):
    budget = update_variables(budget, month, prev_month, cell)
    budget = update_pays(budget, month, prev_month, sign=1, cell=cell, init=init)

    taxable, nontaxable, income = calc_income(budget, month)
    add_mv_pair(budget, 'Taxable Income', month, taxable)
    add_mv_pair(budget, 'Non-Taxable Income', month, nontaxable)
    add_mv_pair(budget, 'Total Income', month, income)

    tsp = update_tsp(budget, tsp, month, prev_month, cell=cell)

    trad_tsp_row = next((r for r in budget if r.get('header') == "Traditional TSP"), None)
    roth_tsp_row = next((r for r in budget if r.get('header') == "Roth TSP"), None)

    if trad_tsp_row:
        trad_tsp_row[month] = -(get_row_value(tsp, 'Trad TSP Contribution', month) + get_row_value(tsp, 'Trad TSP Exempt Contribution', month))
    if roth_tsp_row:
        roth_tsp_row[month] = -(get_row_value(tsp, 'Roth TSP Contribution', month))

    budget = update_pays(budget, month, prev_month, sign=-1, cell=cell, init=init)

    taxes, expenses, net_pay = calc_expenses_net(budget, month)
    add_mv_pair(budget, 'Taxes', month, taxes)
    add_mv_pair(budget, 'Total Expenses', month, expenses)
    add_mv_pair(budget, 'Net Pay', month, net_pay)

    difference = calc_difference(budget, month, prev_month)
    add_mv_pair(budget, 'Difference', month, difference)

    ytd_income, ytd_expenses, ytd_net_pay = calc_ytds(budget, month, prev_month=prev_month)
    add_mv_pair(budget, 'YTD Income', month, ytd_income)
    add_mv_pair(budget, 'YTD Expenses', month, ytd_expenses)
    add_mv_pair(budget, 'YTD Net Pay', month, ytd_net_pay)

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

    budget = set_variable_longs(budget, month)
    return budget


def update_pays(budget, month, prev_month, sign, cell=None, init=False):
    PAY_TEMPLATE = flask_app.config['PAY_TEMPLATE']
    TRIGGER_CALCULATIONS = flask_app.config['TRIGGER_CALCULATIONS']

    rows = [row for row in budget if row.get('sign') == sign]
    for row in rows:
        header = row['header']
        prev_value = row.get(prev_month)

        if header in ["Traditional TSP", "Roth TSP"]:
            continue

        template_row = PAY_TEMPLATE[PAY_TEMPLATE['header'] == header]
        onetime = template_row.iloc[0].get('onetime', False)
        if init and onetime:
            row[month] = 0.00
            continue

        trigger = TRIGGER_CALCULATIONS.get(header)
        function = globals().get(trigger)
        if callable(function):
            row[month] = function(budget, month)
            continue

        if cell is not None and header == cell.get('header') and (month == cell.get('month') or cell.get('repeat')):
            row[month] = cell.get('value')
        else:
            row[month] = prev_value

    return budget


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
