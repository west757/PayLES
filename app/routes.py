from flask import request, render_template, session, jsonify
from app import csrf

from app import flask_app
from app.budget import (
    init_budget,
    add_months,
    update_months,
    remove_months,
    remove_row,
    insert_row,
)
from app.forms import (
    FormSingleExample,
    FormJoint,
)
from app.les import (
    validate_les, 
    process_les,
    calc_les_rect_overlay,
)
from app.tsp import (
    init_tsp,
)
from app.utils import (
    load_json,
    convert_numpy_types,
    validate_file,
    get_months,
    add_recommendations,
)


@flask_app.route('/')
def index():
    form_single_example = FormSingleExample()
    form_joint = FormJoint()

    config_js = {
        'MAX_ROWS': flask_app.config['MAX_ROWS'],
        'TRAD_TSP_RATE_MAX': flask_app.config['TRAD_TSP_RATE_MAX'],
        'ROTH_TSP_RATE_MAX': flask_app.config['ROTH_TSP_RATE_MAX'],
        'MONTHS_SHORT': flask_app.config['MONTHS_SHORT'],
        'COMPONENTS': list(flask_app.config['COMPONENTS'].keys()),
        'GRADES': flask_app.config['GRADES'],
        'HOME_OF_RECORDS': flask_app.config['HOME_OF_RECORDS'].to_dict(orient='records'),
        'FEDERAL_FILING_STATUSES': list(flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'].keys()),
        'STATE_FILING_STATUSES': list(flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'].keys())[:2],
        'SGLI_COVERAGES': flask_app.config['SGLI_COVERAGES'],
        'COMBAT_ZONES': flask_app.config['COMBAT_ZONES'],
    }
    context = {
        'config_js': config_js,
        'form_single_example': form_single_example,
        'form_joint': form_joint,
        'CURRENT_YEAR': flask_app.config['CURRENT_YEAR'],
        'CURRENT_MONTH': flask_app.config['CURRENT_MONTH'],
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
        show_guide_buttons = False

    elif 'button_example' in request.form:
        valid, message, les_pdf = validate_les(flask_app.config['LES_EXAMPLE'])
        show_guide_buttons = True

    else:
        return jsonify({'message': "Invalid submission"}), 400

    if valid:
        les_image, les_text = process_les(les_pdf)
        les_rect_overlay = calc_les_rect_overlay()

        print(les_text)

        budget, init_month, headers = init_budget(les_text=les_text)
        tsp = init_tsp(budget, init_month, les_text=les_text)
        budget, tsp, months = add_months(budget, tsp, latest_month=init_month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'], init=True)

        recommendations = add_recommendations(budget, months)
        budget = convert_numpy_types(budget)
        session['budget'] = budget
        session['tsp'] = tsp
        session['headers'] = headers

        config_js = {
            'budget': budget,
            'tsp': tsp,
            'months': months,
            'headers': headers,
            'recommendations': recommendations,
        }
        context = {
            'config_js': config_js,
            'budget': budget,
            'tsp': tsp,
            'months': months,
            'headers': headers,
            'les_image': les_image,
            'les_rect_overlay': les_rect_overlay,
            'show_guide_buttons': show_guide_buttons,
            'LES_REMARKS': load_json(flask_app.config['LES_REMARKS_JSON']),
            'MODALS': load_json(flask_app.config['MODALS_JSON']),
        }
        return render_template('settings.html', **context)
    else:
        return jsonify({'message': message}), 400


@flask_app.route('/route_joint', methods=['POST'])
def route_joint():
    form = FormJoint()

    if not form.validate_on_submit():
        return jsonify({'message': "Invalid submission"}), 400

    file1 = form.input_file_joint_1.data
    file2 = form.input_file_joint_2.data

    if not file1:
        return jsonify({'message': "No file submitted for Member 1"}), 400
    if not file2:
        return jsonify({'message': "No file submitted for Member 2"}), 400

    valid1, message1 = validate_file(file1)
    if not valid1:
        return jsonify({'message': message1}), 400
    valid2, message2 = validate_file(file2)
    if not valid2:
        return jsonify({'message': message2}), 400

    valid1, message1, les_pdf1 = validate_les(file1)
    if not valid1:
        return jsonify({'message': message1}), 400
    valid2, message2, les_pdf2 = validate_les(file2)
    if not valid2:
        return jsonify({'message': message2}), 400

    if valid1 and valid2:
        les_image1, les_text1 = process_les(les_pdf1)
        les_image2, les_text2 = process_les(les_pdf2)
        les_rect_overlay = calc_les_rect_overlay()


        budget, init_month, headers = init_budget(les_text=les_text1)
        tsp = init_tsp(budget, init_month, les_text=les_text1)
        budget, tsp, months = add_months(budget, tsp, latest_month=init_month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'], init=True)

        recommendations = add_recommendations(budget, months)
        budget = convert_numpy_types(budget)
        session['budget'] = budget
        session['tsp'] = tsp
        session['headers'] = headers

        config_js = {
            'budget': budget,
            'tsp': tsp,
            'months': months,
            'headers': headers,
            'recommendations': recommendations,
        }
        context = {
            'config_js': config_js,
            'budget': budget,
            'tsp': tsp,
            'months': months,
            'headers': headers,
            'les_image': les_image1,
            'les_rect_overlay': les_rect_overlay,
            'LES_REMARKS': load_json(flask_app.config['LES_REMARKS_JSON']),
            'MODALS': load_json(flask_app.config['MODALS_JSON']),
        }
        return render_template('settings.html', **context)
    else:
        return jsonify({'message': "Invalid submission"}), 400


@csrf.exempt
@flask_app.route('/route_initials', methods=['POST'])
def route_initials():
    initials = request.form.to_dict()

    budget, init_month, headers = init_budget(initials=initials)
    tsp = init_tsp(init_month, budget, initials=initials)
    budget, months = add_months(budget, latest_month=init_month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'])
    
    recommendations = add_recommendations(budget, months)
    budget = convert_numpy_types(budget)
    session['budget'] = budget
    session['tsp'] = tsp
    session['headers'] = headers

    config_js = {
        'budget': budget,
        'tsp': tsp,
        'months': months,
        'headers': headers,
        'recommendations': recommendations,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'tsp': tsp,
        'months': months,
        'headers': headers,
        'MODALS': load_json(flask_app.config['MODALS_JSON']),
    }
    return render_template('settings.html', **context)


@csrf.exempt
@flask_app.route('/route_update_cell', methods=['POST'])
def route_update_cell():
    budget = session.get('budget', [])
    tsp = session.get('tsp', [])
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

    budget, tsp = update_months(budget, tsp, months, cell_header, cell_month, cell_value, cell_repeat)
    
    recommendations = add_recommendations(budget, months)
    budget = convert_numpy_types(budget)
    session['budget'] = budget
    session['tsp'] = tsp

    config_js = {
        'budget': budget,
        'tsp': tsp,
        'recommendations': recommendations,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'tsp': tsp,
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/route_change_months', methods=['POST'])
def route_change_months():
    budget = session.get('budget', [])
    tsp = session.get('tsp', [])
    headers = session.get('headers', [])
    months = get_months(budget)

    new_months_num = int(request.form.get('months_num', flask_app.config['DEFAULT_MONTHS_NUM']))
    old_months_num = len(months)

    if new_months_num < old_months_num:
        budget, tsp, months = remove_months(budget, tsp, new_months_num)
    elif new_months_num > old_months_num:
        budget, tsp, months = add_months(budget, tsp, latest_month=months[-1], months_num=new_months_num)

    recommendations = add_recommendations(budget, months)
    budget = convert_numpy_types(budget)
    session['budget'] = budget
    session['tsp'] = tsp

    config_js = {
        'budget': budget,
        'tsp': tsp,
        'months': months,
        'recommendations': recommendations,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'tsp': tsp,
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/route_insert_row', methods=['POST'])
def route_insert_row():
    budget = session.get('budget', [])
    tsp = session.get('tsp', [])
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
    }

    budget, headers = insert_row(budget, months, headers, row_data)
    budget, tsp = update_months(budget, tsp, months)

    recommendations = add_recommendations(budget, months)
    budget = convert_numpy_types(budget)
    session['budget'] = budget
    session['tsp'] = tsp
    session['headers'] = headers

    config_js = {
        'budget': budget,
        'tsp': tsp,
        'headers': headers,
        'recommendations': recommendations,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'tsp': tsp,
        'months': months,
        'headers': headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/route_remove_row', methods=['POST'])
def route_remove_row():
    budget = session.get('budget', [])
    tsp = session.get('tsp', [])
    months = get_months(budget)
    headers = session.get('headers', [])

    header = request.form.get('header', '')

    budget, headers = remove_row(budget, headers, header)
    budget, tsp = update_months(budget, tsp, months)

    recommendations = add_recommendations(budget, months)
    budget = convert_numpy_types(budget)
    session['budget'] = budget
    session['tsp'] = tsp
    session['headers'] = headers

    config_js = {
        'budget': budget,
        'tsp': tsp,
        'headers': headers,
    }
    context = {
        'config_js': config_js,
        'budget': budget,
        'tsp': tsp,
        'months': months,
        'headers': headers,
        'recommendations': recommendations,
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
