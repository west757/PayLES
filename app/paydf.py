from datetime import datetime
from decimal import Decimal
from flask import session
import json
import pandas as pd

from app import flask_app
from app import utils
from app.calculations import (
    calculate_taxed_income,
    calculate_total_taxes,
    calculate_gross_pay,
    calculate_net_pay,
    calculate_difference,
    calculate_base_pay,
    calculate_bas,
    calculate_bah,
    calculate_federal_taxes,
    calculate_fica_social_security,
    calculate_fica_medicare,
    calculate_sgli,
    calculate_state_taxes,
    calculate_traditional_tsp,
    calculate_roth_tsp,
)


# =========================
# build paydf
# =========================

def build_paydf(les_text):
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    DEFAULT_MONTHS_DISPLAY = flask_app.config['DEFAULT_MONTHS_DISPLAY']
    initial_month = les_text[8][3]
    rows = []

    remove_custom_template_rows(PAYDF_TEMPLATE)

    rows = add_variables(rows, les_text)
    rows = add_eda(PAYDF_TEMPLATE, rows, les_text)
    taxable, nontaxable = calculate_taxed_income(PAYDF_TEMPLATE, rows)
    rows.append(["Taxable Income", taxable])
    rows.append(["Non-Taxable Income", nontaxable])
    rows.append(["Total Taxes", calculate_total_taxes(PAYDF_TEMPLATE, rows)])
    rows.append(["Gross Pay", calculate_gross_pay(PAYDF_TEMPLATE, rows)])
    rows.append(["Net Pay", calculate_net_pay(PAYDF_TEMPLATE, rows)])
    rows.append(["Difference", 0])

    session['paydf_rows'] = rows
    paydf = pd.DataFrame(rows, columns=["header", initial_month])

    options = build_options(PAYDF_TEMPLATE, rows, initial_month)

    paydf = expand_paydf(PAYDF_TEMPLATE, paydf, options, DEFAULT_MONTHS_DISPLAY)

    col_headers = paydf.columns.tolist()
    row_headers = paydf['header'].tolist()

    return paydf, col_headers, row_headers, options, DEFAULT_MONTHS_DISPLAY


def add_variables(rows, les_text):
    try:
        year = int('20' + les_text[8][4])
    except Exception:
        year = 0
    rows.append(["Year", year])

    try:
        grade = str(les_text[2][1])
    except Exception:
        grade = "Not Found"
    rows.append(["Grade", grade])

    try:
        pay_date = datetime.strptime(les_text[3][2], '%y%m%d')
        les_date = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
        months_in_service = int(utils.months_in_service(les_date, pay_date))
    except Exception:
        months_in_service = 0
    rows.append(["Months in Service", months_in_service])

    try:
        zip_code = les_text[48][2] if les_text[48][2] != "00000" else "Not Found"
    except Exception:
        zip_code = "Not Found"
    rows.append(["Zip Code", zip_code])

    try:
        military_housing_area = utils.calculate_mha(flask_app.config['MHA_ZIP_CODES'], les_text[48][2])
    except Exception:
        military_housing_area = "Not Found"
    rows.append(["Military Housing Area", military_housing_area])

    try:
        tax_residency_state = les_text[39][1] if les_text[39][1] != "98" else "Not Found"
    except Exception:
        tax_residency_state = "Not Found"
    rows.append(["Tax Residency State", tax_residency_state])

    try:
        status = les_text[24][1]
        if status == "S":
            federal_filing_status = "Single"
        elif status == "M":
            federal_filing_status = "Married"
        elif status == "H":
            federal_filing_status = "Head of Household"
        else:
            federal_filing_status = "Not Found"
    except Exception:
        federal_filing_status = "Not Found"
    rows.append(["Federal Filing Status", federal_filing_status])

    try:
        status = les_text[42][1]
        if status == "S":
            state_filing_status = "Single"
        elif status == "M":
            state_filing_status = "Married"
        else:
            state_filing_status = "Not Found"
    except Exception:
        state_filing_status = "Not Found"
    rows.append(["State Filing Status", state_filing_status])

    try:
        dependents = int(les_text[53][1])
    except Exception:
        dependents = 0
    rows.append(["Dependents", dependents])

    combat_zone = "No"
    rows.append(["Combat Zone", combat_zone])

    try:
        sgli_total = None
        deductions = les_text[10]
        for idx, item in enumerate(deductions):
            if isinstance(item, str) and "sgli" in item.lower():
                for j in range(idx + 1, len(deductions)):
                    val = deductions[j]
                    try:
                        sgli_total = float(val)
                        break
                    except (ValueError, TypeError):
                        continue
                if sgli_total is not None:
                    break

        if sgli_total is not None:
            SGLI_RATES = flask_app.config['SGLI_RATES']

            match = SGLI_RATES[SGLI_RATES['total'] == sgli_total]
            if not match.empty:
                sgli_coverage = int(match.iloc[0]['coverage'])
            else:
                sgli_coverage = 0
        else:
            sgli_coverage = 0
    except Exception:
        sgli_coverage = 0
    rows.append(["SGLI Coverage", sgli_coverage])

    try:
        ttsp_fields = [int(les_text[60][3]), int(les_text[62][3]), int(les_text[64][3]), int(les_text[66][3])]
        traditional_tsp_rate = next((val for val in ttsp_fields if val > 0), 0)
    except Exception:
        traditional_tsp_rate = 0
    rows.append(["Traditional TSP Rate", traditional_tsp_rate])

    try:
        rtsp_fields = [int(les_text[69][3]), int(les_text[71][3]), int(les_text[73][3]), int(les_text[75][3])]
        roth_tsp_rate = next((val for val in rtsp_fields if val > 0), 0)
    except Exception:
        roth_tsp_rate = 0
    rows.append(["Roth TSP Rate", roth_tsp_rate])

    return rows


def add_eda(PAYDF_TEMPLATE, rows, les_text):
    for _, row in PAYDF_TEMPLATE.iterrows():
        header = row['header']
        shortname = str(row['shortname'])
        sign = int(row['sign'])
        required = bool(row['required'])
        value = None
        found = False

        #entitlements in les_text[9], deductions/allotments in les_text[10] and les_text[11]
        if sign == 1:
            sections = [les_text[9]]
        else:
            sections = [les_text[10], les_text[11]]

        #search to see if shortname is in the section
        for section in sections:
            matches = utils.find_multiword_matches(section, shortname)

            for idx in matches:
                for j in range(idx + 1, len(section)):
                    s = section[j]
                    is_num = s.replace('.', '', 1).replace('-', '', 1).isdigit() or (s.startswith('-') and s[1:].replace('.', '', 1).isdigit())
                    if is_num:
                        value = sign * abs(Decimal(section[j]))
                        found = True
                        break
                if found:
                    break
            if found:
                break

        if not found:
            if required:
                value = 0
            else:
                continue

        rows.append([header, value])

    return rows



# =========================
# build options
# =========================

def build_options(PAYDF_TEMPLATE, rows, initial_month):
    template_options = PAYDF_TEMPLATE[PAYDF_TEMPLATE['option'] == True]
    row_dict = {header: value for header, value in rows}
    options = []

    # Loop through template options and add to options array if header is in rows
    for _, row in template_options.iterrows():
        header = row['header']
        if header in row_dict:
            value = row_dict[header]
            options.append([header, value, initial_month])

    return options


def update_options(PAYDF_TEMPLATE, paydf, form, initial_month=None):
    """
    Update the options array based on form input.
    This function will be responsible for handling form values and updating options accordingly.
    """
    # Implementation will depend on your form structure and requirements
    pass



# =========================
# expand paydf
# =========================

def expand_paydf(PAYDF_TEMPLATE, paydf, options, months_display, custom_rows=None):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']
    initial_month = paydf.columns[1]
    month_idx = MONTHS_SHORT.index(initial_month)

    # Get row indices for tax rows
    row_headers = paydf['header'].tolist()
    idx_taxable = row_headers.index("Taxable Income")
    idx_nontaxable = row_headers.index("Non-Taxable Income")
    idx_totaltaxes = row_headers.index("Total Taxes")

    for i in range(1, months_display):
        month_idx = (month_idx + 1) % 12
        new_month = MONTHS_SHORT[month_idx]
        col = []

        # 1. Variables
        col = update_variables(paydf, col, new_month, options)
        # 2. Entitlements
        col = update_entitlements(PAYDF_TEMPLATE, paydf, new_month, options, col)

        # 3. Insert placeholders for tax rows
        while len(col) < idx_taxable:
            col.append(None)
        col.append(None)  # Taxable Income
        col.append(None)  # Non-Taxable Income
        col.append(None)  # Total Taxes

        # 4. Calculate taxable and nontaxable income using the current col
        taxable, nontaxable = calculate_taxed_income(PAYDF_TEMPLATE, col)

        # 5. Assign taxable and nontaxable to correct positions
        col[idx_taxable] = taxable
        col[idx_nontaxable] = nontaxable

        # 6. Deductions/Allotments (may depend on taxable/nontaxable)
        col = update_da(PAYDF_TEMPLATE, paydf, new_month, options, col)

        # 7. Now calculate total taxes using the updated col
        totaltaxes = calculate_total_taxes(PAYDF_TEMPLATE, col)
        col[idx_totaltaxes] = totaltaxes

        # 8. Continue with the rest
        col.append(calculate_gross_pay(PAYDF_TEMPLATE, col))
        col.append(calculate_net_pay(PAYDF_TEMPLATE, col))
        col.append(calculate_difference(col))

        paydf[new_month] = col

    return paydf




def update_variables(paydf, col, month, form):
    MONTHS_SHORT = flask_app.config['MONTHS_SHORT']

    variable_specs = [
        # (header, form_field, form_month_field, type_cast, special_case)
        ("Year", "year_f", "year_m", int, "year"),
        ("Grade", "grade_f", "grade_m", str, None),
        ("Months in Service", "months_in_service_f", "months_in_service_m", int, "mis"),
        ("Zip Code", "zip_code_f", "zip_code_m", str, None),
        ("Military Housing Area", "military_housing_area_f", "military_housing_area_m", str, "mha"),
        ("Tax Residency State", "tax_residency_state_f", "tax_residency_state_m", str, None),
        ("Federal Filing Status", "federal_filing_status_f", "federal_filing_status_m", str, None),
        ("State Filing Status", "state_filing_status_f", "state_filing_status_m", str, None),
        ("Dependents", "dependents_f", "dependents_m", int, None),
        ("Combat Zone", "combat_zone_f", "combat_zone_m", str, None),
        ("SGLI Coverage", "sgli_coverage_f", "sgli_coverage_m", int, None),
        ("Traditional TSP Rate", "traditional_tsp_rate_f", "traditional_tsp_rate_m", int, None),
        ("Roth TSP Rate", "roth_tsp_rate_f", "roth_tsp_rate_m", int, None),
    ]

    columns = paydf.columns.tolist()
    col_idx = columns.index(month)
    prev_month = columns[col_idx - 1] if col_idx > 0 else columns[1]

    def get_prev(header):
        return paydf.at[paydf[paydf['header'] == header].index[0], prev_month]

    for idx, (header, f_field, m_field, cast, special) in enumerate(variable_specs):
        prev = get_prev(header)
        val = form.get(f_field)
        mval = form.get(m_field)

        # Special handling for certain variables
        if special == "year":
            if mval == month and val is not None:
                try:
                    col.append(int(val))
                except Exception:
                    col.append(prev)
            else:
                if MONTHS_SHORT.index(month) == 0 and MONTHS_SHORT.index(prev_month) == 11:
                    col.append(int(prev) + 1)
                else:
                    col.append(prev)
        elif special == "mis":
            if mval == month and val is not None:
                try:
                    col.append(int(val))
                except Exception:
                    col.append(prev)
            else:
                col.append(int(prev) + 1)
        elif special == "mha":
            if mval == month and val is not None:
                col.append(val)
            else:
                zip_code = col[3]  # Zip Code is always the 4th variable
                col.append(utils.calculate_mha(flask_app.config['MHA_ZIP_CODES'], zip_code))
        else:
            if mval == month and val is not None:
                try:
                    col.append(cast(val))
                except Exception:
                    col.append(prev)
            else:
                col.append(prev)
    return col



def update_entitlements(PAYDF_TEMPLATE, paydf, month, form, col):
    columns = paydf.columns.tolist()
    ent_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['sign'] == 1]['header'].tolist()

    for header in ent_rows:
        row_idx = paydf[paydf['header'] == header].index[0]
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if header == 'Base Pay':
            col.append(calculate_base_pay(paydf, month))
        elif header == 'BAS':
            col.append(calculate_bas(paydf, month))
        elif header == 'BAH':
            col.append(calculate_bah(paydf, month))
        else:
            col = update_eda_rows(paydf, row_idx, header, match, month, columns, form, col)

    return col



def update_da(PAYDF_TEMPLATE, paydf, month, form, col):
    columns = paydf.columns.tolist()
    da_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['sign'] == -1]['header'].tolist()

    for header in da_rows:
        row_idx = paydf[paydf['header'] == header].index[0]
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        if header == 'Federal Taxes':
            col.append(calculate_federal_taxes(paydf, month))
        elif header == 'FICA - Social Security':
            col.append(calculate_fica_social_security(paydf, month))
        elif header == 'FICA - Medicare':
            col.append(calculate_fica_medicare(paydf, month))
        elif header == 'SGLI':
            col.append(calculate_sgli(paydf, row_idx, month, None))
        elif header == 'State Taxes':
            col.append(calculate_state_taxes(paydf, month))
        elif header == 'Traditional TSP':
            col.append(calculate_traditional_tsp(paydf, month))
        elif header == 'Roth TSP':
            col.append(calculate_roth_tsp(paydf, month))
        else:
            col = update_eda_rows(paydf, row_idx, header, match, month, columns, form, col)

    return col



def update_eda_rows(paydf, row_idx, header, match, month, columns, form, col):
    if bool(match.iloc[0].get('onetime', False)):
        col.append(0)
        return col

    varname = match.iloc[0]['varname']
    checkbox_field = f"{varname}_f"
    month_field = f"{varname}_m"
    checked = form.get(checkbox_field)
    checked_month = form.get(month_field)
    prev_month = columns[columns.index(month) - 1] if columns.index(month) > 0 else columns[1]
    prev_value = paydf.at[row_idx, prev_month]

    if checked_month == month and checked:
        col.append(prev_value)
    else:
        col.append(0)

    return col



# =========================
# update custom rows
# =========================

def remove_custom_template_rows(PAYDF_TEMPLATE):
    PAYDF_TEMPLATE.drop(PAYDF_TEMPLATE[PAYDF_TEMPLATE['custom'] == True].index, inplace=True)


def parse_custom_rows(custom_rows_json):
    custom_rows = []

    if custom_rows_json:
        custom_rows = json.loads(custom_rows_json)

        if isinstance(custom_rows, dict):
            custom_rows = [custom_rows]

        for row in custom_rows:
            row['values'] = [Decimal(v) if v not in [None, ""] else Decimal(0) for v in row['values']]

            if row.get('type') == 'D':
                row['values'] = [-abs(v) for v in row['values']]

            row['tax'] = row.get('tax', False)
    return custom_rows


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