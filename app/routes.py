from datetime import datetime
from flask import request, render_template, session, jsonify
from app import csrf

from app import flask_app
from app.utils import (
    load_json,
    convert_numpy_types,
    validate_file,
    add_row,
    get_months,
)
from app.les import (
    validate_les, 
)
from app.budget import (
    init_budget,
    remove_months,
    add_months,
    update_months,
)
from app.forms import (
    FormSubmitSingle,
    FormSubmitJoint,
)


@flask_app.route('/')
def index():
    form_single = FormSubmitSingle()
    form_joint = FormSubmitJoint()

    current_year = datetime.now().year
    current_month = datetime.now().strftime('%B')

    HOME_OF_RECORDS = ["Select Home of Record"] + [r['home_of_record'] for r in flask_app.config['HOME_OF_RECORDS']]

    config_js = {
        'MONTHS_SHORT': flask_app.config['MONTHS_SHORT'],
        'OLDEST_YEAR': flask_app.config['OLDEST_YEAR'],
        'MAX_CUSTOM_ROWS': flask_app.config['MAX_CUSTOM_ROWS'],
        'TRAD_TSP_RATE_MAX': flask_app.config['TRAD_TSP_RATE_MAX'],
        'ROTH_TSP_RATE_MAX': flask_app.config['ROTH_TSP_RATE_MAX'],
        'GRADES': flask_app.config['GRADES'],
        'HOME_OF_RECORDS': HOME_OF_RECORDS,
        'HOME_OF_RECORDS_ABBR': flask_app.config['HOME_OF_RECORDS_ABBR'],
        'FEDERAL_FILING_STATUSES': list(flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'].keys()),
        'STATE_FILING_STATUSES': list(flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'].keys())[:2],
        'SGLI_COVERAGES': flask_app.config['SGLI_COVERAGES'],
        'COMBAT_ZONES': flask_app.config['COMBAT_ZONES'],
    }
    context = {
        'config_js': config_js,
        'form_single': form_single,
        'form_joint': form_joint,
        'current_year': current_year,
        'current_month': current_month,
    }
    return render_template('home.html', **context)


@flask_app.route('/route_single', methods=['POST'])
def route_single():
    form = FormSubmitSingle()

    if not form.validate_on_submit():
        return jsonify({'message': "Invalid submission"}), 400

    file = form.input_file_single.data
    if not file:
        return jsonify({'message': "No file submitted"}), 400
    
    valid, message = validate_file(file)
    if not valid:
        return jsonify({'message': message}), 400
    
    valid, message, les_pdf = validate_les(file)

    if valid:
        context = init_budget(les_pdf)
        return render_template('content.html', **context)
    else:
        return jsonify({'message': message}), 400


@flask_app.route('/route_joint', methods=['POST'])
def route_joint():
    form = FormSubmitJoint()

    if not form.validate_on_submit():
        return jsonify({'message': "Invalid submission"}), 400

    file1 = form.input_file_joint_1.data
    file2 = form.input_file_joint_2.data

    if not file1 or not file2:
        return jsonify({'message': "Both LES files required"}), 400

    return render_template('home.html')


@csrf.exempt
@flask_app.route('/route_initials', methods=['POST'])
def route_initials():
    current_year = datetime.now().year
    current_month = datetime.now().strftime('%b').upper()

    initials = {
        'current_year': current_year,
        'current_month': current_month,
        'grade': request.form.get('input_int_initials_grade', ''),
        'months_in_service': request.form.get('input_int_initials_mis', ''),
        'zip_code': request.form.get('input_int_initials_zc', ''),
        'home_of_record': request.form.get('input_select_initials_hor', ''),
        'dependents': request.form.get('input_int_initials_deps', ''),
        'federal_filing_status': request.form.get('input_select_initials_ffs', ''),
        'state_filing_status': request.form.get('input_select_initials_sfs', ''),
        'sgli_coverage': request.form.get('input_select_initials_sc', ''),
        'combat_zone': request.form.get('input_select_initials_cz', ''),
    }

    context = init_budget(initials)
    return render_template('home.html', **context)


@csrf.exempt
@flask_app.route('/route_example', methods=['POST'])
def route_example():
    valid, message, les_pdf = validate_les(flask_app.config['EXAMPLE_LES'])

    if valid:
        context = init_budget(les_pdf)
        return render_template('content.html', **context)
    else:
        return jsonify({'message': message}), 400


@csrf.exempt
@flask_app.route('/update_budget', methods=['POST'])
def update_budget():
    budget = session.get('budget', [])
    headers = session.get('headers', [])
    months = get_months(budget)
    
    cell_header = request.form.get('row_header', '')
    cell_month = request.form.get('col_month', '')
    cell_value = request.form.get('value', 0)
    cell_repeat = request.form.get('repeat', False)

    cell_row = next((r for r in budget if r.get('header') == cell_header), None)
    cell_field = cell_row.get('field')

    if cell_field in ('int', int):
        cell_value = int(cell_value)
    elif cell_field in ('float', float):
        try:
            cell_value = float(cell_value)
        except ValueError:
            cell_value = 0.0
        cell_value *= cell_row.get('sign')
        cell_value = round(cell_value, 2)
    cell_repeat = str(cell_repeat).lower() == "true"

    budget = update_months(budget, months, cell_header, cell_month, cell_value, cell_repeat)

    session['budget'] = budget

    config_js = {
        'budget': convert_numpy_types(budget),
        'months': months,
    }
    context = {
        'config_js': config_js,
        'budget': convert_numpy_types(budget),
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/change_months', methods=['POST'])
def change_months():
    budget = session.get('budget', [])
    headers = session.get('headers', [])
    months = get_months(budget)

    new_months_num = int(request.form.get('months_num', flask_app.config['DEFAULT_MONTHS_NUM']))
    old_months_num = len(months)

    if new_months_num < old_months_num:
        budget, months = remove_months(budget, new_months_num)
    elif new_months_num > old_months_num:
        budget, months = add_months(budget, latest_month=months[-1], months_num=new_months_num)

    session['budget'] = budget

    config_js = {
        'budget': convert_numpy_types(budget),
        'months': months,
    }
    context = {
        'config_js': config_js,
        'budget': convert_numpy_types(budget),
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/add_inject', methods=['POST'])
def add_inject():
    budget = session.get('budget', [])
    headers = session.get('headers', [])
    months = get_months(budget)

    inject_method = request.form.get('method', '')
    inject_type = request.form.get('type', '')
    inject_header = request.form.get('header', '').strip()
    inject_value = request.form.get('value', '0').strip()
    inject_tax = request.form.get('tax', 'false').lower() == 'true'
    init_month = months[0]

    if inject_type == 'd' or inject_type == 'a':
        sign = -1
    else:
        sign = 1

    try:
        inject_value = float(inject_value)
    except ValueError:
        inject_value = 0
    inject_value = round(sign * inject_value, 2)

    insert_idx = len(budget)

    if inject_method == 'template':
        if inject_type == 'e':
            insert_idx = max([i for i, r in enumerate(budget) if r.get('type') == 'e'], default=-1) + 1
        elif inject_type == 'd':
            insert_idx = max([i for i, r in enumerate(budget) if r.get('type') == 'd'], default=-1) + 1
        elif inject_type == 'a':
            a_indices = [i for i, r in enumerate(budget) if r.get('type') == 'a']
            if a_indices:
                insert_idx = max(a_indices) + 1
            else:
                d_indices = [i for i, r in enumerate(budget) if r.get('type') == 'd']
                insert_idx = max(d_indices, default=-1) + 1

        inject_row = add_row(flask_app.config['BUDGET_TEMPLATE'], inject_header, init_month, 0.00)
        for idx, m in enumerate(months[1:]):
            inject_row[m] = inject_value
        budget.insert(insert_idx, inject_row)

    elif inject_method == 'custom':
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

        inject_row = {'header': inject_header}
        for meta in flask_app.config['ROW_METADATA']:
            if meta == 'type':
                inject_row['type'] = 'c'
            elif meta == 'sign':
                inject_row['sign'] = sign
            elif meta == 'field':
                inject_row['field'] = 'float'
            elif meta == 'tax':
                inject_row['tax'] = inject_tax
            elif meta == 'editable':
                inject_row['editable'] = True
            elif meta == 'modal':
                inject_row['modal'] = ''

        for idx, m in enumerate(months):
            inject_row[m] = 0.00 if idx == 0 else inject_value
        budget.insert(insert_idx, inject_row)

        if not any(h['header'].lower() == inject_header.lower() for h in headers):
            headers.append({
                'header': inject_header,
                'type': 'c',
                'tooltip': 'Custom row added by user',
            })
    else:
        return jsonify({'message': 'Invalid method.'}), 400

    budget = update_months(budget, months)

    session['budget'] = budget
    session['headers'] = headers

    config_js = {
        'budget': convert_numpy_types(budget),
        'months': months,
        'headers': headers,
    }
    context = {
        'config_js': config_js,
        'budget': convert_numpy_types(budget),
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/remove_row', methods=['POST'])
def remove_row():
    budget = session.get('budget', [])
    headers = session.get('headers', [])
    months = get_months(budget)

    header = request.form.get('header', '')

    row = next((r for r in budget if r.get('header').lower() == header.lower()), None)
    budget = [r for r in budget if r.get('header').lower() != header.lower()]
    if row.get('type') == 'c':
        headers = [h for h in headers if h.get('header').lower() != header.lower()]

    budget = update_months(budget, months)

    session['budget'] = budget
    session['headers'] = headers

    config_js = {
        'budget': convert_numpy_types(budget),
        'months': months,
        'headers': headers,
    }
    context = {
        'config_js': config_js,
        'budget': convert_numpy_types(budget),
        'months': months,
        'headers': headers,
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
