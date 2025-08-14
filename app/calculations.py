from decimal import Decimal

from app import flask_app
from app.utils import (
    sum_rows,
)

# =========================
# calculation functions
# =========================

def calculate_taxable_income(PAYDF_TEMPLATE, col_dict):
    combat_zone = col_dict["Combat Zone"]
    taxable = Decimal("0.00")
    nontaxable = Decimal("0.00")

    ent_rows = PAYDF_TEMPLATE[
        (PAYDF_TEMPLATE['sign'] == 1) & (PAYDF_TEMPLATE['header'].isin(col_dict))
    ]

    for _, row in ent_rows.iterrows():
        header = row['header']
        tax = row['tax']
        value = col_dict[header]

        if combat_zone == "Yes":
            nontaxable += value
        else:
            if tax:
                taxable += value
            else:
                nontaxable += value

    return round(taxable, 2), round(nontaxable, 2)


def calculate_total_taxes(PAYDF_TEMPLATE, col_dict):
    ded_alt_tax_rows = PAYDF_TEMPLATE[
        (PAYDF_TEMPLATE['sign'] == -1) & (PAYDF_TEMPLATE['tax']) & (PAYDF_TEMPLATE['header'].isin(col_dict))
    ]
    total = sum_rows(ded_alt_tax_rows, col_dict)
    return round(total, 2)


def calculate_gross_net_pay(PAYDF_TEMPLATE, col_dict):
    ent_rows = PAYDF_TEMPLATE[
        (PAYDF_TEMPLATE['sign'] == 1) & (PAYDF_TEMPLATE['header'].isin(col_dict))
    ]
    gross_pay = sum_rows(ent_rows, col_dict)

    ded_rows = PAYDF_TEMPLATE[
        (PAYDF_TEMPLATE['sign'] == -1) & (PAYDF_TEMPLATE['header'].isin(col_dict))
    ]
    net_pay = gross_pay + sum_rows(ded_rows, col_dict)

    return round(gross_pay, 2), round(net_pay, 2)


# =========================
# calculate non-standard rows
# =========================

def calculate_base_pay(col_dict, prev_col_dict=None):
    PAY_ACTIVE = flask_app.config['PAY_ACTIVE']
    grade = col_dict["Grade"]
    months_in_service = col_dict["Months in Service"]
    pay_active_headers = [int(col) for col in PAY_ACTIVE.columns[1:]]
    pay_active_row = PAY_ACTIVE[PAY_ACTIVE["grade"] == grade]

    col_idx = 0
    for i, mis in enumerate(pay_active_headers):
        if months_in_service < mis:
            break
        col_idx = i

    col_name = str(pay_active_headers[col_idx])
    value = pay_active_row[col_name].values[0] if not pay_active_row.empty else 0

    return round(Decimal(value), 2)


def calculate_bas(col_dict, prev_col_dict=None):
    BAS_AMOUNT = flask_app.config['BAS_AMOUNT']
    grade = col_dict["Grade"]

    if str(grade).startswith("E"):
        bas_value = BAS_AMOUNT[1]
    else:
        bas_value = BAS_AMOUNT[0]

    return round(Decimal(bas_value), 2)


def calculate_bah(col_dict, prev_col_dict=None):
    grade = col_dict["Grade"]
    military_housing_area = col_dict["Military Housing Area"]
    dependents = col_dict["Dependents"]

    if int(dependents) > 0:
        BAH_DF = flask_app.config['BAH_WITH_DEPENDENTS']
    else:
        BAH_DF = flask_app.config['BAH_WITHOUT_DEPENDENTS']

    if military_housing_area == "Not Found":
        return Decimal(0)

    bah_row = BAH_DF[BAH_DF["mha"] == military_housing_area]
    value = bah_row[grade].values[0]
    return round(Decimal(str(value)), 2)


def calculate_federal_taxes(col_dict, prev_col_dict=None):
    STANDARD_DEDUCTIONS = flask_app.config['STANDARD_DEDUCTIONS']
    FEDERAL_TAX_RATES = flask_app.config['FEDERAL_TAX_RATES']
    filing_status = col_dict["Federal Filing Status"]
    if not filing_status:
        return Decimal(0)
    taxable_income = col_dict["Taxable Income"]
    taxable_income = Decimal(taxable_income) * 12
    tax = Decimal(0)

    # subtract standard deduction from taxable income based on filing status
    if filing_status == "Single":
        taxable_income -= STANDARD_DEDUCTIONS[0]
    elif filing_status == "Married":
        taxable_income -= STANDARD_DEDUCTIONS[1]
    elif filing_status == "Head of Household":
        taxable_income -= STANDARD_DEDUCTIONS[2]

    taxable_income = max(taxable_income, 0)
    brackets = FEDERAL_TAX_RATES[FEDERAL_TAX_RATES['Status'].str.lower() == filing_status.lower()]
    brackets = brackets.sort_values(by='Bracket').reset_index(drop=True)

    for i in range(len(brackets)):
        lower_bracket = Decimal(str(brackets.at[i, 'Bracket']))
        rate = Decimal(str(brackets.at[i, 'Rate']))

        if i + 1 < len(brackets):
            upper_bracket = Decimal(str(brackets.at[i + 1, 'Bracket']))
        else:
            upper_bracket = Decimal('1e12')

        if taxable_income > lower_bracket:
            taxable_at_rate = min(taxable_income, upper_bracket) - lower_bracket
            tax += taxable_at_rate * rate

    tax = tax / 12
    return -round(tax, 2)


def calculate_fica_social_security(col_dict, prev_col_dict=None):
    FICA_SOCIALSECURITY_TAX_RATE = flask_app.config['FICA_SOCIALSECURITY_TAX_RATE']
    taxable_income = col_dict["Taxable Income"]
    return round(-Decimal(taxable_income) * FICA_SOCIALSECURITY_TAX_RATE, 2)


def calculate_fica_medicare(col_dict, prev_col_dict=None):
    FICA_MEDICARE_TAX_RATE = flask_app.config['FICA_MEDICARE_TAX_RATE']
    taxable_income = col_dict["Taxable Income"]
    return round(-Decimal(taxable_income) * FICA_MEDICARE_TAX_RATE, 2)



def calculate_sgli(col_dict, prev_col_dict=None):
    SGLI_RATES = flask_app.config['SGLI_RATES']
    coverage = col_dict["SGLI Coverage"]
    try:
        coverage = int(coverage)
    except Exception:
        coverage = 0

    # Find the row in SGLI_RATES where coverage matches
    row = SGLI_RATES[SGLI_RATES['coverage'] == coverage]
    if not row.empty:
        total = row.iloc[0]['total']
        try:
            total = Decimal(str(total))
        except Exception:
            total = Decimal(0)
    else:
        total = Decimal(0)

    return -abs(total)


def calculate_state_taxes(col_dict, prev_col_dict=None):
    STATE_TAX_RATES = flask_app.config['STATE_TAX_RATES']
    home_of_record = col_dict["Home of Record"]
    state_brackets = STATE_TAX_RATES[STATE_TAX_RATES['state'] == home_of_record]
    filing_status = col_dict["State Filing Status"]
    taxable_income = col_dict["Taxable Income"]
    taxable_income = Decimal(taxable_income) * 12
    tax = Decimal(0)

    if filing_status == "Single":
        brackets = state_brackets[['single_bracket', 'single_rate']].rename(columns={'single_bracket': 'bracket', 'single_rate': 'rate'})
    elif filing_status == "Married":
        brackets = state_brackets[['married_bracket', 'married_rate']].rename(columns={'married_bracket': 'bracket', 'married_rate': 'rate'})
    else:
        return Decimal(0)

    brackets = brackets.sort_values(by='bracket').reset_index(drop=True)
    
    for i in range(len(brackets)):
        lower_bracket = Decimal(str(brackets.at[i, 'bracket']))
        rate = Decimal(str(brackets.at[i, 'rate']))

        if i + 1 < len(brackets):
            upper_bracket = Decimal(str(brackets.at[i + 1, 'bracket']))
        else:
            upper_bracket = Decimal('1e12')

        if taxable_income > lower_bracket:
            taxable_rate = min(taxable_income, upper_bracket) - lower_bracket
            tax += taxable_rate * rate

    tax = tax / 12
    return -round(tax, 2)


def calculate_traditional_tsp(col_dict, prev_col_dict=None):
    base_pay = col_dict["Base Pay"]
    tsp_rate = col_dict["Traditional TSP Rate"]
    value = Decimal(base_pay) * Decimal(tsp_rate) / Decimal(100)
    return -round(value, 2)


def calculate_roth_tsp(col_dict, prev_col_dict=None):
    base_pay = col_dict["Base Pay"]
    tsp_rate = col_dict["Roth TSP Rate"]
    value = Decimal(base_pay) * Decimal(tsp_rate) / Decimal(100)
    return -round(value, 2)