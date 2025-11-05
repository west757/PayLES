from app import flask_app

from app.utils import (
    get_row_value,
)


def calc_income(pay, month):
    taxable = 0.0
    nontaxable = 0.0

    combat_zone = get_row_value(pay, "Combat Zone", month)

    income_rows = [row for row in pay if row.get('type') in ['ent', 'inc']]
    for row in income_rows:
        value = row[month]
        tax = row['tax']
        type = row['type']

        if (
            (type == 'ent' and combat_zone == "Yes") or
            (type == 'ent' and not tax and combat_zone == "No") or
            (type == 'inc' and not tax)
        ):
            nontaxable += value
        elif (
            (type == 'ent' and tax and combat_zone == "No") or
            (type == 'inc' and tax)
        ):
            taxable += value

    return round(taxable, 2), round(nontaxable, 2), round(taxable + nontaxable, 2)


def calc_expenses(pay, month):
    taxes = 0.0
    expenses = 0.0

    expense_rows = [row for row in pay if row.get('type') in ['ded', 'alt', 'exp']]
    for row in expense_rows:
        expenses += row[month]
        if row['tax']:
            taxes += row[month]

    return round(taxes, 2), round(expenses, 2)


def calc_difference(pay, month, prev_month):
    return round(get_row_value(pay, "Net Pay", month) - get_row_value(pay, "Net Pay", prev_month), 2)


def calc_ytds(pay, month, prev_month=None):
    ytd_income = get_row_value(pay, 'YTD Income', prev_month) if prev_month else 0
    ytd_expenses = get_row_value(pay, 'YTD Expenses', prev_month) if prev_month else 0
    ytd_net_pay = get_row_value(pay, 'YTD Net Pay', prev_month) if prev_month else 0

    income = get_row_value(pay, 'Total Income', month)
    expenses = get_row_value(pay, 'Total Expenses', month)
    net_pay = get_row_value(pay, 'Net Pay', month)

    ytd_income = income if month == "JAN" else ytd_income + income
    ytd_expenses = expenses if month == "JAN" else ytd_expenses + expenses
    ytd_net_pay = net_pay if month == "JAN" else ytd_net_pay + net_pay

    return round(ytd_income, 2), round(ytd_expenses, 2), round(ytd_net_pay, 2)



# =========================
# calculate special rows
# =========================

def calc_base_pay(pay, month):
    PAY_ACTIVE = flask_app.config['PAY_ACTIVE']
    grade = get_row_value(pay, "Grade", month)
    months_in_service = get_row_value(pay, "Months in Service", month)

    pay_row = PAY_ACTIVE[PAY_ACTIVE["grade"] == grade]
    month_cols = [int(col) * 12 for col in pay_row.columns[1:]]

    index = 0
    for i, m in enumerate(month_cols):
        if months_in_service < m:
            index = i - 1 if i > 0 else 0
            break

    selected_col = pay_row.columns[index + 1]

    base_pay = pay_row[selected_col].iloc[0]
    return round(float(base_pay), 2)


def calc_bas(pay, month):
    BAS_AMOUNT = flask_app.config['BAS_AMOUNT']
    grade = get_row_value(pay, "Grade", month)

    if str(grade).startswith("E"):
        bas = BAS_AMOUNT[0]
    else:
        bas = BAS_AMOUNT[1]

    return round(float(bas), 2)


def calc_bah(pay, month):
    grade = get_row_value(pay, "Grade", month)
    military_housing_area_code = get_row_value(pay, "Military Housing Area Code", month)
    dependents = get_row_value(pay, "Dependents", month)
    
    if military_housing_area_code == "Not Found":
        return 0.00

    BAH_DF = flask_app.config['BAH_WITH_DEPENDENTS'] if dependents > 0 else flask_app.config['BAH_WITHOUT_DEPENDENTS']

    bah_row = BAH_DF[BAH_DF["mha"] == military_housing_area_code]
    bah = bah_row[grade].values[0]
    return round(float(bah), 2)


def calc_federal_taxes(pay, month):
    FEDERAL_TAX_RATES = flask_app.config['FEDERAL_TAX_RATES']
    filing_status = get_row_value(pay, "Federal Filing Status", month)
    taxable_income = get_row_value(pay, "Taxable Income", month) * 12

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


def calc_fica_social_security(pay, month):
    taxable_income = get_row_value(pay, "Taxable Income", month)
    return -round(float(taxable_income * flask_app.config['FICA_SOCIALSECURITY_TAX_RATE']), 2)


def calc_fica_medicare(pay, month):
    taxable_income = get_row_value(pay, "Taxable Income", month)
    return -round(float(taxable_income * flask_app.config['FICA_MEDICARE_TAX_RATE']), 2)


def calc_sgli(pay, month):
    SGLI_RATES = flask_app.config['SGLI_RATES']
    coverage = get_row_value(pay, "SGLI Coverage", month)
    row = SGLI_RATES[SGLI_RATES['coverage'] == coverage]
    total = row.iloc[0]['total'] if not row.empty else 0
    return -abs(float(total))


def calc_state_taxes(pay, month):
    STATE_TAX_RATES = flask_app.config['STATE_TAX_RATES']
    HOME_OF_RECORDS = flask_app.config['HOME_OF_RECORDS']
    home_of_record = get_row_value(pay, "Home of Record", month)
    filing_status = get_row_value(pay, "State Filing Status", month)
    taxable_income = get_row_value(pay, "Taxable Income", month)
    military_housing_area = get_row_value(pay, "Military Housing Area", month)

    taxable_income = taxable_income * 12
    tax = 0.00

    # get income_taxed policy for home of record
    hor_row = HOME_OF_RECORDS[HOME_OF_RECORDS['abbr'] == home_of_record]
    income_taxed = hor_row['income_taxed'].values[0].lower() if not hor_row.empty else "full"

    # determine if member is living inside or outside their home state
    mha_state = military_housing_area[:2] if military_housing_area and len(military_housing_area) >= 2 else ""
    living_in_state = (mha_state == home_of_record)

    if income_taxed == "none":
        taxable_base = 0.0
    elif income_taxed == "exempt":
        # only custom income rows
        taxable_base = sum(
            row.get(month, 0.0)
            for row in pay
            if row.get('type') == 'inc' and isinstance(row.get(month, 0.0), (int, float))
        )
    elif income_taxed == "outside":
        if living_in_state:
            taxable_base = taxable_income
        else:
            # only custom income rows
            taxable_base = sum(
                row.get(month, 0.0)
                for row in pay
                if row.get('type') == 'inc' and isinstance(row.get(month, 0.0), (int, float))
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


def calc_conus_cola(pay, month):
    return 0.0

def calc_oconus_cola(pay, month):
    return 0.0

def calc_oha(pay, month):
    return 0.0

def calc_miha_m(pay, month):
    return 0.0