from bisect import bisect_right
from decimal import Decimal

from app import flask_app


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
    headers = ded_alt_tax_rows['header'].tolist()
    total = sum([col_dict[h] for h in headers])
    return round(total, 2)


def calculate_gross_net_pay(PAYDF_TEMPLATE, col_dict):
    ent_rows = PAYDF_TEMPLATE[
        (PAYDF_TEMPLATE['sign'] == 1) & (PAYDF_TEMPLATE['header'].isin(col_dict))
    ]
    ent_headers = ent_rows['header'].tolist()
    gross_pay = sum([col_dict[h] for h in ent_headers])

    ded_rows = PAYDF_TEMPLATE[
        (PAYDF_TEMPLATE['sign'] == -1) & (PAYDF_TEMPLATE['header'].isin(col_dict))
    ]
    ded_headers = ded_rows['header'].tolist()
    net_pay = gross_pay + sum([col_dict[h] for h in ded_headers])

    return round(gross_pay, 2), round(net_pay, 2)



# =========================
# calculate special rows
# =========================

def calculate_base_pay(col_dict):
    PAY_ACTIVE = flask_app.config['PAY_ACTIVE']
    grade = col_dict["Grade"]
    months_in_service = int(col_dict["Months in Service"])
    pay_row = PAY_ACTIVE[PAY_ACTIVE["grade"] == grade]

    month_cols = []
    for col in pay_row.columns:
        if col != "grade":
            month_cols.append(int(col))
    month_cols.sort()

    idx = bisect_right(month_cols, months_in_service) - 1
    selected_month_num = str(month_cols[idx])

    pay = pay_row[selected_month_num].iloc[0]
    return round(Decimal(pay), 2)


def calculate_bas(col_dict):
    BAS_AMOUNT = flask_app.config['BAS_AMOUNT']
    grade = col_dict["Grade"]

    if grade.startswith("E"):
        bas = BAS_AMOUNT[0]
    else:
        bas = BAS_AMOUNT[1]

    return round(Decimal(bas), 2)


def calculate_bah(col_dict):
    grade = col_dict["Grade"]
    military_housing_area = col_dict["Military Housing Area"]
    dependents = col_dict["Dependents"]

    if military_housing_area == "Not Found":
        return Decimal("0.00")

    if dependents > 0:
        BAH_DF = flask_app.config['BAH_WITH_DEPENDENTS']
    else:
        BAH_DF = flask_app.config['BAH_WITHOUT_DEPENDENTS']

    bah_row = BAH_DF[BAH_DF["mha"] == military_housing_area]
    bah = bah_row[grade].values[0]
    return round(Decimal(str(bah)), 2)


def calculate_federal_taxes(col_dict):
    TAX_FILING_TYPES_DEDUCTIONS = flask_app.config['TAX_FILING_TYPES_DEDUCTIONS']
    FEDERAL_TAX_RATES = flask_app.config['FEDERAL_TAX_RATES']
    filing_status = col_dict["Federal Filing Status"]
    taxable_income = col_dict["Taxable Income"] * 12
    tax = 0

    if filing_status == "Not Found":
        return Decimal("0.00")

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

        if taxable_income > Decimal(str(lower_bracket)):
            taxable_at_rate = min(taxable_income, upper_bracket) - lower_bracket
            tax += taxable_at_rate * rate

    tax = tax / 12
    return -round(Decimal(tax), 2)


def calculate_fica_social_security(col_dict):
    FICA_SOCIALSECURITY_TAX_RATE = flask_app.config['FICA_SOCIALSECURITY_TAX_RATE']
    taxable_income = col_dict["Taxable Income"]
    return round(-Decimal(taxable_income) * FICA_SOCIALSECURITY_TAX_RATE, 2)


def calculate_fica_medicare(col_dict):
    FICA_MEDICARE_TAX_RATE = flask_app.config['FICA_MEDICARE_TAX_RATE']
    taxable_income = col_dict["Taxable Income"]
    return round(-Decimal(taxable_income) * FICA_MEDICARE_TAX_RATE, 2)


def calculate_sgli(col_dict):
    SGLI_RATES = flask_app.config['SGLI_RATES']
    coverage = str(col_dict["SGLI Coverage"])
    row = SGLI_RATES[SGLI_RATES['coverage'] == coverage]
    total = row.iloc[0]['total']
    return -abs(total)


def calculate_state_taxes(col_dict):
    STATE_TAX_RATES = flask_app.config['STATE_TAX_RATES']
    home_of_record = col_dict["Home of Record"]
    state_brackets = STATE_TAX_RATES[STATE_TAX_RATES['state'] == home_of_record]
    filing_status = col_dict["State Filing Status"]
    taxable_income = col_dict["Taxable Income"]
    taxable_income = Decimal(taxable_income) * 12
    tax = Decimal("0.00")

    if filing_status == "Single":
        brackets = state_brackets[['single_bracket', 'single_rate']].rename(columns={'single_bracket': 'bracket', 'single_rate': 'rate'})
    elif filing_status == "Married":
        brackets = state_brackets[['married_bracket', 'married_rate']].rename(columns={'married_bracket': 'bracket', 'married_rate': 'rate'})
    else:
        return Decimal("0.00")

    brackets = brackets.sort_values(by='bracket').reset_index(drop=True)
    
    for i in range(len(brackets)):
        lower_bracket = brackets.at[i, 'bracket']
        rate = brackets.at[i, 'rate']

        if i + 1 < len(brackets):
            upper_bracket = brackets.at[i + 1, 'bracket']
        else:
            upper_bracket = 10**7

        if taxable_income > Decimal(str(lower_bracket)):
            taxable_rate = min(taxable_income, upper_bracket) - lower_bracket
            tax += taxable_rate * rate

    tax = tax / 12
    return -round(Decimal(tax), 2)



#need to add in max tsp yearly limit
def calculate_trad_roth_tsp(PAYDF_TEMPLATE, col_dict):
    VARIABLE_TEMPLATE = flask_app.config['VARIABLE_TEMPLATE']
    trad_total = Decimal("0.00")
    roth_total = Decimal("0.00")

    # Get all TSP rate rows from VARIABLE_TEMPLATE
    tsp_rows = VARIABLE_TEMPLATE[VARIABLE_TEMPLATE['type'] == 't']

    for _, tsp_row in tsp_rows.iterrows():
        tsp_var = tsp_row['varname']
        modal = tsp_row['modal']
        rate = Decimal(str(col_dict.get(tsp_var, 0)))

        if rate > 0:
            # Find all entitlement rows in PAYDF_TEMPLATE with matching modal
            rows = PAYDF_TEMPLATE[(PAYDF_TEMPLATE['sign'] == 1) & (PAYDF_TEMPLATE['modal'] == modal)]
            headers = rows['header'].tolist()

            total = sum(Decimal(col_dict.get(h, 0)) for h in headers)
            value = total * rate / Decimal(100)

            if tsp_var.lower().startswith("trad"):
                trad_total += value
            elif tsp_var.lower().startswith("roth"):
                roth_total += value

    return -round(trad_total, 2), -round(roth_total, 2)