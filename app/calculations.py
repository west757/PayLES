from decimal import Decimal

from app import flask_app
from app import utils


# =========================
# calculation functions
# =========================

def calculate_taxed_income(PAYDF_TEMPLATE, paydf, col_idx):
    combat_zone_row = paydf[paydf['header'] == 'Combat Zone']
    combat_zone = combat_zone_row.iloc[0, col_idx] if not combat_zone_row.empty else "No"
    is_combat_zone = str(combat_zone).strip().upper() == 'YES'
    taxable = Decimal(0)
    nontaxable = Decimal(0)

    for _, row in paydf.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if match.empty:
            continue

        row_type = match.iloc[0]['type']

        if row_type == 'E':
            value = row.iloc[col_idx]

            if value is None or value == '':
                value = Decimal(0)
            else:
                try:
                    value = Decimal(str(value))
                except Exception:
                    value = Decimal(0)

            tax_flag = match.iloc[0]['tax']

            if is_combat_zone:
                nontaxable += value
            else:
                if tax_flag:
                    taxable += value
                else:
                    nontaxable += value

    if is_combat_zone:
        taxable = Decimal(0)

    return round(taxable, 2), round(nontaxable, 2)


def calculate_total_taxes(PAYDF_TEMPLATE, paydf, col_idx):
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'D']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    total = Decimal(0)

    for _, row in rows.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if match.empty:
            continue

        tax_flag = match.iloc[0]['tax']

        if tax_flag:
            value = row.iloc[col_idx]
            value = Decimal(str(value))
            total += value

    return round(total, 2)


def calculate_gross_pay(PAYDF_TEMPLATE, paydf, col_idx):
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'E']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    total = Decimal(0)

    for _, row in rows.iterrows():
        value = row.iloc[col_idx]
        total += Decimal(value)

    return round(total, 2)


def calculate_net_pay(PAYDF_TEMPLATE, paydf, col_idx):
    deduction_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'D']['header'].tolist()
    allotment_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'A']['header'].tolist()
    row_headers = deduction_headers + allotment_headers

    rows = paydf[paydf['header'].isin(row_headers)]
    row_headers = paydf['header'].tolist()
    gross_pay_current = paydf.iloc[row_headers.index("Gross Pay"), col_idx]
    total = Decimal(0)

    for i, row in rows.iterrows():
        value = row.iloc[col_idx]

        if value is None or value == '':
            value = Decimal(0)
        else:
            try:
                value = Decimal(str(value))
            except Exception:
                value = Decimal(0)
        total += value

    total = gross_pay_current + total

    return round(total, 2)


def calculate_difference(paydf, col_idx):
    row_headers = paydf['header'].tolist()
    netpay_current = paydf.iloc[row_headers.index("Net Pay"), col_idx]
    netpay_prev = paydf.iloc[row_headers.index("Net Pay"), col_idx - 1]

    difference = Decimal(netpay_current) - Decimal(netpay_prev)
    return round(difference, 2)



# =========================
# calculate non-standard rows
# =========================

def calculate_base_pay(paydf, month):
    PAY_ACTIVE = flask_app.config['PAY_ACTIVE']
    row_headers = paydf['header'].tolist()
    grade = paydf.at[row_headers.index("Grade"), month]
    months_in_service = paydf.at[row_headers.index("Months in Service"), month]
    pay_active_headers = [int(col) for col in PAY_ACTIVE.columns[1:]]
    pay_active_row = PAY_ACTIVE[PAY_ACTIVE["grade"] == grade]

    col_idx = 0
    for i, mis in enumerate(pay_active_headers):
        if months_in_service < mis:
            break
        col_idx = i

    col_name = str(pay_active_headers[col_idx])
    value = pay_active_row[col_name].values[0]

    return round(Decimal(value), 2)


def calculate_bas(paydf, month):
    BAS_AMOUNT = flask_app.config['BAS_AMOUNT']
    row_headers = paydf['header'].tolist()
    grade = paydf.at[row_headers.index("Grade"), month]

    if str(grade).startswith("E"):
        bas_value = BAS_AMOUNT[1]
    else:
        bas_value = BAS_AMOUNT[0]

    return round(Decimal(bas_value), 2)


def calculate_bah(paydf, month):
    row_headers = paydf['header'].tolist()
    grade = paydf.at[row_headers.index("Grade"), month]
    military_housing_area = paydf.at[row_headers.index("Military Housing Area"), month]
    dependents = paydf.at[row_headers.index("Dependents"), month]

    if int(dependents) > 0:
        BAH_DF = flask_app.config['BAH_WITH_DEPENDENTS']
    else:
        BAH_DF = flask_app.config['BAH_WITHOUT_DEPENDENTS']

    if military_housing_area == "Not Found":
            return Decimal(0)

    bah_row = BAH_DF[BAH_DF["mha"] == military_housing_area]

    value = bah_row[grade].values[0]
    return round(Decimal(str(value)), 2)


def calculate_federal_taxes(paydf, month):
    STANDARD_DEDUCTIONS = flask_app.config['STANDARD_DEDUCTIONS']
    FEDERAL_TAX_RATE = flask_app.config['FEDERAL_TAX_RATE']
    row_headers = paydf['header'].tolist()
    filing_status = paydf.at[row_headers.index("Federal Filing Status"), month]
    taxable_income = paydf.at[row_headers.index("Taxable Income"), month]
    taxable_income = Decimal(taxable_income) * 12
    tax = Decimal(0)

    #subtract standard deduction from taxable income based on filing status
    if filing_status == "Single":
        taxable_income -= STANDARD_DEDUCTIONS[0]
    elif filing_status == "Married":
        taxable_income -= STANDARD_DEDUCTIONS[1]
    elif filing_status == "Head of Household":
        taxable_income -= STANDARD_DEDUCTIONS[2]
    
    taxable_income = max(taxable_income, 0)
    brackets = FEDERAL_TAX_RATE[FEDERAL_TAX_RATE['Status'].str.lower() == filing_status.lower()]
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


def calculate_fica_social_security(paydf, month):
    FICA_SOCIALSECURITY_TAX_RATE = flask_app.config['FICA_SOCIALSECURITY_TAX_RATE']
    row_headers = paydf['header'].tolist()
    taxable_income = paydf.at[row_headers.index("Taxable Income"), month]

    return round(-Decimal(taxable_income) * FICA_SOCIALSECURITY_TAX_RATE, 2)


def calculate_fica_medicare(paydf, month):
    FICA_MEDICARE_TAX_RATE = flask_app.config['FICA_MEDICARE_TAX_RATE']
    row_headers = paydf['header'].tolist()
    taxable_income = paydf.at[row_headers.index("Taxable Income"), month]

    return round(-Decimal(taxable_income) * FICA_MEDICARE_TAX_RATE, 2)


def calculate_sgli(paydf, row_idx, month, options):
    columns = paydf.columns.tolist()
    col_idx = columns.index(month)
    prev_value = paydf.at[row_idx, paydf.columns[col_idx - 1]]
    sgli_value, sgli_month = utils.get_option('SGLI', options)

    if month >= sgli_month:
        return -abs(Decimal(sgli_value))
    
    return -abs(Decimal(prev_value))


def calculate_state_taxes(paydf, month):
    STATE_TAX_RATE = flask_app.config['STATE_TAX_RATE']
    row_headers = paydf['header'].tolist()
    state = paydf.at[row_headers.index("Tax Residency State"), month]
    state_brackets = STATE_TAX_RATE[STATE_TAX_RATE['state'] == state]
    filing_status = paydf.at[row_headers.index("State Filing Status"), month]
    taxable_income = paydf.at[row_headers.index("Taxable Income"), month]
    taxable_income = Decimal(taxable_income) * 12
    tax = Decimal(0)

    if filing_status == "Single":
        brackets = state_brackets[['single_bracket', 'single_rate']].rename(columns={'single_bracket': 'bracket', 'single_rate': 'rate'})
    elif filing_status == "Married":
        brackets = state_brackets[['married_bracket', 'married_rate']].rename(columns={'married_bracket': 'bracket', 'married_rate': 'rate'})

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


def calculate_traditional_tsp(paydf, month):
    row_headers = paydf['header'].tolist()
    base_pay = paydf.at[row_headers.index("Base Pay"), month]
    tsp_rate = paydf.at[row_headers.index("Traditional TSP Rate"), month]

    value = Decimal(base_pay) * Decimal(tsp_rate) / Decimal(100)

    return -round(value, 2)


def calculate_roth_tsp(paydf, month):
    row_headers = paydf['header'].tolist()
    base_pay = paydf.at[row_headers.index("Base Pay"), month]
    tsp_rate = paydf.at[row_headers.index("Roth TSP Rate"), month]

    value = Decimal(base_pay) * Decimal(tsp_rate) / Decimal(100)

    return -round(value, 2)