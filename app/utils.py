import json
import numpy as np

from app import flask_app


def load_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        return {}


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


def add_row(template, header, month, value):
    ROW_METADATA = flask_app.config['ROW_METADATA']
    row_data = template[template['header'] == header]
    metadata = {}

    for col in ROW_METADATA:
        if col in row_data.columns:
            metadata[col] = row_data.iloc[0][col]

    row = {'header': header}
    row.update(metadata)
    row[month] = value
    return row


def validate_calculate_zip_mha(zip_code):
    MHA_ZIP_CODES = flask_app.config['MHA_ZIP_CODES']

    if zip_code in ("00000", "", "Not Found"):
        return "Not Found", "Not Found"

    try:
        zip_int = int(zip_code)
        mha_search = MHA_ZIP_CODES[MHA_ZIP_CODES.isin([zip_int])].stack()

        if not mha_search.empty:
            mha_search_row = mha_search.index[0][0]
            mha = str(MHA_ZIP_CODES.loc[mha_search_row, "mha"])
            return str(zip_code), mha
        else:
            return "Not Found", "Not Found"
        
    except Exception:
        return "Not Found", "Not Found"
    

def validate_home_of_record(home_of_record):
    if home_of_record in flask_app.config['HOME_OF_RECORDS_ABBR']:
        return home_of_record
    return "Not Found"


def get_months(budget):
    metadata_keys = set(['header']) | set(flask_app.config['ROW_METADATA'])
    return [key for key in budget[0].keys() if key not in metadata_keys]


def add_recommendations(budget, month):
    recs = []

    # SGLI minimum coverage recommendation
    sgli_rate = next((row[month] for row in budget if row.get('header', '') == 'SGLI Rate'), 0)
    if sgli_rate == 0:
        recs.append(
            '<div class="rec-item"><b>SGLI Coverage:</b> You currently have no SGLI coverage. It is recommended to have at ' \
            'least the minimum amount of SGLI coverage, which is a $3.50 monthly premium for $50,000. This is due to also ' \
            'providing you with Traumatic Injury Protection Coverage (TSGLI).</div>'
        )

    # TSP matching recommendation
    months_in_service = next((row[month] for row in budget if row.get('header', '') == 'Months in Service'), 0)
    trad_tsp = next((row[month] for row in budget if row.get('header', '') == 'Trad TSP Base Rate'), 0)
    roth_tsp = next((row[month] for row in budget if row.get('header', '') == 'Roth TSP Base Rate'), 0)
    if months_in_service >= 24 and (trad_tsp + roth_tsp) < 5:
        recs.append(
            '<div class="rec-item"><b>TSP Base Rate:</b> You are fully vested in the Thrift Savings Plan, however are not ' \
            'currently taking advantage of the service agency automatic matching up to 5%. It is recommended to increase ' \
            'the Traditional TSP or Roth TSP Base Rate contribution percentages to at least 5% to receive the full matching ' \
            'contributions.</div>'
        )

    tsp_ytd = next((row[month] for row in budget if row.get('header', '') == 'YTD TSP Contribution'), 0)
    tsp_limit = flask_app.config['TSP_CONTRIBUTION_LIMIT']
    if tsp_ytd > tsp_limit:
        recs.append(
            f'<div class="rec-item"><b>TSP Contribution Limit:</b> You are currently anticipating reaching the limit of TSP contributions for the year, which is ${tsp_limit:,.2f}. '
            'It is recommended to reduce your TSP contribution percentages to ensure you do not invest over this limit to avoid penalties.</div>'
        )

    # state income tax recommendation
    home_of_record = next((row[month] for row in budget if row.get('header', '') == 'Home of Record'), '')
    mha = next((row[month] for row in budget if row.get('header', '') == 'MHA'), '')
    hor_row = None

    for r in flask_app.config['HOME_OF_RECORDS']:
        if r['abbr'] == home_of_record:
            hor_row = r
            break

    if hor_row:
        income_type = hor_row.get('income', '').lower()
        tooltip = hor_row.get('tooltip', '')
        show_state_tax_msg = False

        if income_type in ['partial', 'full']:
            show_state_tax_msg = True
        elif income_type == 'outside' and mha != "Not Found":
            mha_state = mha[:2]
            if mha_state == home_of_record:
                show_state_tax_msg = True

        if show_state_tax_msg:
            msg = (
                '<div class="rec-item"><b>State Income Tax:</b> You are currently paying state income tax. It is '
                'recommended to investigate options and requirements relating to your home of record, as you may '
                'be eligible to avoid paying state income tax. This may include changing your home of record to a '
                'state which does not tax military income, or meeting certain exemptions for your current home of record.'
            )
            if tooltip:
                msg += f'<br>{tooltip}'
            msg += '</div>'
            recs.append(msg)

    if not recs:
        recs.append('<div class="rec-item">No current recommendations for your budget.</div>')

    return recs