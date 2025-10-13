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


def init_budgets(les_variables, tsp_variables, month, les_text=None):
    PARAMS_TEMPLATE = flask_app.config['PARAMS_TEMPLATE']

    pay = []
    for _, row in PARAMS_TEMPLATE.iterrows():
        add_row("pay", pay, row['header'], template=PARAMS_TEMPLATE)

    if les_text:
        pay = add_pay_variables(pay, month, les_variables)
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
        pay = add_pay_variables(pay, month, les_variables)
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

    add_mv_pair(pay, 'Difference', month, 0.00)
    pay = convert_numpy_types(pay)
    tsp = convert_numpy_types(tsp)

    return pay, tsp


def add_months(pay, tsp, month, months_num, init=False):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    months = get_months(pay)

    # calculates how many more months to add, starting from latest_month
    months_num_to_add = months_num - len(months)
    latest_month_idx = MONTHS_SHORT.index(month)

    for i in range(months_num_to_add):
        month = MONTHS_SHORT[(latest_month_idx + 1 + i) % 12]
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


def insert_row(pay, months, headers, row_data):
    if row_data['type'] == 'd' or row_data['type'] == 'a':
        sign = -1
    else:
        sign = 1

    value = round(sign * float(row_data['value']), 2)

    if row_data['method'] == 'template':
        row = add_row(pay, row_data['header'], flask_app.config['PAY_TEMPLATE'])
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

        row = add_row(pay, row_data['header'], metadata=row_meta)

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

        row = add_row(pay, row_data['header'], metadata=row_meta)

        percent = float(row_data.get('percent', 0)) / 100
        interest = float(row_data.get('interest', 0)) / 100

        if row_data['method'] == 'tsp':
            trad_row = next((r for r in pay if r['header'] == 'Traditional TSP'), None)
            roth_row = next((r for r in pay if r['header'] == 'Roth TSP'), None)
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
            net_pay_row = next((r for r in pay if r['header'] == 'Net Pay'), None)
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

    return pay, headers


def remove_row(pay, headers, header):
    row = get_row_value('pay', header)
    pay = [r for r in pay if r.get('header').lower() != header.lower()]
    
    if row.get('type') == 'c':
        headers = [h for h in headers if h.get('header').lower() != header.lower()]

    return pay, headers


def add_recommendations(pay, months):
    recs = {}

    # SGLI minimum coverage recommendation
    sgli_months = []
    for month in months:
        sgli_rate = next((row[month] for row in pay if row.get('header', '') == 'SGLI Rate'), 0)
        if sgli_rate == 0:
            sgli_months.append(month)
    if sgli_months:
        recs['sgli'] = {
            'months': sgli_months,
            'text': (
                '<b>SGLI Coverage:</b> For month(s): 'f'{", ".join(sgli_months)}, you have no SGLI coverage. PayLES recommends having at least the minimum amount of SGLI coverage, which is a $3.50 monthly premium for $50,000. This also provides Traumatic Injury Protection Coverage (TSGLI). Learn more at <a href="https://www.insurance.va.gov/sgliSite/default.htm" target="_blank">VA SGLI</a>.'
            )
        }

    # TSP contribution limit recommendation
    #tsp_contribution_limit = flask_app.config['TSP_ELECTIVE_LIMIT']
    #tsp_contrib_months = []
    #for month in months:
    #    ytd_trad = next((row[month] for row in pay if row.get('header', '') == 'YTD Trad TSP'), 0)
    #    ytd_roth = next((row[month] for row in pay if row.get('header', '') == 'YTD Roth TSP'), 0)
    #    if (ytd_trad + ytd_roth) >= tsp_contribution_limit:
    #        tsp_contrib_months.append(month)
    #if tsp_contrib_months:
    #    recs['tsp_contribution_limit'] = {
    #        'months': tsp_contrib_months,
    #        'text': (
    #            '<b>TSP Contribution Limit:</b> For month(s): 'f'{", ".join(tsp_contrib_months)}, the TSP contribution limit of ${tsp_contribution_limit} has been reached. Any additional contributions not made within a combat zone towards the Traditional TSP will not be deducted. PayLES recommends adjusting your TSP contribution rates to avoid reaching the contribution limit. Learn more at <a href="https://www.tsp.gov/making-contributions/contribution-limits/" target="_blank">TSP Contribution Limits</a>.'
    #        )
    #    }

    # TSP annual limit recommendation
    #tsp_annual_limit = flask_app.config['TSP_ANNUAL_LIMIT']
    #tsp_annual_months = []
    #for month in months:
    #    ytd_trad = next((row[month] for row in pay if row.get('header', '') == 'YTD Trad TSP'), 0)
    #    ytd_trad_exempt = next((row[month] for row in pay if row.get('header', '') == 'YTD Trad TSP Exempt'), 0)
    #    ytd_roth = next((row[month] for row in pay if row.get('header', '') == 'YTD Roth TSP'), 0)
    #    ytd_matching = next((row[month] for row in pay if row.get('header', '') == 'YTD TSP Matching'), 0)
    #    if (ytd_trad + ytd_trad_exempt + ytd_roth + ytd_matching) >= tsp_annual_limit:
    #        tsp_annual_months.append(month)
    #if tsp_annual_months:
    #    recs['tsp_annual_limit'] = {
    #        'months': tsp_annual_months,
    #        'text': (
    #            '<b>TSP Annual Limit:</b> For month(s): 'f'{", ".join(tsp_annual_months)}, the TSP annual limit of ${tsp_annual_limit} has been reached. Any additional contributions will not be deducted. PayLES recommends adjusting your TSP contribution rates to avoid reaching the contribution limit. Learn more at <a href="https://www.tsp.gov/making-contributions/contribution-limits/" target="_blank">TSP Contribution Limits</a>.'
    #        )
    #    }

    # Combat zone TSP recommendation
    #combat_zone_months = []
    #for month in months:
    #    combat_zone = next((row[month] for row in pay if row.get('header', '') == 'Combat Zone'), "No")
    #    if str(combat_zone).strip().lower() == "yes":
    #        combat_zone_months.append(month)
    #if combat_zone_months:
    #    recs['combat_zone_tsp'] = {
    #        'months': combat_zone_months,
    #        'text': (
    #            '<b>Combat Zone:</b> For month(s): 'f'{", ".join(combat_zone_months)}, you are anticipating being in a combat zone. PayLES recommends taking full advantage of the TSP combat zone tax exclusion (CZTE) benefit by contributing as much as practical to the Traditional TSP. Learn more at <a href="https://themilitarywallet.com/maximizing-your-thrift-savings-plan-contributions-in-a-combat-zone/" target="_blank">How to Maximize TSP Contributions in a Combat Zone</a>.'
    #        )
    #    }

    # negative net pay recommendation
    negative_net_pay_months = []
    for month in months:
        net_pay = next((row[month] for row in pay if row.get('header', '') == 'Net Pay'), 0)
        if net_pay < 0:
            negative_net_pay_months.append(month)
    if negative_net_pay_months:
        recs['negative_net_pay'] = {
            'months': negative_net_pay_months,
            'text': (
                '<b>Negative Net Pay:</b> For month(s): 'f'{", ".join(negative_net_pay_months)}, you have a negative net pay. PayLES recommends recalculating parts of your pay to avoid a negative net pay as that can potentially incur debts and missed payments for deductions or allotments. Learn more about U.S. military debts at <a href="https://www.dfas.mil/debtandclaims/" target="_blank">DFAS Debts & Claims</a>.'
            )
        }

    # TSP matching recommendation
    #months_in_service = None
    #for row in pay:
    #    if row.get('header', '') == 'Months in Service':
    #        # Use the first month found (should be the same for all months)
    #        months_in_service = next((row[m] for m in months if m in row), None)
    #        break

    #tsp_matching_months = []
    #if months_in_service is not None and months_in_service >= 24:
    #    for month in months:
    #        trad_rate = next((row[month] for row in pay if row.get('header', '') == 'Trad TSP Base Rate'), 0)
    #        roth_rate = next((row[month] for row in pay if row.get('header', '') == 'Roth TSP Base Rate'), 0)
    #        if (trad_rate + roth_rate) < 5:
    #            tsp_matching_months.append(month)
    #if tsp_matching_months:
    #    recs['tsp_matching'] = {
    #        'months': tsp_matching_months,
    #        'text': (
    #            '<b>TSP Matching:</b> For month(s): 'f'{", ".join(tsp_matching_months)}, you are fully vested in the TSP however are not taking full advantage of the 1%-4% agency matching for TSP contributions. PayLES recommends to have the combined total of your Traditional TSP base rate and Roth TSP base rate to be at least 5% to get the highest agency matching rate. Your current combined rate is {trad_rate + roth_rate}%. Learn more at <a href="https://www.tsp.gov/making-contributions/contribution-types/" target="_blank">TSP Contribution Types</a>.'
    #        )
    #    }


    # state income tax recommendation
    HOME_OF_RECORDS = flask_app.config['HOME_OF_RECORDS']
    home_of_record_row = next((row for row in pay if row.get('header', '') == "Home of Record"), None)
    mha_row = next((row for row in pay if row.get('header', '') == "Military Housing Area"), None)

    if home_of_record_row and mha_row:
        taxed_states = {}
        for month in months:
            home_of_record = home_of_record_row.get(month)

            if not home_of_record or home_of_record == "Not Found":
                continue
            hor_row = HOME_OF_RECORDS[HOME_OF_RECORDS['abbr'] == home_of_record]

            if hor_row.empty:
                continue
            income_taxed = hor_row['income_taxed'].values[0].lower()

            if income_taxed in ("none", "exempt"):
                continue
            mha_code = mha_row.get(month)
            mha_state = mha_code[:2] if mha_code and len(mha_code) >= 2 else ""

            if income_taxed == "outside":
                if mha_state == home_of_record:
                    taxed_states.setdefault(home_of_record, []).append(month)
            elif income_taxed == "full":
                taxed_states.setdefault(home_of_record, []).append(month)

        for hor, taxed_months in taxed_states.items():
            if taxed_months:

                longname_row = HOME_OF_RECORDS[HOME_OF_RECORDS['abbr'] == hor]
                longname = longname_row['longname'].values[0] if not longname_row.empty else hor
                recs[f'state_tax_{hor}'] = {
                    'months': taxed_months,
                    'text': (
                        f'<b>State Income Tax:</b> For month(s): {", ".join(taxed_months)}, your home of record - {longname} - is taxing your military pay. PayLES recommends changing your home of record, if possible, to a state/territory which either has no state income tax, fully exempts military income, or does not tax military income when stationed outside of the home of record. View the <a href="/static/graphics/military_income_state_taxed_map.png" target="_blank">Military Income State Taxed Map</a>, and learn more at <a href="https://www.military.com/money/personal-finance/state-tax-information.html" target="_blank">Military State Tax Info</a>.'
                    )
                }

    return [rec['text'] for rec in recs.values()]