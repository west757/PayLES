from bisect import bisect_right

from app import flask_app


# =========================
# calculation functions
# =========================

def calculate_taxable_income(budget, month, init=False):
    taxable = 0.00
    nontaxable = 0.00

    # Find Combat Zone value
    combat_zone_row = next((row for row in budget if row['header'] == "Combat Zone"), None)
    combat_zone = combat_zone_row[month] if combat_zone_row and month in combat_zone_row else "No"

    for row in budget:
        if row.get('type') == 'e' and month in row:
            value = row[month]
            tax = row.get('tax', False)

            if combat_zone == "Yes":
                nontaxable += value
            else:
                if tax:
                    taxable += value
                else:
                    nontaxable += value

    taxable = round(taxable, 2)
    nontaxable = round(nontaxable, 2)

    if init:
        budget.append({'header': 'Taxable Income', month: taxable})
        budget.append({'header': 'Non-Taxable Income', month: nontaxable})
    else:
        for row in budget:
            if row['header'] == 'Taxable Income':
                row[month] = taxable
            elif row['header'] == 'Non-Taxable Income':
                row[month] = nontaxable

    return budget


def calculate_total_taxes(budget, month, init=False):
    total_taxes = 0.00

    for row in budget:
        if row.get('type') in ('d', 'a') and row.get('tax', False) and month in row:
            total_taxes += row[month]

    total_taxes = round(total_taxes, 2)

    if init:
        budget.append({'header': 'Total Taxes', month: total_taxes})
    else:
        for row in budget:
            if row['header'] == 'Total Taxes':
                row[month] = total_taxes

    return budget


def calculate_gross_net_pay(budget, month, init=False):
    gross_pay = 0.00
    for row in budget:
        if row.get('type') == 'e' and month in row:
            gross_pay += row[month]

    net_pay = gross_pay
    for row in budget:
        if row.get('type') in ('d', 'a') and month in row:
            net_pay += row[month]

    gross_pay = round(gross_pay, 2)
    net_pay = round(net_pay, 2)

    if init:
        budget.append({'header': 'Gross Pay', month: gross_pay})
        budget.append({'header': 'Net Pay', month: net_pay})
    else:
        for row in budget:
            if row['header'] == 'Gross Pay':
                row[month] = gross_pay
            elif row['header'] == 'Net Pay':
                row[month] = net_pay

    return budget


def calculate_difference(budget, month_headers, month_idx):
    prev_month = month_headers[month_idx - 1]
    next_month = month_headers[month_idx]

    net_pay_row = next((r for r in budget if r['header'] == "Net Pay"), None)
    difference_row = next((r for r in budget if r['header'] == "Difference"), None)

    difference_row[next_month] = net_pay_row[next_month] - net_pay_row[prev_month]



# =========================
# calculate special rows
# =========================

def calculate_base_pay(budget, next_month):
    PAY_ACTIVE = flask_app.config['PAY_ACTIVE']
    grade_row = next((row for row in budget if row['header'] == "Grade"), None)
    months_row = next((row for row in budget if row['header'] == "Months in Service"), None)
    grade = grade_row.get(next_month) if grade_row else "Not Found"
    months_in_service = int(months_row.get(next_month, 0)) if months_row else 0

    pay_row = PAY_ACTIVE[PAY_ACTIVE["grade"] == grade]

    month_cols = []
    for col in pay_row.columns:
        if col != "grade":
            month_cols.append(int(col))
    month_cols.sort()

    idx = bisect_right(month_cols, months_in_service) - 1
    selected_month_num = str(month_cols[idx])

    base_pay = pay_row[selected_month_num].iloc[0]
    return round(base_pay, 2)


def calculate_bas(budget, next_month):
    BAS_AMOUNT = flask_app.config['BAS_AMOUNT']
    grade_row = next((row for row in budget if row['header'] == "Grade"), None)
    grade = grade_row.get(next_month) if grade_row else "Not Found"

    if str(grade).startswith("E"):
        bas = BAS_AMOUNT[0]
    else:
        bas = BAS_AMOUNT[1]

    return round(bas, 2)


def calculate_bah(budget, next_month):
    grade_row = next((row for row in budget if row['header'] == "Grade"), None)
    mha_row = next((row for row in budget if row['header'] == "Military Housing Area"), None)
    dependents_row = next((row for row in budget if row['header'] == "Dependents"), None)

    grade = grade_row[next_month]
    military_housing_area = mha_row[next_month]
    dependents = dependents_row[next_month]
    
    if military_housing_area == "Not Found":
        return 0.00

    if dependents > 0:
        BAH_DF = flask_app.config['BAH_WITH_DEPENDENTS']
    else:
        BAH_DF = flask_app.config['BAH_WITHOUT_DEPENDENTS']

    bah_row = BAH_DF[BAH_DF["mha"] == military_housing_area]
    bah = bah_row[grade].values[0]
    return round(bah, 2)


def calculate_federal_taxes(budget, next_month):
    TAX_FILING_TYPES_DEDUCTIONS = flask_app.config['TAX_FILING_TYPES_DEDUCTIONS']
    FEDERAL_TAX_RATES = flask_app.config['FEDERAL_TAX_RATES']
    filing_status_row = next((row for row in budget if row['header'] == "Federal Filing Status"), None)
    taxable_income_row = next((row for row in budget if row['header'] == "Taxable Income"), None)

    filing_status = filing_status_row.get(next_month) if filing_status_row else "Not Found"
    taxable_income = taxable_income_row.get(next_month, 0.00) if taxable_income_row else 0.00
    taxable_income = taxable_income * 12
    tax = 0.00

    if filing_status == "Not Found":
        return 0.00

    deduction = TAX_FILING_TYPES_DEDUCTIONS[filing_status]
    taxable_income -= deduction
    taxable_income = max(taxable_income, 0)

    brackets = FEDERAL_TAX_RATES[FEDERAL_TAX_RATES['status'] == filing_status]
    brackets = brackets.sort_values(by='bracket').reset_index(drop=True)

    for i in range(len(brackets)):
        lower_bracket = brackets.at[i, 'bracket']
        rate = brackets.at[i, 'rate']

        if i + 1 < len(brackets):
            upper_bracket = brackets.at[i + 1, 'bracket']
        else:
            upper_bracket = 10**7

        if taxable_income > lower_bracket:
            taxable_at_rate = min(taxable_income, upper_bracket) - lower_bracket
            tax += taxable_at_rate * rate

    tax = tax / 12
    return -round(tax, 2)


def calculate_fica_social_security(budget, next_month):
    FICA_SOCIALSECURITY_TAX_RATE = flask_app.config['FICA_SOCIALSECURITY_TAX_RATE']
    taxable_income_row = next((row for row in budget if row['header'] == "Taxable Income"), None)
    taxable_income = taxable_income_row.get(next_month, 0.00) if taxable_income_row else 0.00
    return round(-taxable_income * FICA_SOCIALSECURITY_TAX_RATE, 2)

def calculate_fica_medicare(budget, next_month):
    FICA_MEDICARE_TAX_RATE = flask_app.config['FICA_MEDICARE_TAX_RATE']
    taxable_income_row = next((row for row in budget if row['header'] == "Taxable Income"), None)
    taxable_income = taxable_income_row.get(next_month, 0.00) if taxable_income_row else 0.00
    return round(-taxable_income * FICA_MEDICARE_TAX_RATE, 2)


def calculate_sgli(budget, next_month):
    SGLI_RATES = flask_app.config['SGLI_RATES']
    coverage_row = next((row for row in budget if row['header'] == "SGLI Coverage"), None)
    coverage = str(coverage_row.get(next_month)) if coverage_row and next_month in coverage_row else "0"
    row = SGLI_RATES[SGLI_RATES['coverage'] == coverage]
    total = row.iloc[0]['total'] if not row.empty else 0
    return -abs(total)


def calculate_state_taxes(budget, next_month):
    STATE_TAX_RATES = flask_app.config['STATE_TAX_RATES']
    home_of_record_row = next((row for row in budget if row['header'] == "Home of Record"), None)
    filing_status_row = next((row for row in budget if row['header'] == "State Filing Status"), None)
    taxable_income_row = next((row for row in budget if row['header'] == "Taxable Income"), None)

    home_of_record = home_of_record_row.get(next_month) if home_of_record_row else "Not Found"
    filing_status = filing_status_row.get(next_month) if filing_status_row else "Single"
    taxable_income = taxable_income_row.get(next_month, 0.00) if taxable_income_row else 0.00
    taxable_income = taxable_income * 12
    tax = 0.00

    state_brackets = STATE_TAX_RATES[STATE_TAX_RATES['state'] == home_of_record]

    if filing_status == "Single":
        brackets = state_brackets[['single_bracket', 'single_rate']].rename(columns={'single_bracket': 'bracket', 'single_rate': 'rate'})
    elif filing_status == "Married":
        brackets = state_brackets[['married_bracket', 'married_rate']].rename(columns={'married_bracket': 'bracket', 'married_rate': 'rate'})
    else:
        return 0.00

    brackets = brackets.sort_values(by='bracket').reset_index(drop=True)
    
    for i in range(len(brackets)):
        lower_bracket = brackets.at[i, 'bracket']
        rate = brackets.at[i, 'rate']

        if i + 1 < len(brackets):
            upper_bracket = brackets.at[i + 1, 'bracket']
        else:
            upper_bracket = 10**7

        if taxable_income > lower_bracket:
            taxable_rate = min(taxable_income, upper_bracket) - lower_bracket
            tax += taxable_rate * rate

    tax = tax / 12
    return -round(tax, 2)


def calculate_trad_roth_tsp(budget, next_month):
    VARIABLE_TEMPLATE = flask_app.config['VARIABLE_TEMPLATE']
    tsp_rows = VARIABLE_TEMPLATE[VARIABLE_TEMPLATE['type'] == 't']
    trad_total = 0.00
    roth_total = 0.00

    specialty_rows = [row['header'] for row in budget if row.get('modal') == 'specialty' and row.get('sign') == 1]
    incentive_rows = [row['header'] for row in budget if row.get('modal') == 'incentive' and row.get('sign') == 1]
    bonus_rows = [row['header'] for row in budget if row.get('modal') == 'bonus' and row.get('sign') == 1]

    # Helper to get value from budget for a header
    def get_value(header):
        row = next((r for r in budget if r['header'] == header), None)
        return row.get(next_month, 0) if row and next_month in row else 0.00

    for _, tsp_row in tsp_rows.iterrows():
        tsp_var = tsp_row['header']
        rate = get_value(tsp_var)

        if rate > 0:
            if 'Base' in tsp_var:
                total = get_value('Base Pay')
            elif 'Specialty' in tsp_var:
                total = sum(get_value(h) for h in specialty_rows)
            elif 'Incentive' in tsp_var:
                total = sum(get_value(h) for h in incentive_rows)
            elif 'Bonus' in tsp_var:
                total = sum(get_value(h) for h in bonus_rows)
            else:
                total = 0.00

            value = total * rate / 100

            if tsp_var.startswith("Trad"):
                trad_total += value
            elif tsp_var.startswith("Roth"):
                roth_total += value

    return -round(trad_total, 2), -round(roth_total, 2)