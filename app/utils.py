import json
import numpy as np
import traceback

from app import flask_app


def load_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise Exception(get_error_context(e, f"JSON file not found: {path}"))
    except json.JSONDecodeError as e:
        raise Exception(get_error_context(e, f"Invalid JSON format in {path}: {e}"))
    except Exception as e:
        raise Exception(get_error_context(e, f"Error loading JSON from {path}: {e}"))


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


def validate_file(file):
    if file.filename == '':
        return False, "No file submitted"
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in flask_app.config['ALLOWED_EXTENSIONS']):
        return False, "Invalid file type, only PDFs are accepted"
    return True, ""


def get_all_headers():
    return (flask_app.config['PAY_TEMPLATE'][['header', 'type', 'tooltip']].to_dict(orient='records') 
            + flask_app.config['PARAMS_TEMPLATE'][['header', 'type', 'tooltip']].to_dict(orient='records') 
            + flask_app.config['TSP_TEMPLATE'][['header', 'type', 'tooltip']].to_dict(orient='records'))


def add_row(pay, header, template=None, metadata=None):
    PAY_METADATA = flask_app.config['PAY_METADATA']
    type_order = list(flask_app.config['TYPE_SIGN'].keys())

    if template is not None:
        row_data = template[template['header'] == header]
        row_metadata = {col: row_data.iloc[0][col] for col in PAY_METADATA if col in row_data.columns}
    elif metadata:
        row_metadata = metadata.copy()

    type = row_metadata.get('type')
    row = {'header': header, **row_metadata}

    insert_idx = len(pay)
    if type and type_order:
        same_type_indices = [i for i, r in enumerate(pay) if r.get('type') == type]
        if same_type_indices:
            insert_idx = same_type_indices[-1] + 1
        else:
            type_pos = type_order.index(type)
            later_types = set(type_order[type_pos + 1:])
            next_idx = next((i for i, r in enumerate(pay) if r.get('type') in later_types), None)
            if next_idx is not None:
                insert_idx = next_idx
    pay.insert(insert_idx, row)
    return None


# add a month-value pair to a row identified by header
def add_mv_pair(budget, header, month, value):
    row = next((r for r in budget if r['header'] == header), None)
    if row is None:
        return
    
    field = row['field']
    if field == 'int':
        value = int(value)
    elif field == 'float':
        value = float(value)
    row[month] = value


def get_months(pay):
    return [key for key in pay[0].keys() if key in flask_app.config['MONTHS'].keys()]


def get_row_value(budget, header, key=None):
    row = next((r for r in budget if r.get('header') == header), None)
    if row is not None:
        if key is not None:
            return row.get(key)
        return row
    return None


def sum_rows_via_modal(pay, modal_str, month):
    total = 0.0
    for row in pay:
        if row.get('modal') == modal_str:
            value = row.get(month, 0.0)
            try:
                total += float(value)
            except (TypeError, ValueError):
                continue
    return total
