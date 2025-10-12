from app import flask_app

from app.utils import (
    get_row_value,
)

# =========================
# calculation functions
# =========================

def calc_income(budget, month):
    taxable = 0.00
    nontaxable = 0.00

    combat_zone = get_row_value(budget, "Combat Zone", month)

    income_rows = [row for row in budget if row.get('sign') == 1]
    for row in income_rows:
        value = row[month]
        tax = row.get('tax')

        if row.get('type') == 'c':
            if tax:
                taxable += value
            else:
                nontaxable += value
        else:
            if combat_zone == "Yes":
                nontaxable += value
            else:
                if tax:
                    taxable += value
                else:
                    nontaxable += value

    taxable = round(taxable, 2)
    nontaxable = round(nontaxable, 2)
    income = round(taxable + nontaxable, 2)

    return taxable, nontaxable, income


def calc_expenses_net(budget, month):
    taxes = 0.00
    expenses = 0.00

    expense_rows = [row for row in budget if row.get('sign') == -1]
    for row in expense_rows:
        expenses += row[month]
        if row.get('tax', False):
            taxes += row[month]

    income = get_row_value(budget, 'Total Income', month)
    net_pay = income + expenses
    expenses = round(expenses, 2)
    taxes = round(taxes, 2)
    net_pay = round(net_pay, 2)

    return taxes, expenses, net_pay


def calc_difference(budget, month, prev_month):
    difference = round(get_row_value(budget, "Net Pay", month) - get_row_value(budget, "Net Pay", prev_month), 2)
    return difference


def calc_ytds(budget, month, prev_month=None):
    ytd_income = get_row_value(budget, 'YTD Income', prev_month) if prev_month else 0
    ytd_expenses = get_row_value(budget, 'YTD Expenses', prev_month) if prev_month else 0
    ytd_net_pay = get_row_value(budget, 'YTD Net Pay', prev_month) if prev_month else 0

    income = get_row_value(budget, 'Total Income', month)
    expenses = get_row_value(budget, 'Total Expenses', month)
    net_pay = get_row_value(budget, 'Net Pay', month)

    ytd_income = income if month == "JAN" else round(ytd_income + income, 2)
    ytd_expenses = expenses if month == "JAN" else round(ytd_expenses + expenses, 2)
    ytd_net_pay = net_pay if month == "JAN" else round(ytd_net_pay + net_pay, 2)

    return ytd_income, ytd_expenses, ytd_net_pay



# =========================
# calculate special rows
# =========================

def calc_base_pay(budget, month):
    PAY_ACTIVE = flask_app.config['PAY_ACTIVE']
    grade = get_row_value(budget, "Grade", month)
    months_in_service = get_row_value(budget, "Months in Service", month)

    pay_row = PAY_ACTIVE[PAY_ACTIVE["grade"] == grade]
    month_cols = [int(col) * 12 for col in pay_row.columns[1:]]

    idx = 0
    for i, m in enumerate(month_cols):
        if months_in_service < m:
            idx = i - 1 if i > 0 else 0
            break

    selected_col = pay_row.columns[idx + 1]

    base_pay = pay_row[selected_col].iloc[0]
    return round(float(base_pay), 2)


def calc_bas(budget, month):
    BAS_AMOUNT = flask_app.config['BAS_AMOUNT']
    grade = get_row_value(budget, "Grade", month)

    if str(grade).startswith("E"):
        bas = BAS_AMOUNT[0]
    else:
        bas = BAS_AMOUNT[1]

    return round(float(bas), 2)


def calc_bah(budget, month):
    grade = get_row_value(budget, "Grade", month)
    military_housing_area_code = get_row_value(budget, "Military Housing Area Code", month)
    dependents = get_row_value(budget, "Dependents", month)
    
    if military_housing_area_code == "Not Found":
        return 0.00

    if dependents > 0:
        BAH_DF = flask_app.config['BAH_WITH_DEPENDENTS']
    else:
        BAH_DF = flask_app.config['BAH_WITHOUT_DEPENDENTS']

    bah_row = BAH_DF[BAH_DF["mha"] == military_housing_area_code]
    bah = bah_row[grade].values[0]
    return round(float(bah), 2)


def calc_federal_taxes(budget, month):
    FEDERAL_TAX_RATES = flask_app.config['FEDERAL_TAX_RATES']
    filing_status = get_row_value(budget, "Federal Filing Status", month)
    taxable_income = get_row_value(budget, "Taxable Income", month) * 12

    tax = 0.00

    if filing_status == "Not Found":
        return 0.00

    deduction = flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'][filing_status]
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
    return -round(float(tax), 2)


def calc_fica_social_security(budget, month):
    taxable_income = get_row_value(budget, "Taxable Income", month)
    return -round(float(taxable_income * flask_app.config['FICA_SOCIALSECURITY_TAX_RATE']), 2)


def calc_fica_medicare(budget, month):
    taxable_income = get_row_value(budget, "Taxable Income", month)
    return -round(float(taxable_income * flask_app.config['FICA_MEDICARE_TAX_RATE']), 2)


def calc_sgli(budget, month):
    SGLI_RATES = flask_app.config['SGLI_RATES']
    coverage = get_row_value(budget, "SGLI Coverage", month)
    row = SGLI_RATES[SGLI_RATES['coverage'] == coverage]
    total = row.iloc[0]['total'] if not row.empty else 0
    return -abs(float(total))


def calc_state_taxes(budget, month):
    STATE_TAX_RATES = flask_app.config['STATE_TAX_RATES']
    HOME_OF_RECORDS = flask_app.config['HOME_OF_RECORDS']
    home_of_record = get_row_value(budget, "Home of Record", month)
    filing_status = get_row_value(budget, "State Filing Status", month)
    taxable_income = get_row_value(budget, "Taxable Income", month)
    military_housing_area = get_row_value(budget, "Military Housing Area", month)

    taxable_income = taxable_income * 12
    tax = 0.00

    # Get income_taxed policy for home of record
    hor_row = HOME_OF_RECORDS[HOME_OF_RECORDS['abbr'] == home_of_record]
    income_taxed = hor_row['income_taxed'].values[0].lower() if not hor_row.empty else "full"

    # Determine if member is living inside or outside their home state
    mha_state = military_housing_area[:2] if military_housing_area and len(military_housing_area) >= 2 else ""
    living_in_state = (mha_state == home_of_record)

    if income_taxed == "none":
        taxable_base = 0.0
    elif income_taxed == "exempt":
        # Only custom income rows (type 'c', sign 1)
        taxable_base = sum(
            row.get(month, 0.0)
            for row in budget
            if row.get('type') == 'c' and row.get('sign') == 1 and isinstance(row.get(month, 0.0), (int, float))
        )
    elif income_taxed == "outside":
        if living_in_state:
            # Tax all taxable income
            taxable_base = taxable_income
        else:
            # Only custom income rows (type 'c', sign 1)
            taxable_base = sum(
                row.get(month, 0.0)
                for row in budget
                if row.get('type') == 'c' and row.get('sign') == 1 and isinstance(row.get(month, 0.0), (int, float))
            )
    else:  # "full" or any other value
        taxable_base = taxable_income

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

        if taxable_base > lower_bracket:
            taxable_rate = min(taxable_base, upper_bracket) - lower_bracket
            tax += taxable_rate * rate

    tax = tax / 12
    return -round(float(tax), 2)


def calc_conus_cola(budget, month):
    return 0.0

def calc_oconus_cola(budget, month):
    return 0.0

def calc_oha(budget, month):
    return 0.0

def calc_miha_m(budget, month):
    return 0.0