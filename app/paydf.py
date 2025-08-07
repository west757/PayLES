from flask import session
from datetime import datetime
import pandas as pd

from app import flask_app
from app import utils
from app.calculations import (
    calculate_bah,
    calculate_base_pay,
    calculate_bas,
    calculate_federal_taxes,
    calculate_fica_social_security,
    calculate_fica_medicare,
    calculate_sgli,
    calculate_state_taxes,
    calculate_traditional_tsp,
    calculate_roth_tsp,
    calculate_taxed_income,
    calculate_total_taxes,
    calculate_gross_pay,
    calculate_net_pay,
    calculate_difference,
)


# =========================
# build paydf
# =========================

def build_paydf(les_text):
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    DEFAULT_MONTHS_DISPLAY = flask_app.config['DEFAULT_MONTHS_DISPLAY']
    initial_month = les_text[8][3]

    remove_custom_template_rows(PAYDF_TEMPLATE)

    paydf = pd.DataFrame(columns=["header", initial_month])
    paydf = add_variables(PAYDF_TEMPLATE, paydf, les_text)
    paydf = add_entitlements(PAYDF_TEMPLATE, paydf, les_text)
    paydf = add_deductions(PAYDF_TEMPLATE, paydf, les_text)
    paydf = add_allotments(PAYDF_TEMPLATE, paydf, les_text)
    paydf = add_calculations(PAYDF_TEMPLATE, paydf)

    #convert paydf to JSON and store in session for use in update_paydf
    session['paydf_json'] = paydf.to_json()

    options = build_options(PAYDF_TEMPLATE, paydf=paydf)
    paydf = expand_paydf(PAYDF_TEMPLATE, paydf, options, DEFAULT_MONTHS_DISPLAY)

    col_headers = paydf.columns.tolist()
    row_headers = paydf['header'].tolist()

    return paydf, col_headers, row_headers, options, DEFAULT_MONTHS_DISPLAY


def add_variables(PAYDF_TEMPLATE, paydf, les_text):
    MHA_ZIP_CODES = flask_app.config['MHA_ZIP_CODES']
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'V']

    for _, row in var_rows.iterrows():
        header = row['header']
        dtype = row['dtype']
        value = row['default']

        if header == 'Year':
            value = int('20' + les_text[8][4])
        elif header == 'Grade':
            value = str(les_text[2][1])
        elif header == 'Months in Service':
            paydate = datetime.strptime(les_text[3][2], '%y%m%d')
            lesdate = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
            value = int(utils.months_in_service(lesdate, paydate))
        elif header == 'Zip Code':
            if les_text[48][2] != "00000":
                value = les_text[48][2]
        elif header == 'Military Housing Area':
            value = utils.calculate_mha(MHA_ZIP_CODES,les_text[48][2])
        elif header == 'Tax Residency State':
            if les_text[39][1] != "98":
                value = les_text[39][1]
        elif header == 'Federal Filing Status':
            status = les_text[24][1]
            if status == "S":
                value = "Single"
            elif status == "M":
                value = "Married"
            elif status == "H":
                value = "Head of Household"
        elif header == 'State Filing Status':
            status = les_text[42][1]
            if status == "S":
                value = "Single"
            elif status == "M":
                value = "Married"
        elif header == 'Dependents':
            value = int(les_text[53][1])
        elif header == 'Combat Zone':
            value = "No"
        elif header == 'Traditional TSP Rate':
            ttsp_fields = [int(les_text[60][3]), int(les_text[62][3]), int(les_text[64][3]), int(les_text[66][3])]
            value = next((val for val in ttsp_fields if val > 0), 0)
        elif header == 'Roth TSP Rate':
            rtsp_fields = [int(les_text[69][3]), int(les_text[71][3]), int(les_text[73][3]), int(les_text[75][3])]
            value = next((val for val in rtsp_fields if val > 0), 0)

        value = utils.cast_dtype(value, dtype)
        paydf.loc[len(paydf)] = [header, value]

    return paydf


def add_entitlements(PAYDF_TEMPLATE, paydf, les_text):
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'E']
    section = les_text[9]

    for _, row in var_rows.iterrows():
        value = utils.parse_eda_sections(section, row)
        if value is not None:
            paydf.loc[len(paydf)] = [row['header'], value]
    return paydf


def add_deductions(PAYDF_TEMPLATE, paydf, les_text):
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'D']
    section = les_text[10]

    for _, row in var_rows.iterrows():
        value = utils.parse_eda_sections(section, row)
        if value is not None:
            paydf.loc[len(paydf)] = [row['header'], -value]
    return paydf


def add_allotments(PAYDF_TEMPLATE, paydf, les_text):
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'A']
    section = les_text[11]
    
    for _, row in var_rows.iterrows():
        value = utils.parse_eda_sections(section, row)
        if value is not None:
            paydf.loc[len(paydf)] = [row['header'], -value]
    return paydf


def add_calculations(PAYDF_TEMPLATE, paydf):
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'C']

    taxable, nontaxable = calculate_taxed_income(PAYDF_TEMPLATE, paydf, 1)

    for _, row in var_rows.iterrows():
        header = row['header']
        value = 0

        if header == "Taxable Income":
            value = taxable
        elif header == "Non-Taxable Income":
            value = nontaxable
        elif header == "Total Taxes":
            value = calculate_total_taxes(PAYDF_TEMPLATE, paydf, 1)
        elif header == "Gross Pay":
            value = calculate_gross_pay(PAYDF_TEMPLATE, paydf, 1)
        elif header == "Net Pay":
            value = calculate_net_pay(PAYDF_TEMPLATE, paydf, 1)
        elif header == "Difference":
            value = 0

        value = utils.cast_dtype(value, row['dtype'])
        paydf.loc[len(paydf)] = [header, value]
    return paydf



# =========================
# build options
# =========================

def build_options(PAYDF_TEMPLATE, paydf, form=None):
    MHA_ZIP_CODES = flask_app.config['MHA_ZIP_CODES']
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    options = []

    def add_option(header, varname):
        row_idx = paydf[paydf['header'] == header].index[0]

        if form:
            value = form.get(f"{varname}_f", None)
            month = form.get(f"{varname}_m", "")

            if header == "Zip Code" and value not in [None, ""]:
                value = utils.validate_zip_code(MHA_ZIP_CODES, value)

            #calcualtes checkbox values as "on" or None
            if value == "on":
                first_month_col = paydf.columns[1]
                value = paydf.at[row_idx, first_month_col]
            elif value is None:
                value = 0
            elif value == "":
                first_month_col = paydf.columns[1]
                value = paydf.at[row_idx, first_month_col]

        else:
            first_month_col = paydf.columns[1]
            value = paydf.at[row_idx, first_month_col]
            first_month_idx = MONTHS_SHORT.index(first_month_col)
            month = MONTHS_SHORT[(first_month_idx + 1) % 12]

        options.append([header, value, month])

    for _, row in PAYDF_TEMPLATE.iterrows():
        if not row.get('option', False):
            continue

        header = row['header']
        varname = row['varname']
        required = bool(row['required'])

        if required:
            add_option(header, varname)
        else:
            if header in paydf['header'].values:
                add_option(header, varname)

    return options



# =========================
# expand paydf
# =========================

def expand_paydf(PAYDF_TEMPLATE, paydf, options, months_display, custom_rows=None):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    initial_month = paydf.columns[1]
    month_idx = MONTHS_SHORT.index(initial_month)

    for i in range(1, months_display):
        month_idx = (month_idx + 1) % 12
        new_month = MONTHS_SHORT[month_idx]
        defaults = []

        for _, row in paydf.iterrows():
            header = row['header']
            match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

            if not match.empty:
                defaults.append(utils.cast_dtype(match.iloc[0]['default'], match.iloc[0]['dtype']))
            else:
                defaults.append(0)

        paydf[new_month] = defaults
        paydf = update_variables(PAYDF_TEMPLATE, paydf, new_month, options)
        paydf = update_entitlements(PAYDF_TEMPLATE, paydf, new_month, options, custom_rows=custom_rows)
        paydf = update_calculations(PAYDF_TEMPLATE, paydf, new_month, only_taxable=True)
        paydf = update_deductions(PAYDF_TEMPLATE, paydf, new_month, options, custom_rows=custom_rows)
        paydf = update_allotments(PAYDF_TEMPLATE, paydf, new_month, options)
        paydf = update_calculations(PAYDF_TEMPLATE, paydf, new_month, only_taxable=False)

    return paydf


def update_variables(PAYDF_TEMPLATE, paydf, month, options):
    MHA_ZIP_CODES = flask_app.config['MHA_ZIP_CODES']
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'V']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    option_headers = set(opt[0] for opt in options)

    for row_idx, row in rows.iterrows():
        header = row['header']
        columns = paydf.columns.tolist()
        col_idx = columns.index(month)
        prev_month = paydf.columns[col_idx - 1]
        prev_value = paydf.at[row_idx, prev_month]

        if header in option_headers:
            future_value, future_month = utils.get_option(header, options)

            if future_month in columns:
                future_col_idx = columns.index(future_month)
                current_col_idx = columns.index(month)

                if current_col_idx >= future_col_idx:
                    paydf.at[row_idx, month] = future_value
                else:
                    paydf.at[row_idx, month] = prev_value
            else:
                paydf.at[row_idx, month] = prev_value
            continue

        elif header == 'Year':
            if MONTHS_SHORT.index(month) == 0 and MONTHS_SHORT.index(prev_month) == 11:
                paydf.at[row_idx, month] = prev_value + 1
            else:
                paydf.at[row_idx, month] = prev_value
            continue

        elif header == 'Months in Service':
            paydf.at[row_idx, month] = prev_value + 1
            continue

        elif header == 'Military Housing Area':
            zip_code = paydf.at[row_idx - 1, month]
            paydf.at[row_idx, month] = utils.calculate_mha(MHA_ZIP_CODES, zip_code)
            continue

    return paydf


def update_entitlements(PAYDF_TEMPLATE, paydf, month, options, custom_rows=None):
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'E']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    columns = paydf.columns.tolist()

    for row_idx, row in rows.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if utils.update_eda_rows(paydf, row_idx, header, match, month, columns, options, custom_rows):
            continue
        elif header == 'Base Pay':
            paydf.at[row_idx, month] = calculate_base_pay(paydf, month)
        elif header == 'BAS':
            paydf.at[row_idx, month] = calculate_bas(paydf, month)
        elif header == 'BAH':
            paydf.at[row_idx, month] = calculate_bah(paydf, month)

    return paydf


def update_deductions(PAYDF_TEMPLATE, paydf, month, options, custom_rows=None):
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'D']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    columns = paydf.columns.tolist()

    for row_idx, row in rows.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if utils.update_eda_rows(paydf, row_idx, header, match, month, columns, options, custom_rows):
            continue
        elif header == 'Federal Taxes':
            paydf.at[row_idx, month] = calculate_federal_taxes(paydf, month)
        elif header == 'FICA - Social Security':
            paydf.at[row_idx, month] = calculate_fica_social_security(paydf, month)
        elif header == 'FICA - Medicare':
            paydf.at[row_idx, month] = calculate_fica_medicare(paydf, month)
        elif header == 'SGLI':
            paydf.at[row_idx, month] = calculate_sgli(paydf, row_idx, month, options)
        elif header == 'State Taxes':
            paydf.at[row_idx, month] = calculate_state_taxes(paydf, month)
        elif header == 'Traditional TSP':
            paydf.at[row_idx, month] = calculate_traditional_tsp(paydf, month)
        elif header == 'Roth TSP':
            paydf.at[row_idx, month] = calculate_roth_tsp(paydf, month)

    return paydf


def update_allotments(PAYDF_TEMPLATE, paydf, month, options, custom_rows=None):
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'A']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    columns = paydf.columns.tolist()

    for row_idx, row in rows.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if utils.update_eda_rows(paydf, row_idx, header, match, month, columns, options, custom_rows):
            continue

    return paydf


def update_calculations(PAYDF_TEMPLATE, paydf, month, only_taxable):
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'C']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    columns = paydf.columns.tolist()
    col_idx = columns.index(month)

    for row_idx, row in rows.iterrows():
        header = row['header']

        if only_taxable:
            taxable, nontaxable = calculate_taxed_income(PAYDF_TEMPLATE, paydf, col_idx)
            if header == "Taxable Income":
                paydf.at[row_idx, month] = taxable
            elif header == "Non-Taxable Income":
                paydf.at[row_idx, month] = nontaxable
        else:
            if header == "Total Taxes":
                paydf.at[row_idx, month] = calculate_total_taxes(PAYDF_TEMPLATE, paydf, col_idx)
            elif header == "Gross Pay":
                paydf.at[row_idx, month] = calculate_gross_pay(PAYDF_TEMPLATE, paydf, col_idx)
            elif header == "Net Pay":
                paydf.at[row_idx, month] = calculate_net_pay(PAYDF_TEMPLATE, paydf, col_idx)
            elif header == "Difference":
                paydf.at[row_idx, month] = calculate_difference(paydf, col_idx)
    return paydf



# =========================
# update custom rows
# =========================

def remove_custom_template_rows(PAYDF_TEMPLATE):
    PAYDF_TEMPLATE.drop(PAYDF_TEMPLATE[PAYDF_TEMPLATE['custom'] == True].index, inplace=True)


def add_custom_template_rows(PAYDF_TEMPLATE, custom_rows):
    existing_headers = set(PAYDF_TEMPLATE['header'].values)
    
    for row in custom_rows:
        header = row['header']

        if header in existing_headers:
            header = f"{header}_unique"

        PAYDF_TEMPLATE.loc[len(PAYDF_TEMPLATE)] = {
            'header': header,
            'varname': '',
            'shortname': '',
            'longname': '',
            'type': row['type'],
            'dtype': 'Decimal',
            'default': 0,
            'required': False,
            'onetime': False,
            'standard': False,
            'tax': row['tax'],
            'option': False,
            'custom': True,
            'modal': ''
        }
        row['header'] = header
        existing_headers.add(header)


def add_custom_row(paydf, custom_rows):
    first_month_col = paydf.columns[1]

    for row in custom_rows:
        if first_month_col:
            paydf.loc[len(paydf)] = [row['header'], 0]
        else:
            paydf.loc[len(paydf)] = [row['header']]
    return paydf