from app import flask_app


# =========================
# calculation functions
# =========================

def calculate_income(budget, working_month):
    taxable = 0.00
    nontaxable = 0.00

    combat_zone_row = next((row for row in budget if row['header'] == "Combat Zone"), None)
    combat_zone = combat_zone_row[working_month] if combat_zone_row and working_month in combat_zone_row else "No"

    for row in budget:
        if row.get('sign') == 1 and working_month in row:
            value = row[working_month]
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

    for row in budget:
        if row['header'] == 'Taxable Income':
            row[working_month] = taxable
        elif row['header'] == 'Non-Taxable Income':
            row[working_month] = nontaxable
        elif row['header'] == 'Total Income':
            row[working_month] = income

    return budget


def calculate_tax_exp_net(budget, working_month):
    taxes = 0.00
    expenses = 0.00

    for row in budget:
        if working_month in row:
            if row.get('sign') == -1:
                expenses += row[working_month]
                if row.get('tax', False):
                    taxes += row[working_month]

    income_row = next((r for r in budget if r.get('header') == 'Total Income'), None)
    income = income_row[working_month]

    net_pay = income + expenses
    expenses = round(expenses, 2)
    taxes = round(taxes, 2)
    net_pay = round(net_pay, 2)

    for row in budget:
        if row['header'] == 'Taxes':
            row[working_month] = taxes
        elif row['header'] == 'Total Expenses':
            row[working_month] = expenses
        elif row['header'] == 'Net Pay':
            row[working_month] = net_pay

    return budget


def calculate_difference(budget, prev_month, working_month):
    net_pay_row = next((r for r in budget if r['header'] == "Net Pay"), None)

    for row in budget:
        if row['header'] == 'Difference':
            row[working_month] = round(net_pay_row[working_month] - net_pay_row[prev_month], 2)

    return budget


def calculate_ytd_rows(budget, prev_month, working_month):
    ytd_ent_row = next((r for r in budget if r['header'] == 'YTD Income'), None)
    ytd_ded_row = next((r for r in budget if r['header'] == 'YTD Expenses'), None)
    ytd_net_row = next((r for r in budget if r['header'] == 'YTD Net Pay'), None)

    income_row = next((r for r in budget if r['header'] == 'Total Income'), None)
    income = income_row[working_month]

    expenses_row = next((r for r in budget if r['header'] == 'Total Expenses'), None)
    expenses = expenses_row[working_month]

    net_pay_row = next((r for r in budget if r['header'] == 'Net Pay'), None)
    net_pay = net_pay_row[working_month]


    if working_month == "JAN":
        ytd_ent_row[working_month] = income
        ytd_ded_row[working_month] = expenses
        ytd_net_row[working_month] = net_pay
    else:
        ytd_ent_row[working_month] = round(ytd_ent_row[prev_month] + income, 2)
        ytd_ded_row[working_month] = round(ytd_ded_row[prev_month] + expenses, 2)
        ytd_net_row[working_month] = round(ytd_net_row[prev_month] + net_pay, 2)

    return budget



# =========================
# calculate special rows
# =========================

def calculate_base_pay(budget, month):
    PAY_ACTIVE = flask_app.config['PAY_ACTIVE']
    grade_row = next((row for row in budget if row['header'] == "Grade"), None)
    months_row = next((row for row in budget if row['header'] == "Months in Service"), None)
    grade = grade_row.get(month) if grade_row else "Not Found"
    months_in_service = int(months_row[month])

    pay_row = PAY_ACTIVE[PAY_ACTIVE["grade"] == grade]
    month_cols = [int(col) * 12 for col in pay_row.columns[1:]]

    idx = 0
    for i, m in enumerate(month_cols):
        if months_in_service < m:
            idx = i - 1 if i > 0 else 0
            break

    selected_col = pay_row.columns[idx + 1]

    base_pay = pay_row[selected_col].iloc[0]
    return round(base_pay, 2)


def calculate_bas(budget, month):
    BAS_AMOUNT = flask_app.config['BAS_AMOUNT']
    grade_row = next((row for row in budget if row['header'] == "Grade"), None)
    grade = grade_row.get(month) if grade_row else "Not Found"

    if str(grade).startswith("E"):
        bas = BAS_AMOUNT[0]
    else:
        bas = BAS_AMOUNT[1]

    return round(bas, 2)


def calculate_bah(budget, month):
    grade_row = next((row for row in budget if row['header'] == "Grade"), None)
    mha_row = next((row for row in budget if row['header'] == "Military Housing Area"), None)
    dependents_row = next((row for row in budget if row['header'] == "Dependents"), None)

    grade = grade_row[month]
    military_housing_area = mha_row[month]
    dependents = dependents_row[month]
    
    if military_housing_area == "Not Found":
        return 0.00

    if dependents > 0:
        BAH_DF = flask_app.config['BAH_WITH_DEPENDENTS']
    else:
        BAH_DF = flask_app.config['BAH_WITHOUT_DEPENDENTS']

    bah_row = BAH_DF[BAH_DF["mha"] == military_housing_area]
    bah = bah_row[grade].values[0]
    return round(bah, 2)


def calculate_federal_taxes(budget, month):
    FEDERAL_TAX_RATES = flask_app.config['FEDERAL_TAX_RATES']
    filing_status_row = next((row for row in budget if row['header'] == "Federal Filing Status"), None)
    taxable_income_row = next((row for row in budget if row['header'] == "Taxable Income"), None)

    filing_status = filing_status_row.get(month) if filing_status_row else "Not Found"
    taxable_income = taxable_income_row.get(month, 0.00) if taxable_income_row else 0.00
    taxable_income = taxable_income * 12
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
    return -round(tax, 2)


def calculate_fica_social_security(budget, month):
    taxable_income_row = next((row for row in budget if row['header'] == "Taxable Income"), None)
    taxable_income = taxable_income_row.get(month, 0.00) if taxable_income_row else 0.00
    return round(-taxable_income * flask_app.config['FICA_SOCIALSECURITY_TAX_RATE'], 2)


def calculate_fica_medicare(budget, month):
    taxable_income_row = next((row for row in budget if row['header'] == "Taxable Income"), None)
    taxable_income = taxable_income_row.get(month, 0.00) if taxable_income_row else 0.00
    return round(-taxable_income * flask_app.config['FICA_MEDICARE_TAX_RATE'], 2)


def calculate_sgli(budget, month):
    SGLI_RATES = flask_app.config['SGLI_RATES']
    coverage_row = next((row for row in budget if row['header'] == "SGLI Coverage"), None)
    coverage = str(coverage_row.get(month)) if coverage_row and month in coverage_row else "0"
    row = SGLI_RATES[SGLI_RATES['coverage'] == coverage]
    total = row.iloc[0]['total'] if not row.empty else 0
    return -abs(total)


def calculate_state_taxes(budget, month):
    STATE_TAX_RATES = flask_app.config['STATE_TAX_RATES']
    HOME_OF_RECORDS = flask_app.config['HOME_OF_RECORDS']
    home_of_record_row = next((row for row in budget if row['header'] == "Home of Record"), None)
    filing_status_row = next((row for row in budget if row['header'] == "State Filing Status"), None)
    taxable_income_row = next((row for row in budget if row['header'] == "Taxable Income"), None)
    mha_row = next((row for row in budget if row['header'] == "Military Housing Area"), None)

    home_of_record = home_of_record_row.get(month)
    filing_status = filing_status_row.get(month)
    taxable_income = taxable_income_row.get(month, 0.00)
    taxable_income = taxable_income * 12
    tax = 0.00

    # Get income_taxed policy for home of record
    hor_row = HOME_OF_RECORDS[HOME_OF_RECORDS['abbr'] == home_of_record]
    income_taxed = hor_row['income_taxed'].values[0].lower() if not hor_row.empty else "full"

    # Determine if member is living inside or outside their home state
    mha_code = mha_row.get(month)
    mha_state = mha_code[:2] if mha_code and len(mha_code) >= 2 else ""
    living_in_state = (mha_state == home_of_record)

    # Calculate taxable base according to policy
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
    return -round(tax, 2)
