from datetime import datetime
from flask import request, render_template, session, jsonify
from app import csrf

from app import flask_app
from app.utils import (
    load_json,
    convert_numpy_types,
    validate_file,
    get_months,
    add_recommendations,
)
from app.les import (
    validate_les, 
    process_les,
)
from app.budget import (
    init_budget,
    add_months,
    update_months,
    remove_months,
    remove_row,
    add_row,
)
from app.forms import (
    FormSingleExample,
    FormJoint,
)


@flask_app.route('/')
def index():
    form_single_example = FormSingleExample()
    form_joint = FormJoint()

    current_year = datetime.now().year
    current_month = datetime.now().strftime('%B')

    config_js = {
        'MAX_ROWS': flask_app.config['MAX_ROWS'],
        'OLDEST_YEAR': flask_app.config['OLDEST_YEAR'],
        'TRAD_TSP_RATE_MAX': flask_app.config['TRAD_TSP_RATE_MAX'],
        'ROTH_TSP_RATE_MAX': flask_app.config['ROTH_TSP_RATE_MAX'],
        'MONTHS_SHORT': flask_app.config['MONTHS_SHORT'],
        'GRADES': flask_app.config['GRADES'],
        'HOME_OF_RECORDS': flask_app.config['HOME_OF_RECORDS'].to_dict(orient='records'),
        'MHA_ZIP_CODES': flask_app.config['MHA_ZIP_CODES'][['mha', 'mha_name']].to_dict(orient='records'),
        'FEDERAL_FILING_STATUSES': list(flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'].keys()),
        'STATE_FILING_STATUSES': list(flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'].keys())[:2],
        'SGLI_COVERAGES': flask_app.config['SGLI_COVERAGES'],
        'COMBAT_ZONES': flask_app.config['COMBAT_ZONES'],
    }
    context = {
        'config_js': config_js,
        'form_single_example': form_single_example,
        'form_joint': form_joint,
        'current_year': current_year,
        'current_month': current_month,
    }
    return render_template('home.html', **context)


@flask_app.route('/route_single_example', methods=['POST'])
def route_single_example():
    form = FormSingleExample()

    if 'button_single' in request.form:
        if not form.validate_on_submit():
            return jsonify({'message': "Invalid submission"}), 400

        file = form.input_file_single.data
        if not file:
            return jsonify({'message': "No file submitted"}), 400
    
        valid, message = validate_file(file)
        if not valid:
            return jsonify({'message': message}), 400
        
        valid, message, les_pdf = validate_les(file)
        show_instructions = False

    elif 'button_example' in request.form:
        valid, message, les_pdf = validate_les(flask_app.config['EXAMPLE_LES'])
        show_instructions = True

    if valid:
        les_image, rect_overlay, les_text = process_les(les_pdf)
        budget, init_month, headers = init_budget(les_text=les_text)
        budget, months = add_months(budget, latest_month=init_month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'], init=True)
        recommendations = add_recommendations(budget, init_month)

        budget = convert_numpy_types(budget)
        session['budget'] = budget
        session['headers'] = headers

        config_js = {
            'budget': budget,
            'months': months,
            'headers': headers,
        }
        context = {
            'config_js': config_js,
            'budget': budget,
            'months': months,
            'headers': headers,
            'les_image': les_image,
            'rect_overlay': rect_overlay,
            'recommendations': recommendations,
            'show_instructions': show_instructions,
            'LES_REMARKS': load_json(flask_app.config['LES_REMARKS_JSON']),
            'MODALS': load_json(flask_app.config['MODALS_JSON']),
        }
        return render_template('content.html', **context)
    else:
        return jsonify({'message': message}), 400


@flask_app.route('/route_joint', methods=['POST'])
def route_joint():
    form = FormJoint()

    if not form.validate_on_submit():
        return jsonify({'message': "Invalid submission"}), 400

    file1 = form.input_file_joint_1.data
    file2 = form.input_file_joint_2.data

    if not file1 or not file2:
        return jsonify({'message': "Both LES files required"}), 400

    return render_template('content.html')


@csrf.exempt
@flask_app.route('/route_initials', methods=['POST'])
def route_initials():
    current_year = datetime.now().year
    current_month = datetime.now().strftime('%b').upper()

    initials = {
        'current_year': current_year,
        'current_month': current_month,
        'grade': request.form.get('input-select-initials-grade', ''),
        'months_in_service': int(request.form.get('input-int-initials-mis', 0)),
        'zip_code': request.form.get('input-int-initials-zc', ''),
        'home_of_record': request.form.get('input-select-initials-hor', ''),
        'dependents': int(request.form.get('input-int-initials-deps', 0)),
        'federal_filing_status': request.form.get('input-select-initials-ffs', ''),
        'state_filing_status': request.form.get('input-select-initials-sfs', ''),
        'sgli_coverage': request.form.get('input-select-initials-sc', ''),
        'combat_zone': request.form.get('input-select-initials-cz', ''),
        'trad_tsp_base_rate': int(request.form.get('input-int-initials-tradbase', 0)),
        'trad_tsp_specialty_rate': int(request.form.get('input-int-initials-tradspecialty', 0)),
        'trad_tsp_incentive_rate': int(request.form.get('input-int-initials-tradincentive', 0)),
        'trad_tsp_bonus_rate': int(request.form.get('input-int-initials-tradbonus', 0)),
        'roth_tsp_base_rate': int(request.form.get('input-int-initials-rothbase', 0)),
        'roth_tsp_specialty_rate': int(request.form.get('input-int-initials-rothspecialty', 0)),
        'roth_tsp_incentive_rate': int(request.form.get('input-int-initials-rothincentive', 0)),
        'roth_tsp_bonus_rate': int(request.form.get('input-int-initials-rothbonus', 0)),
        'ytd_income': float(request.form.get('input-float-initials-ytd-income', 0.00)),
        'ytd_expenses': float(request.form.get('input-float-initials-ytd-expenses', 0.00)),
        'ytd_tsp': float(request.form.get('input-float-initials-ytd-tsp', 0.00)),
        'ytd_charity': float(request.form.get('input-float-initials-ytd-charity', 0.00)),
    }

    home_of_record_long = initials['home_of_record']
    HOME_OF_RECORDS = flask_app.config['HOME_OF_RECORDS']
    abbr_row = HOME_OF_RECORDS.loc[HOME_OF_RECORDS['home_of_record'] == home_of_record_long]
    initials['home_of_record'] = abbr_row.iloc[0]['abbr']

    budget, init_month, headers = init_budget(initials=initials)
    budget, months = add_months(budget, latest_month=init_month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'])
    recommendations = add_recommendations(budget, init_month)

    budget = convert_numpy_types(budget)
    session['budget'] = budget
    session['headers'] = headers

    config_js = {
        'budget': budget,
        'months': months,
        'headers': headers,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'months': months,
        'headers': headers,
        'recommendations': recommendations,
        'MODALS': load_json(flask_app.config['MODALS_JSON']),
    }
    return render_template('content.html', **context)


@csrf.exempt
@flask_app.route('/route_update_cell', methods=['POST'])
def route_update_cell():
    budget = session.get('budget', [])
    months = get_months(budget)
    headers = session.get('headers', [])
    
    cell_header = request.form.get('row_header', '')
    cell_month = request.form.get('month', '')
    cell_value = request.form.get('value', 0)
    cell_repeat = request.form.get('repeat', False).lower() == "true"

    cell_row = next((r for r in budget if r.get('header') == cell_header), None)
    cell_field = cell_row.get('field')

    if cell_field in ('int', int):
        cell_value = int(cell_value)
    elif cell_field in ('float', float):
        cell_value = round((float(cell_value) * cell_row.get('sign')), 2)

    budget = update_months(budget, months, cell_header, cell_month, cell_value, cell_repeat)

    budget = convert_numpy_types(budget)
    session['budget'] = budget

    config_js = {
        'budget': budget,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/route_change_months', methods=['POST'])
def route_change_months():
    budget = session.get('budget', [])
    headers = session.get('headers', [])
    months = get_months(budget)

    new_months_num = int(request.form.get('months_num', flask_app.config['DEFAULT_MONTHS_NUM']))
    old_months_num = len(months)

    if new_months_num < old_months_num:
        budget, months = remove_months(budget, new_months_num)
    elif new_months_num > old_months_num:
        budget, months = add_months(budget, latest_month=months[-1], months_num=new_months_num)

    budget = convert_numpy_types(budget)
    session['budget'] = budget

    config_js = {
        'budget': budget,
        'months': months,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/route_add_row', methods=['POST'])
def route_add_row():
    budget = session.get('budget', [])
    months = get_months(budget)
    headers = session.get('headers', [])

    row_data = {
        'method': request.form.get('method', ''),
        'type': request.form.get('type', ''),
        'header': request.form.get('header', '').strip(),
        'value': request.form.get('value', '0').strip(),
        'tax': request.form.get('tax', 'false').lower() == 'true',
        'percent': request.form.get('percent', '0'),
        'interest': request.form.get('interest', '0'),
        'rows': request.form.get('rows', '').split(','),
    }
    

    budget, headers = add_row(budget, months, headers, row_data)
    budget = update_months(budget, months)

    budget = convert_numpy_types(budget)
    session['budget'] = budget
    session['headers'] = headers

    config_js = {
        'budget': budget,
        'headers': headers,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)




@csrf.exempt
@flask_app.route('/route_remove_row', methods=['POST'])
def route_remove_row():
    budget = session.get('budget', [])
    months = get_months(budget)
    headers = session.get('headers', [])

    header = request.form.get('header', '')

    budget, headers = remove_row(budget, headers, header)
    budget = update_months(budget, months)

    budget = convert_numpy_types(budget)
    session['budget'] = budget
    session['headers'] = headers

    config_js = {
        'budget': budget,
        'headers': headers,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@flask_app.route('/about')
def about():
    return render_template('about.html')


@flask_app.route('/faq')
def faq():
    context = {
        'FAQS': load_json(flask_app.config['FAQ_JSON']),
    }
    return render_template('faq.html', **context)


@flask_app.route('/resources')
def resources():
    context = {
        'RESOURCES': load_json(flask_app.config['RESOURCES_JSON']),
    }
    return render_template('resources.html', **context)


@flask_app.route('/leave')
def leave():
    return render_template('leave.html')
