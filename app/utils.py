from decimal import Decimal
import json
import os


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


def months_in_service(date1, date2):
    return (date1.year - date2.year) * 12 + date1.month - date2.month


def validate_zip_code(MHA_ZIP_CODES, zip_code):
    if not (MHA_ZIP_CODES.isin([int(zip_code)]).any().any()):
        return "Not Found"
    return str(zip_code)


def calculate_mha(MHA_ZIP_CODES, zip_code):
    if zip_code != "00000" and zip_code != "" and zip_code != "Not Found":
        mha_search = MHA_ZIP_CODES[MHA_ZIP_CODES.isin([int(zip_code)])].stack()
        mha_search_row = mha_search.index[0][0]
        mha = MHA_ZIP_CODES.loc[mha_search_row, "mha"]
    else:
        mha = "Not Found"

    return mha


def get_option(header, options):
    for opt in options:
        if opt[0] == header:
            return opt[1], opt[2]
    return None, None