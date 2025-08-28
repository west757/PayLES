from flask import request, render_template, session, jsonify
from app import csrf

from app import flask_app
from app.utils import (
    load_json,
    convert_numpy_types,
    validate_file,
    get_month_headers,
)
from app.les import (
    validate_les, 
    process_les,
)
from app.budget import (
    build_budget,
    add_row,
    remove_month,
    build_months,
)
from app.forms import (
    HomeForm,
)


@flask_app.route('/')
def index():
    home_form = HomeForm()
    return render_template('home.html', home_form=home_form)


@flask_app.route('/submit_les', methods=['POST'])
def submit_les():
    home_form = HomeForm()
    if not home_form.validate_on_submit():
            return jsonify({'message': "Invalid submission"}), 400

    if home_form.submit_les.data:
        les_file = home_form.home_input.data

        if not les_file:
            return jsonify({'message': "No file submitted"}), 400
        
        valid, message = validate_file(les_file)
        if not valid:
            return jsonify({'message': message}), 400
        
        valid, message, les_pdf = validate_les(les_file)

    elif home_form.submit_example.data:
        valid, message, les_pdf = validate_les(flask_app.config['EXAMPLE_LES'])
    else:
        return jsonify({'message': "Unknown action, no LES or example submitted"}), 400

    if valid:
        les_image, rect_overlay, les_text = process_les(les_pdf)
        budget, initial_month = build_budget(les_text)
        budget, month_headers = build_months(all_rows=True, budget=budget, prev_month=initial_month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'] - 1)
        header_data = flask_app.config['BUDGET_HEADER_LIST'] + flask_app.config['VARIABLE_HEADER_LIST']

        session['budget'] = budget
        session['header_data'] = header_data

        LES_REMARKS = load_json(flask_app.config['LES_REMARKS_JSON'])
        MODALS = load_json(flask_app.config['MODALS_JSON'])

        config_js = {
            'budget': convert_numpy_types(budget),
            'headerData': header_data,
            'MAX_CUSTOM_ROWS': flask_app.config['MAX_CUSTOM_ROWS'],
            'TRAD_TSP_RATE_MAX': flask_app.config['TRAD_TSP_RATE_MAX'],
            'ROTH_TSP_RATE_MAX': flask_app.config['ROTH_TSP_RATE_MAX'],
            'GRADES': flask_app.config['GRADES'],
            'HOME_OF_RECORDS': flask_app.config['HOME_OF_RECORDS'],
            'HOME_OF_RECORDS_ABBR': flask_app.config['HOME_OF_RECORDS_ABBR'],
            'SGLI_COVERAGES': flask_app.config['SGLI_COVERAGES'],
        }
        context = {
            'config_js': config_js,
            'les_image': les_image,
            'rect_overlay': rect_overlay,
            'budget': convert_numpy_types(budget),
            'month_headers': month_headers,
            'header_data': header_data,
            'LES_REMARKS': LES_REMARKS,
            'MODALS': MODALS,
        }
        return render_template('content.html', **context)
    else:
        return jsonify({'message': message}), 400
    

@csrf.exempt
@flask_app.route('/update_budget', methods=['POST'])
def update_budget():
    budget = session.get('budget', [])
    month_headers = get_month_headers(budget)
    header_data = session.get('header_data', [])
    row_header = request.form.get('row_header', '')
    col_month = request.form.get('col_month', '')
    value = request.form.get('value', 0)
    repeat = request.form.get('repeat', False)

    row = next((r for r in budget if r.get('header') == row_header), None)
    field = row.get('field')

    if field in ('int', int):
        value = int(value)
    elif field in ('float', float):
        try:
            value = float(value)
        except ValueError:
            value = 0.0
        value *= row.get('sign')
        value = round(value, 2)
    repeat = str(repeat).lower() == "true"

    if col_month in month_headers:
        idx = month_headers.index(col_month)
        months_num = len(month_headers) - idx
        budget, month_headers = build_months(all_rows=False, budget=budget, prev_month=col_month, months_num=months_num, 
                                             row_header=row_header, col_month=col_month, value=value, repeat=repeat)

    session['budget'] = budget

    config_js = {
        'budget': convert_numpy_types(budget),
    }
    context = {
        'config_js': config_js,
        'budget': convert_numpy_types(budget),
        'month_headers': month_headers,
        'header_data': header_data,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/update_months', methods=['POST'])
def update_months():
    budget = session.get('budget', [])
    month_headers = get_month_headers(budget)
    header_data = session.get('header_data', [])
    next_months_num = int(request.form.get('months_num', flask_app.config['DEFAULT_MONTHS_NUM']))
    prev_months_num = len(month_headers)

    if next_months_num < prev_months_num:
        months_to_remove = month_headers[next_months_num:]
        for month in months_to_remove:
            remove_month(budget, month)
        month_headers = month_headers[:next_months_num]

    elif next_months_num > prev_months_num:
        months_num = next_months_num - prev_months_num
        prev_month = month_headers[-1]

        budget, month_headers = build_months(all_rows=True, budget=budget, prev_month=prev_month, months_num=months_num)

    session['budget'] = budget

    config_js = {
        'budget': convert_numpy_types(budget),
    }
    context = {
        'config_js': config_js,
        'budget': convert_numpy_types(budget),
        'month_headers': month_headers,
        'header_data': header_data,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/add_injects', methods=['POST'])
def add_injects():
    budget = session.get('budget', [])
    month_headers = get_month_headers(budget)
    header_data = session.get('header_data', [])
    method = request.form.get('method', '')
    row_type = request.form.get('row_type', '')
    header = request.form.get('header', '').strip()
    value = request.form.get('value', '0').strip()
    tax = request.form.get('tax', 'false').lower() == 'true'
    initial_month = month_headers[0]

    if row_type == 'd' or row_type == 'a':
        sign = -1
    else:
        sign = 1

    try:
        value = float(value)
    except ValueError:
        value = 0
    value = round(value, 2)
    value *= sign

    insert_idx = len(budget)

    if method == 'template':
        if row_type == 'e':
            insert_idx = max([i for i, r in enumerate(budget) if r.get('type') == 'e'], default=-1) + 1
        elif row_type == 'd':
            insert_idx = max([i for i, r in enumerate(budget) if r.get('type') == 'd'], default=-1) + 1
        elif row_type == 'a':
            a_indices = [i for i, r in enumerate(budget) if r.get('type') == 'a']
            if a_indices:
                insert_idx = max(a_indices) + 1
            else:
                d_indices = [i for i, r in enumerate(budget) if r.get('type') == 'd']
                insert_idx = max(d_indices, default=-1) + 1

        row = add_row(flask_app.config['BUDGET_TEMPLATE'], header, 0.00, initial_month)
        for idx, m in enumerate(month_headers[1:]):
            row[m] = value
        budget.insert(insert_idx, row)

    elif method == 'custom':
        c_indices = [i for i, r in enumerate(budget) if r.get('type') == 'c']
        a_indices = [i for i, r in enumerate(budget) if r.get('type') == 'a']
        d_indices = [i for i, r in enumerate(budget) if r.get('type') == 'd']
        if c_indices:
            insert_idx = max(c_indices) + 1
        elif a_indices:
            insert_idx = max(a_indices) + 1
        elif d_indices:
            insert_idx = max(d_indices) + 1

        custom_rows = [r for r in budget if r.get('type') == 'c']
        if len(custom_rows) >= flask_app.config['MAX_CUSTOM_ROWS']:
            return jsonify({'message': 'Maximum number of custom rows reached. Cannot have more than ' + str(flask_app.config['MAX_CUSTOM_ROWS']) + ' custom rows.'}), 400

        row = {'header': header}
        for meta in flask_app.config['ROW_METADATA']:
            if meta == 'type':
                row['type'] = 'c'
            elif meta == 'sign':
                row['sign'] = sign
            elif meta == 'field':
                row['field'] = 'float'
            elif meta == 'tax':
                row['tax'] = tax
            elif meta == 'editable':
                row['editable'] = True
            elif meta == 'modal':
                row['modal'] = ''

        for idx, m in enumerate(month_headers):
            row[m] = 0.0 if idx == 0 else value
        budget.insert(insert_idx, row)

        if not any(h['header'].lower() == header.lower() for h in header_data):
            header_data.append({
                'header': header,
                'type': 'c',
                'tooltip': 'Custom row added by user',
            })
    else:
        return jsonify({'message': 'Invalid method.'}), 400

    budget, month_headers = build_months(
        all_rows=False,
        budget=budget,
        prev_month=month_headers[1],
        months_num=len(month_headers),
        row_header=header,
        col_month=month_headers[1],
        value=value,
        repeat=True
    )

    session['budget'] = budget
    session['header_data'] = header_data

    config_js = {
        'budget': convert_numpy_types(budget),
        'headerData': header_data,
    }
    context = {
        'config_js': config_js,
        'budget': convert_numpy_types(budget),
        'month_headers': month_headers,
        'header_data': header_data,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/remove_row', methods=['POST'])
def remove_row():
    header = request.form.get('header', '').strip()
    budget = session.get('budget', [])
    month_headers = get_month_headers(budget)
    header_data = session.get('header_data', [])

    row = next((r for r in budget if r.get('header').lower() == header.lower()), None)
    budget = [r for r in budget if r.get('header').lower() != header.lower()]
    if row and row.get('type') == 'c':
        header_data = [h for h in header_data if h.get('header').lower() != header.lower()]

    budget, month_headers = build_months(all_rows=False, budget=budget, prev_month=month_headers[1], months_num=len(month_headers), 
                                         row_header="", col_month="", value=0, repeat=True)

    session['budget'] = budget
    session['header_data'] = header_data

    config_js = {
        'budget': convert_numpy_types(budget),
        'headerData': header_data,
    }
    context = {
        'config_js': config_js,
        'budget': convert_numpy_types(budget),
        'month_headers': month_headers,
        'header_data': header_data,
    }
    return render_template('budget.html', **context)


@flask_app.route('/about')
def about():
    return render_template('about.html')


@flask_app.route('/faq')
def faq():
    FAQS = load_json(flask_app.config['FAQ_JSON'])
    return render_template('faq.html', FAQS=FAQS)


@flask_app.route('/resources')
def resources():
    RESOURCES = load_json(flask_app.config['RESOURCES_JSON'])
    return render_template('resources.html', RESOURCES=RESOURCES)


@flask_app.route('/levdf')
def levdf():
    return render_template('levdf.html')
