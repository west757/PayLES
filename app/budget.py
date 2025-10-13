from datetime import datetime
import pandas as pd
import re

from app import flask_app
from app.calculations import (
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
from app.utils import (
    get_error_context,
    add_row,
    add_mv_pair,
    get_row_value,
)


def get_budget_variables(les_text):
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


def add_budget_variables(budget, month, variables):
    for var, val in variables.items():
        row = next((row for row in budget if row.get('header') == var), None)
        if row:
            add_mv_pair(budget, row['header'], month, val)
        else:
            raise Exception(f"Variable '{var}' not found in PARAMS_TEMPLATE")
        
    budget = set_variable_longs(budget, month)
    return budget


def set_variable_longs(budget, month):
    branch = get_row_value(budget, 'Branch', month)
    branch_long = flask_app.config['BRANCHES'].get(branch, "Not Found")
    add_mv_pair(budget, 'Branch Long', month, branch_long)

    component = get_row_value(budget, 'Component', month)
    component_long = flask_app.config['COMPONENTS'].get(component, "Not Found")
    add_mv_pair(budget, 'Component Long', month, component_long)

    GRADES_RANKS = flask_app.config['GRADES_RANKS']
    grade = get_row_value(budget, 'Grade', month)
    branch = get_row_value(budget, 'Branch', month)
    rank_row = GRADES_RANKS[GRADES_RANKS['grade'] == grade]
    rank_long = rank_row.iloc[0][branch]
    add_mv_pair(budget, 'Rank Long', month, rank_long)

    zip_code = get_row_value(budget, 'Zip Code', month)
    mha_code, mha_long = get_military_housing_area(zip_code)
    add_mv_pair(budget, 'Military Housing Area Code', month, mha_code)
    add_mv_pair(budget, 'Military Housing Area Long', month, mha_long)

    oconus_locality_code = get_row_value(budget, 'OCONUS Locality Code', month)
    oconus_locality_code_long = ""
    add_mv_pair(budget, 'OCONUS Locality Code Long', month, oconus_locality_code_long)

    home_of_record = get_row_value(budget, 'Home of Record', month)
    longname, _ = get_home_of_record(home_of_record)
    add_mv_pair(budget, 'Home of Record Long', month, longname)

    return budget


def get_military_housing_area(zip_code):
    MHA_ZIP_CODES = flask_app.config['MHA_ZIP_CODES']

    if zip_code in ("00000", "", "Not Found"):
        return "Not Found", "Not Found"

    try:
        for _, row in MHA_ZIP_CODES.iterrows():
            for zip_val in row[2:]:

                if pd.isna(zip_val):
                    continue

                zip_str = str(zip_val).strip()
                if not zip_str:
                    continue

                if '.' in zip_str:
                    zip_str = zip_str.split('.')[0]
                    
                zip_str = zip_str.zfill(5)
                if zip_str == str(zip_code).strip().zfill(5):
                    return row['mha'], row['mha_name']
        return "Not Found", "Not Found"
    except Exception:
        return "Not Found", "Not Found"


def get_home_of_record(home_of_record):
    HOME_OF_RECORDS = flask_app.config['HOME_OF_RECORDS']

    if not home_of_record or home_of_record == "Not Found":
        return "Not Found", "Not Found"

    home_of_record = str(home_of_record).strip()
    if len(home_of_record) == 2:
        row = HOME_OF_RECORDS[HOME_OF_RECORDS['abbr'] == home_of_record]
        return row.iloc[0]['longname'], home_of_record
    else:
        row = HOME_OF_RECORDS[HOME_OF_RECORDS['longname'] == home_of_record]
        return home_of_record, row.iloc[0]['abbr']


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


def parse_pay_string(pay_string, pay_template):
    results = {}

    # build a regex pattern that matches all LESNAMEs as whole words, followed by a number
    # sort by length descending to match longer names first
    lesnames = [row['lesname'] for _, row in pay_template.iterrows() if isinstance(row['lesname'], str) and row['lesname'].strip()]
    lesnames = sorted(lesnames, key=len, reverse=True)
    # escape and join for regex alternation
    pattern = r'(' + '|'.join(re.escape(lesname) for lesname in lesnames) + r')\s+(-?\d+(?:\.\d+)?)'

    # find all matches
    for match in re.findall(pattern, pay_string):
        lesname, value_str = match
        try:
            value = float(value_str.replace(",", ""))
            results[lesname] = round(value, 2)
        except Exception:
            continue

    return results


def add_calc_pay(budget, month, sign):
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


def update_variables(budget, month, prev_month, cell=None):
    variable_rows = [row for row in budget if row.get('type') == 'v']
    for row in variable_rows:
        header = row['header']
        prev_value = row.get(prev_month)

        if header == "Year":
            row[month] = prev_value + 1 if month == "JAN" else prev_value
            continue
        elif header == "Months in Service":
            row[month] = prev_value + 1
            continue

        if cell is not None and header == cell.get('header'):
            if cell.get('repeat') or cell.get('month') == month:
                row[month] = cell.get('value')
            elif month in row:
                pass
            else:
                row[month] = prev_value
        elif month in row:
            pass
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

        if cell is not None and header == cell.get('header'):
            if cell.get('repeat') or cell.get('month') == month:
                row[month] = cell.get('value')
            elif month in row:
                pass
            else:
                row[month] = prev_value
        elif month in row:
            pass
        else:
            row[month] = prev_value

    return budget


def compare_budgets(budget_les, budget_calc, month):
    calc_lookup = {row['header']: row for row in budget_calc if row.get('type') in ('e', 'd')}
    discrepancies = []

    for row in budget_les:
        if row.get('type') in ('e', 'd') and row['header'] in calc_lookup:
            les_value = row.get(month)
            calc_value = calc_lookup[row['header']].get(month)

            if les_value != calc_value:
                discrepancies.append({
                    'header': row['header'],
                    'les_value': les_value,
                    'calc_value': calc_value
                })

    return discrepancies