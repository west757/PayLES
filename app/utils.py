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
    ALLOWED_EXTENSIONS = flask_app.config['ALLOWED_EXTENSIONS']

    if file.filename == '':
        return False, "No file submitted"
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        return False, "Invalid file type, only PDFs are accepted"
    return True, ""


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
    HOME_OF_RECORDS = flask_app.config['HOME_OF_RECORDS']
    if home_of_record in HOME_OF_RECORDS:
        return home_of_record
    return "Not Found"


def get_month_headers(budget):
    difference_row = next((row for row in budget if row.get('header') == 'Difference'), None)
    if difference_row:
        return [key for key in difference_row.keys() if key != 'header']
    return []