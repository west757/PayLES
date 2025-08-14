from decimal import Decimal
import json

from app import flask_app





def validate_file(file, ALLOWED_EXTENSIONS):
    if file.filename == '':
        return False, "No file submitted"
    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        return False, "Invalid file type, only PDFs are accepted"
    return True, ""


def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cast_dtype(value, dtype):
    if dtype == 'int':
        return int(value)
    elif dtype == 'str':
        return str(value)
    elif dtype == 'Decimal':
        return Decimal(value)
    elif dtype == 'bool':
        return bool(value)
    return value


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


def cast_dtype(value, dtype):
    if dtype == 'int':
        return int(value)
    elif dtype == 'str':
        return str(value)
    elif dtype == 'Decimal':
        return Decimal(value)
    elif dtype == 'bool':
        return bool(value)
    return value
    

def find_multiword_matches(section, shortname):
    short_words = shortname.split()
    n = len(short_words)
    matches = []

    for i in range(len(section) - n + 1):
        candidate = ' '.join(section[i:i+n])
        if candidate == shortname:
            matches.append(i + n - 1)

    return matches


def calculate_months_in_service(date1, date2):
    return (date1.year - date2.year) * 12 + date1.month - date2.month


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


def sum_rows(row_subset, col_dict):
    total = Decimal("0.00")
    for _, row in row_subset.iterrows():
        header = row['header']
        value = col_dict[header]
        total += value
    return total