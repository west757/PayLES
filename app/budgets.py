from app import flask_app
from app.pay import (
    add_pay_variables,
    add_les_pay,
    add_calc_pay,
    add_ytds,
    update_variables,
    update_pays,
)
from app.calculations import (
    calc_income,
    calc_expenses_net,
    calc_difference,
    calc_ytds,
)
from app.tsp import (
    init_tsp,
    update_tsp,
)
from app.utils import (
    convert_numpy_types,
    get_row_value,
    add_row,
    add_mv_pair,
    get_months,
)


def init_budgets(pay_variables, tsp_variables, year, month, les_text=None):
    PARAMS_TEMPLATE = flask_app.config['PARAMS_TEMPLATE']

    pay = []
    for _, row in PARAMS_TEMPLATE.iterrows():
        add_row(pay, row['header'], template=PARAMS_TEMPLATE)

    add_mv_pair(pay, 'Year', month, year)

    if les_text:
        pay = add_pay_variables(pay, month, pay_variables)
        pay = add_les_pay(pay, month, les_text)

        taxable, nontaxable, income = calc_income(pay, month)
        add_mv_pair(pay, 'Taxable Income', month, taxable)
        add_mv_pair(pay, 'Non-Taxable Income', month, nontaxable)
        add_mv_pair(pay, 'Total Income', month, income)

        tsp = init_tsp(tsp_variables, pay, month, les_text)
        
        taxes, expenses, net_pay = calc_expenses_net(pay, month)
        add_mv_pair(pay, 'Taxes', month, taxes)
        add_mv_pair(pay, 'Total Expenses', month, expenses)
        add_mv_pair(pay, 'Net Pay', month, net_pay)

        pay = add_ytds(pay, month, les_text)
    else:
        pay = add_pay_variables(pay, month, pay_variables)
        pay = add_calc_pay(pay, month, sign=1)

        taxable, nontaxable, income = calc_income(pay, month)
        add_mv_pair(pay, 'Taxable Income', month, taxable)
        add_mv_pair(pay, 'Non-Taxable Income', month, nontaxable)
        add_mv_pair(pay, 'Total Income', month, income)

        tsp = init_tsp(tsp_variables, pay, month)

        pay = add_calc_pay(pay, month, sign=-1)
        add_mv_pair(pay, 'Traditional TSP', month, -(get_row_value(tsp, 'Trad TSP Contribution', month) + get_row_value(tsp, 'Trad TSP Exempt Contribution', month)))
        add_mv_pair(pay, 'Roth TSP', month, -(get_row_value(tsp, 'Roth TSP Contribution', month)))

        taxes, expenses, net_pay = calc_expenses_net(pay, month)
        add_mv_pair(pay, 'Taxes', month, taxes)
        add_mv_pair(pay, 'Total Expenses', month, expenses)
        add_mv_pair(pay, 'Net Pay', month, net_pay)

        ytd_income, ytd_expenses, ytd_net_pay = calc_ytds(pay, month)
        add_mv_pair(pay, 'YTD Income', month, ytd_income)
        add_mv_pair(pay, 'YTD Expenses', month, ytd_expenses)
        add_mv_pair(pay, 'YTD Net Pay', month, ytd_net_pay)

    add_mv_pair(pay, 'Difference', month, 0.0)

    add_mv_pair(pay, 'Direct Deposit Account', month, 0.0)
    add_mv_pair(tsp, 'TSP Account',  month, 0.0)

    pay = convert_numpy_types(pay)
    tsp = convert_numpy_types(tsp)

    return pay, tsp


def add_months(pay, tsp, month, months_num, init=False):
    MONTHS = list(flask_app.config['MONTHS'].keys())
    months = get_months(pay)

    # calculates how many more months to add, starting from latest_month
    months_num_to_add = months_num - len(months)
    latest_month_idx = MONTHS.index(month)

    for i in range(months_num_to_add):
        month = MONTHS[(latest_month_idx + 1 + i) % 12]
        pay, tsp = build_month(pay, tsp, month, months[-1], init=init)
        months.append(month)

    return pay, tsp, months


def update_months(pay, tsp, months, cell=None):
    # if cell is provided, start from that month and update from there
    # else, start from the second month to update entire budget
    if cell:
        start_idx = months.index(cell.get('month'))
    else:
        start_idx = 1

    for i in range(start_idx, len(months)):
        pay, tsp = build_month(pay, tsp, months[i], months[i-1], cell=cell)

    return pay, tsp


def build_month(pay, tsp, month, prev_month, cell=None, init=False):
    prev_year = get_row_value(pay, 'Year', prev_month)
    year = prev_year + 1 if month == 'JAN' else prev_year
    add_mv_pair(pay, 'Year', month, year)

    pay = update_variables(pay, month, prev_month, cell)
    pay = update_pays(pay, month, prev_month, sign=1, cell=cell, init=init)

    taxable, nontaxable, income = calc_income(pay, month)
    add_mv_pair(pay, 'Taxable Income', month, taxable)
    add_mv_pair(pay, 'Non-Taxable Income', month, nontaxable)
    add_mv_pair(pay, 'Total Income', month, income)

    tsp = update_tsp(pay, tsp, month, prev_month, cell=cell)

    trad_tsp_row = get_row_value(pay, 'Traditional TSP')
    roth_tsp_row = get_row_value(pay, 'Roth TSP')

    if trad_tsp_row:
        trad_tsp_row[month] = -(get_row_value(tsp, 'Trad TSP Contribution', month) + get_row_value(tsp, 'Trad TSP Exempt Contribution', month))
    if roth_tsp_row:
        roth_tsp_row[month] = -(get_row_value(tsp, 'Roth TSP Contribution', month))

    pay = update_pays(pay, month, prev_month, sign=-1, cell=cell, init=init)

    taxes, expenses, net_pay = calc_expenses_net(pay, month)
    add_mv_pair(pay, 'Taxes', month, taxes)
    add_mv_pair(pay, 'Total Expenses', month, expenses)
    add_mv_pair(pay, 'Net Pay', month, net_pay)

    difference = calc_difference(pay, month, prev_month)
    add_mv_pair(pay, 'Difference', month, difference)

    ytd_income, ytd_expenses, ytd_net_pay = calc_ytds(pay, month, prev_month=prev_month)
    add_mv_pair(pay, 'YTD Income', month, ytd_income)
    add_mv_pair(pay, 'YTD Expenses', month, ytd_expenses)
    add_mv_pair(pay, 'YTD Net Pay', month, ytd_net_pay)

    update_account(pay, "Direct Deposit Account", month=month, prev_month=prev_month)
    update_account(tsp, "TSP Account", month=month, prev_month=prev_month)

    return pay, tsp


def remove_months(pay, tsp, months_num):
    months = get_months(pay)
    months_to_remove = months[months_num:]

    for row in pay:
        for month in months_to_remove:
            if month in row:
                del row[month]
    for row in tsp:
        for month in months_to_remove:
            if month in row:
                del row[month]
    months = months[:months_num]

    return pay, tsp, months


def insert_row(pay, months, headers, insert):
    sign = flask_app.config['TYPE_SIGN'][get_row_value(pay, insert['header'], 'type')]
    value = round(sign * float(insert['value']), 2)

    if insert['method'] == 'template':
        add_row(pay, insert['header'], flask_app.config['PAY_TEMPLATE'])
        row = get_row_value(pay, insert['header'])

        for idx, m in enumerate(months):
            row[m] = 0.0 if idx == 0 else value

    elif insert['method'] == 'custom':
        metadata = {}
        metadata['type'] = insert['type']
        metadata['field'] = 'float'
        metadata['tax'] = insert['tax']
        metadata['editable'] = True
        metadata['modal'] = 'none'

        add_row(pay, insert['header'], metadata=metadata)
        row = get_row_value(pay, insert['header'])

        for idx, m in enumerate(months):
            row[m] = 0.0 if idx == 0 else value

        headers.append({
            'header': insert['header'],
            'type': insert['type'],
            'tooltip': 'Custom row added by user',
        })

    pay = convert_numpy_types(pay)

    return pay, headers


def remove_row(pay, headers, header):
    row = get_row_value(pay, header)
    pay = [r for r in pay if r.get('header').lower() != header.lower()]
    
    if row.get('type') == 'c':
        headers = [h for h in headers if h.get('header').lower() != header.lower()]

    return pay, headers


def update_account(budget, header, month=None, prev_month=None, months=None, initial=None,):
    if header == "Direct Deposit Account":
        add_row = "Net Pay"
    elif header == "TSP Account":
        add_row = "TSP Contribution Total"
    else:
        return None

    row = get_row_value(budget, header)

    # if months and initial are provided, rewrite the entire row
    if months is not None and initial is not None:
        prev_value = initial
        for idx, m in enumerate(months):
            if idx == 0:
                row[m] = round(prev_value, 2)
            else:
                add_value = get_row_value(budget, add_row, m)
                value = prev_value + add_value if add_value > 0 else prev_value
                row[m] = round(value, 2)
                prev_value = value
    # otherwise, just update the current month using previous value
    elif month is not None and prev_month is not None:
        prev_value = row.get(prev_month, initial)
        add_value = get_row_value(budget, add_row, month)
        value = prev_value + add_value if add_value > 0 else prev_value
        row[month] = round(value, 2)

    return None
