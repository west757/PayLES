import os
import json
from decimal import Decimal


def validate_file(file, allowed_extensions):
    if file.filename == '':
        return False, "No file submitted"
    if not allowed_file(file.filename, allowed_extensions):
        return False, "Invalid file type, only PDFs are accepted"
    return True, ""


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


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


def load_json(filename, static_folder):
    path = os.path.join(static_folder, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


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


def load_json(STATIC_FOLDER, filename):
    path = os.path.join(STATIC_FOLDER, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)
    

def find_multiword_matches(section, shortname):
    short_words = shortname.split()
    n = len(short_words)
    matches = []

    for i in range(len(section) - n + 1):
        candidate = ' '.join(section[i:i+n])
        if candidate == shortname:
            matches.append(i + n - 1)

    return matches


def months_in_service(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


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


def parse_eda_sections(section, row):
    value = None
    found = False
    shortname = str(row['shortname'])
    matches = find_multiword_matches(section, shortname)

    for idx in matches:
        for j in range(idx + 1, len(section)):
            s = section[j]
            is_num = s.replace('.', '', 1).replace('-', '', 1).isdigit() or (s.startswith('-') and s[1:].replace('.', '', 1).isdigit())
            
            if is_num:
                val = Decimal(section[j])
                value = abs(val)
                found = True
                break

        if found:
            break

    if not found:
        if bool(row['required']):
            default_value = cast_dtype(row['default'], row['dtype'])
            value = abs(default_value)
        else:
            return None
        
    return cast_dtype(value, row['dtype'])


def update_eda_rows(paydf, row_idx, header, match, month, columns, options, custom_rows):
    if match.iloc[0].get('custom', False):
        custom_row = next((r for r in custom_rows if r['header'] == header), None)

        if custom_row:
            col_idx = columns.index(month)
            value_idx = col_idx - 2
            value = custom_row['values'][value_idx] if 0 <= value_idx < len(custom_row['values']) else Decimal(0)
            paydf.at[row_idx, month] = value
        return True

    if bool(match.iloc[0].get('onetime', False)):
        paydf.at[row_idx, month] = 0
        return True

    if bool(match.iloc[0].get('standard', False)):
        future_value, future_month = get_option(header, options)
        col_idx = columns.index(month)
        prev_month = columns[col_idx - 1]
        prev_value = paydf.at[row_idx, prev_month]

        if future_month in columns:
            future_col_idx = columns.index(future_month)
            current_col_idx = columns.index(month)

            if future_col_idx is not None and current_col_idx >= future_col_idx:
                paydf.at[row_idx, month] = future_value
            else:
                paydf.at[row_idx, month] = prev_value
        else:
            paydf.at[row_idx, month] = prev_value
        return True

    return False


def get_option(header, options):
    for opt in options:
        if opt[0] == header:
            return opt[1], opt[2]
    return None, None