import json
import numpy as np
import pandas as pd
import re
import traceback

from app import flask_app


def get_error_context(exc, custom_message=""):
    tb = traceback.extract_tb(exc.__traceback__)[-1]
    file_name = tb.filename
    function_name = tb.name
    line_number = tb.lineno
    exc_type = type(exc).__name__
    error_message = str(exc)
    
    return {
        "custom_message": custom_message,
        "filepath": file_name,
        "function": function_name,
        "line": line_number,
        "error_type": exc_type,
        "error_message": error_message,
    }


def load_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f), ""
    except FileNotFoundError as e:
        return {}, f"JSON file not found: {path}"
    except json.JSONDecodeError as e:
        return {}, f"Invalid JSON format in {path}: {e}"
    except Exception as e:
        return {}, f"Error loading JSON from {path}: {e}"


def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    return obj


def validate_file(file):
    if file.filename == '':
        return False, "No file submitted"
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in flask_app.config['ALLOWED_EXTENSIONS']):
        return False, "Invalid file type, only PDFs are accepted"
    return True, ""


def get_headers():
    return (flask_app.config['PAY_TEMPLATE'][['header', 'type', 'tooltip']].to_dict(orient='records') 
            + flask_app.config['PARAMS_TEMPLATE'][['header', 'type', 'tooltip']].to_dict(orient='records') 
            + flask_app.config['TSP_TEMPLATE'][['header', 'type', 'tooltip']].to_dict(orient='records'))


def add_row(table_type, table, header, template=None, metadata=None):
    if table_type == "budget":
        metadata_fields = flask_app.config['BUDGET_METADATA']
        type_order = flask_app.config['BUDGET_TYPE_ORDER']
    elif table_type == "tsp":
        metadata_fields = flask_app.config['TSP_METADATA']
        type_order = flask_app.config['TSP_TYPE_ORDER']

    if template is not None:
        row_data = template[template['header'] == header]
        if row_data.empty:
            return None
        row_metadata = {col: row_data.iloc[0][col] for col in metadata_fields if col in row_data.columns}
    elif metadata:
        row_metadata = metadata.copy()
    else:
        return None

    row_type = row_metadata.get('type', None)
    row = {'header': header}
    row.update(row_metadata)

    insert_idx = len(table)  # default to end
    if row_type and type_order:
        # find all indices of rows with the same type
        same_type_indices = [i for i, r in enumerate(table) if r.get('type') == row_type]
        if same_type_indices:
            insert_idx = same_type_indices[-1] + 1  # insert row after last of same type
        else:
            # find the first row of any later type in type_order
            type_pos = type_order.index(row_type)
            later_types = type_order[type_pos + 1:]
            next_idx = next((i for i, r in enumerate(table) if r.get('type') in later_types), None)
            if next_idx is not None:
                insert_idx = next_idx

    table.insert(insert_idx, row)
    return None


# add a month-value pair to a row identified by header
def add_mv_pair(table, header, month, value):
    row = next((r for r in table if r['header'] == header), None)
    if row is None:
        return
    
    field = row['field']
    if field == 'int':
        value = int(value)
    elif field == 'float':
        value = float(value)
    row[month] = value


def build_table_index(table):
    return {row['header']: row for row in table}


def sum_rows_via_modal(budget, modal_str, month):
    total = 0.0
    for row in budget:
        if row.get('modal') == modal_str:
            value = row.get(month, 0.0)
            try:
                total += float(value)
            except (TypeError, ValueError):
                continue
    return total


def get_table_val(table, header, month):
    row = next((r for r in table if r['header'] == header), None)
    if row is None:
        return None
    return row.get(month, None)


def get_months(budget):
    metadata_keys = set(['header']) | set(flask_app.config['ROW_METADATA'])
    return [key for key in budget[0].keys() if key not in metadata_keys]


def parse_pay_string(pay_string, pay_template):
    results = {}

    # for each lesname in PAY_TEMPLATE, search for it in the string and extract the float after it
    for _, row in pay_template.iterrows():
        lesname = row['lesname']

        if not isinstance(lesname, str) or not lesname.strip():
            continue

        # regex: match lesname followed by a float (with optional comma)
        pattern = rf"{re.escape(lesname)}\s+(-?\d+(?:\.\d+)?)"
        match = re.search(pattern, pay_string)

        if match:
            try:
                value = float(match.group(1).replace(",", ""))
                results[lesname] = round(value, 2)
            except Exception:
                continue

    return results


def set_variable_longs(budget, budget_index, month):
    branch = budget_index.get('Branch').get(month)
    branch_long = flask_app.config['BRANCHES'].get(branch, "Not Found")
    add_mv_pair(budget, 'Branch Long', month, branch_long)

    component = budget_index.get('Component').get(month)
    component_long = flask_app.config['COMPONENTS'].get(component, "Not Found")
    add_mv_pair(budget, 'Component Long', month, component_long)

    zip_code = budget_index.get('Zip Code').get(month)
    _, mha_long = get_military_housing_area(zip_code)
    add_mv_pair(budget, 'MHA Long', month, mha_long)

    locality_code = budget_index.get('OCONUS Locality Code').get(month)
    #get locality code long
    add_mv_pair(budget, 'Locality Code Long', month, "")
    
    home_of_record = budget_index.get('Home of Record').get(month)
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


def add_recommendations(budget, months):
    recs = {}

    # SGLI minimum coverage recommendation
    sgli_months = []
    for month in months:
        sgli_rate = next((row[month] for row in budget if row.get('header', '') == 'SGLI Rate'), 0)
        if sgli_rate == 0:
            sgli_months.append(month)
    if sgli_months:
        recs['sgli'] = {
            'months': sgli_months,
            'text': (
                '<b>SGLI Coverage:</b> For month(s): 'f'{", ".join(sgli_months)}, you have no SGLI coverage. PayLES recommends having at least the minimum amount of SGLI coverage, which is a $3.50 monthly premium for $50,000. This also provides Traumatic Injury Protection Coverage (TSGLI). Learn more at <a href="https://www.insurance.va.gov/sgliSite/default.htm" target="_blank">VA SGLI</a>.'
            )
        }

    # TSP contribution limit recommendation
    #tsp_contribution_limit = flask_app.config['TSP_ELECTIVE_LIMIT']
    #tsp_contrib_months = []
    #for month in months:
    #    ytd_trad = next((row[month] for row in budget if row.get('header', '') == 'YTD Trad TSP'), 0)
    #    ytd_roth = next((row[month] for row in budget if row.get('header', '') == 'YTD Roth TSP'), 0)
    #    if (ytd_trad + ytd_roth) >= tsp_contribution_limit:
    #        tsp_contrib_months.append(month)
    #if tsp_contrib_months:
    #    recs['tsp_contribution_limit'] = {
    #        'months': tsp_contrib_months,
    #        'text': (
    #            '<b>TSP Contribution Limit:</b> For month(s): 'f'{", ".join(tsp_contrib_months)}, the TSP contribution limit of ${tsp_contribution_limit} has been reached. Any additional contributions not made within a combat zone towards the Traditional TSP will not be deducted. PayLES recommends adjusting your TSP contribution rates to avoid reaching the contribution limit. Learn more at <a href="https://www.tsp.gov/making-contributions/contribution-limits/" target="_blank">TSP Contribution Limits</a>.'
    #        )
    #    }

    # TSP annual limit recommendation
    #tsp_annual_limit = flask_app.config['TSP_ANNUAL_LIMIT']
    #tsp_annual_months = []
    #for month in months:
    #    ytd_trad = next((row[month] for row in budget if row.get('header', '') == 'YTD Trad TSP'), 0)
    #    ytd_trad_exempt = next((row[month] for row in budget if row.get('header', '') == 'YTD Trad TSP Exempt'), 0)
    #    ytd_roth = next((row[month] for row in budget if row.get('header', '') == 'YTD Roth TSP'), 0)
    #    ytd_matching = next((row[month] for row in budget if row.get('header', '') == 'YTD TSP Matching'), 0)
    #    if (ytd_trad + ytd_trad_exempt + ytd_roth + ytd_matching) >= tsp_annual_limit:
    #        tsp_annual_months.append(month)
    #if tsp_annual_months:
    #    recs['tsp_annual_limit'] = {
    #        'months': tsp_annual_months,
    #        'text': (
    #            '<b>TSP Annual Limit:</b> For month(s): 'f'{", ".join(tsp_annual_months)}, the TSP annual limit of ${tsp_annual_limit} has been reached. Any additional contributions will not be deducted. PayLES recommends adjusting your TSP contribution rates to avoid reaching the contribution limit. Learn more at <a href="https://www.tsp.gov/making-contributions/contribution-limits/" target="_blank">TSP Contribution Limits</a>.'
    #        )
    #    }

    # Combat zone TSP recommendation
    #combat_zone_months = []
    #for month in months:
    #    combat_zone = next((row[month] for row in budget if row.get('header', '') == 'Combat Zone'), "No")
    #    if str(combat_zone).strip().lower() == "yes":
    #        combat_zone_months.append(month)
    #if combat_zone_months:
    #    recs['combat_zone_tsp'] = {
    #        'months': combat_zone_months,
    #        'text': (
    #            '<b>Combat Zone:</b> For month(s): 'f'{", ".join(combat_zone_months)}, you are anticipating being in a combat zone. PayLES recommends taking full advantage of the TSP combat zone tax exclusion (CZTE) benefit by contributing as much as practical to the Traditional TSP. Learn more at <a href="https://themilitarywallet.com/maximizing-your-thrift-savings-plan-contributions-in-a-combat-zone/" target="_blank">How to Maximize TSP Contributions in a Combat Zone</a>.'
    #        )
    #    }

    # negative net pay recommendation
    negative_net_pay_months = []
    for month in months:
        net_pay = next((row[month] for row in budget if row.get('header', '') == 'Net Pay'), 0)
        if net_pay < 0:
            negative_net_pay_months.append(month)
    if negative_net_pay_months:
        recs['negative_net_pay'] = {
            'months': negative_net_pay_months,
            'text': (
                '<b>Negative Net Pay:</b> For month(s): 'f'{", ".join(negative_net_pay_months)}, you have a negative net pay. PayLES recommends recalculating parts of your budget to avoid a negative net pay as that can potentially incur debts and missed payments for deductions or allotments. Learn more about U.S. military debts at <a href="https://www.dfas.mil/debtandclaims/" target="_blank">DFAS Debts & Claims</a>.'
            )
        }

    # TSP matching recommendation
    #months_in_service = None
    #for row in budget:
    #    if row.get('header', '') == 'Months in Service':
    #        # Use the first month found (should be the same for all months)
    #        months_in_service = next((row[m] for m in months if m in row), None)
    #        break

    #tsp_matching_months = []
    #if months_in_service is not None and months_in_service >= 24:
    #    for month in months:
    #        trad_rate = next((row[month] for row in budget if row.get('header', '') == 'Trad TSP Base Rate'), 0)
    #        roth_rate = next((row[month] for row in budget if row.get('header', '') == 'Roth TSP Base Rate'), 0)
    #        if (trad_rate + roth_rate) < 5:
    #            tsp_matching_months.append(month)
    #if tsp_matching_months:
    #    recs['tsp_matching'] = {
    #        'months': tsp_matching_months,
    #        'text': (
    #            '<b>TSP Matching:</b> For month(s): 'f'{", ".join(tsp_matching_months)}, you are fully vested in the TSP however are not taking full advantage of the 1%-4% agency matching for TSP contributions. PayLES recommends to have the combined total of your Traditional TSP base rate and Roth TSP base rate to be at least 5% to get the highest agency matching rate. Your current combined rate is {trad_rate + roth_rate}%. Learn more at <a href="https://www.tsp.gov/making-contributions/contribution-types/" target="_blank">TSP Contribution Types</a>.'
    #        )
    #    }


    # state income tax recommendation
    HOME_OF_RECORDS = flask_app.config['HOME_OF_RECORDS']
    home_of_record_row = next((row for row in budget if row.get('header', '') == "Home of Record"), None)
    mha_row = next((row for row in budget if row.get('header', '') == "Military Housing Area"), None)

    if home_of_record_row and mha_row:
        taxed_states = {}
        for month in months:
            home_of_record = home_of_record_row.get(month)

            if not home_of_record or home_of_record == "Not Found":
                continue
            hor_row = HOME_OF_RECORDS[HOME_OF_RECORDS['abbr'] == home_of_record]

            if hor_row.empty:
                continue
            income_taxed = hor_row['income_taxed'].values[0].lower()

            if income_taxed in ("none", "exempt"):
                continue
            mha_code = mha_row.get(month)
            mha_state = mha_code[:2] if mha_code and len(mha_code) >= 2 else ""

            if income_taxed == "outside":
                if mha_state == home_of_record:
                    taxed_states.setdefault(home_of_record, []).append(month)
            elif income_taxed == "full":
                taxed_states.setdefault(home_of_record, []).append(month)

        for hor, taxed_months in taxed_states.items():
            if taxed_months:

                longname_row = HOME_OF_RECORDS[HOME_OF_RECORDS['abbr'] == hor]
                longname = longname_row['longname'].values[0] if not longname_row.empty else hor
                recs[f'state_tax_{hor}'] = {
                    'months': taxed_months,
                    'text': (
                        f'<b>State Income Tax:</b> For month(s): {", ".join(taxed_months)}, your home of record - {longname} - is taxing your military pay. PayLES recommends changing your home of record, if possible, to a state/territory which either has no state income tax, fully exempts military income, or does not tax military income when stationed outside of the home of record. View the <a href="/static/graphics/military_income_state_taxed_map.png" target="_blank">Military Income State Taxed Map</a>, and learn more at <a href="https://www.military.com/money/personal-finance/state-tax-information.html" target="_blank">Military State Tax Info</a>.'
                    )
                }

    return [rec['text'] for rec in recs.values()]
