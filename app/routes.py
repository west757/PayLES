import traceback

from flask import request, render_template, session, jsonify
from app import csrf

from app import flask_app
from app import pay
from app.pay import (
    get_pay_variables,
    compare_pay,
)
from app.forms import (
    FormSingle,
    FormJoint,
)
from app.les import (
    validate_les, 
    process_les,
    validate_les_age,
    get_les_rect_overlay,
)
from app.budgets import (
    init_budgets,
    add_months,
    update_months,
    remove_months,
    insert_row,
    remove_row,
    update_account,
    add_recommendations,
)
from app.tsp import (
    get_tsp_variables,
)
from app.utils import (
    load_json,
    validate_file,
    get_all_headers,
    get_months,
    get_row_value,
)


@flask_app.route('/')
def index():
    form_single = FormSingle()
    form_joint = FormJoint()

    config_js = {
        'MAX_ROWS': flask_app.config['MAX_ROWS'],
        'TRAD_TSP_RATE_MAX': flask_app.config['TRAD_TSP_RATE_MAX'],
        'ROTH_TSP_RATE_MAX': flask_app.config['ROTH_TSP_RATE_MAX'],
        'MONTHS': flask_app.config['MONTHS'],
        'BRANCHES': flask_app.config['BRANCHES'],
        'COMPONENTS_OPTIONS': list(flask_app.config['COMPONENTS'].values()),
        'GRADES_OPTIONS': flask_app.config['GRADES'],
        'HOME_OF_RECORDS_OPTIONS': flask_app.config['HOME_OF_RECORDS'].iloc[:, 0].tolist(),
        'DEPENDENTS_MAX': flask_app.config['DEPENDENTS_MAX'],
        'TAX_FILING_STATUSES': list(flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'].keys()),
        'SGLI_COVERAGES': flask_app.config['SGLI_COVERAGES'],
        'COMBAT_ZONES': flask_app.config['COMBAT_ZONES'],
        'DRILLS_MAX': flask_app.config['DRILLS_MAX'],
    }
    context = {
        'config_js': config_js,
        'form_single': form_single,
        'form_joint': form_joint,
        'CURRENT_YEAR': flask_app.config['CURRENT_YEAR'],
        'CURRENT_MONTH_LONG': flask_app.config['CURRENT_MONTH_LONG'],
    }
    return render_template('home.html', **context)


@flask_app.route('/route_single', methods=['POST'])
def route_single():
    form = FormSingle()

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

        valid, message, year, month = validate_les_age(les_text)
        if not valid:
            return jsonify({'message': message}), 400

        headers = get_all_headers()

        les_variables = get_pay_variables(les_text)
        tsp_variables = get_tsp_variables(les_text)

        pay, tsp = init_budgets(les_variables, tsp_variables, year, month, les_text=les_text)
        pay_calc, tsp_calc = init_budgets(les_variables, tsp_variables, year, month)

        pay, tsp, months = add_months(pay, tsp, month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'], init=True)

        #for row in pay:
        #    print(row)
        #print("-------------------")
        #for row in tsp:
        #    print(row)

        session['pay'] = pay
        session['tsp'] = tsp
        session['headers'] = headers

        config_js = {
            'pay': pay,
            'tsp': tsp,
            'months': months,
            'headers': headers,
            'discrepancies': compare_pay(pay, pay_calc, month),
            'recommendations': add_recommendations(pay, tsp, months),
        }
        context = {
            'config_js': config_js,
            'pay': pay,
            'tsp': tsp,
            'months': months,
            'headers': headers,
            'show_guide_buttons': show_guide_buttons,
            'les_image': les_image,
            'les_rect_overlay': get_les_rect_overlay(),
            'REMARKS': load_json(flask_app.config['REMARKS_JSON']),
            'MODALS': load_json(flask_app.config['MODALS_JSON']),
        }
        return render_template('bslm.html', **context)
    else:
        return jsonify({'message': message}), 400


@flask_app.route('/route_joint', methods=['POST'])
def route_joint():
    form = FormJoint()

    if not form.validate_on_submit():
        return jsonify({'message': "Invalid submission"}), 400

    file1 = form.input_file_joint1.data
    file2 = form.input_file_joint2.data

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
        headers = get_all_headers()

        month1, les_variables1 = get_pay_variables(les_text1)
        tsp_variables1 = get_tsp_variables(les_text1)

        month2, les_variables2 = get_pay_variables(les_text2)
        tsp_variables2 = get_tsp_variables(les_text2)

        if month1 != month2:
            return jsonify({'message': "LES months do not match. In order to use joint LES upload, both months must be the same."}), 400
        month = month1

        pay_les1, tsp_les1 = init_budgets(les_variables1, tsp_variables1, month, les_text=les_text1)
        pay_les2, tsp_les2 = init_budgets(les_variables2, tsp_variables2, month, les_text=les_text2)

        pay_les1, tsp_les1, months = add_months(pay_les1, tsp_les1, month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'], init=True)
        pay_les2, tsp_les2, months = add_months(pay_les2, tsp_les2, month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'], init=True)

        session['pay1'] = pay_les1
        session['pay2'] = pay_les2
        session['tsp1'] = tsp_les1
        session['tsp2'] = tsp_les2
        session['headers'] = headers

        config_js = {
            'pay1': pay_les1,
            'tsp1': tsp_les1,
            'pay2': pay_les2,
            'tsp2': tsp_les2,
            'months': months,
            'headers': headers,
            'recommendations': add_recommendations(pay_les1, months),
        }
        context = {
            'config_js': config_js,
            'pay1': pay_les1,
            'tsp1': tsp_les1,
            'pay2': pay_les2,
            'tsp2': tsp_les2,
            'months': months,
            'headers': headers,
            'les_image': les_image1,
            'les_rect_overlay': get_les_rect_overlay(),
            'REMARKS': load_json(flask_app.config['REMARKS_JSON']),
            'MODALS': load_json(flask_app.config['MODALS_JSON']),
        }
        return render_template('bslm.html', **context)
    else:
        return jsonify({'message': "Invalid submission"}), 400


@csrf.exempt
@flask_app.route('/route_manual', methods=['POST'])
def route_manual():
    month = flask_app.config['CURRENT_MONTH']
    headers = get_all_headers()

    manuals = request.form.to_dict()
    variables = manuals

    pay_calc, tsp_calc = init_budgets(variables, variables, month)
    pay_calc, tsp_calc, months = add_months(pay_calc, tsp_calc, month, months_num=flask_app.config['DEFAULT_MONTHS_NUM'], init=True)

    session['pay'] = pay_calc
    session['tsp'] = tsp_calc
    session['headers'] = headers

    config_js = {
        'pay': pay_calc,
        'tsp': tsp_calc,
        'months': months,
        'headers': headers,
        'recommendations': add_recommendations(pay_calc, months),
    }
    context = {
        'config_js': config_js,
        'pay': pay_calc,
        'tsp': tsp_calc,
        'months': months,
        'headers': headers,
        'MODALS': load_json(flask_app.config['MODALS_JSON']),
    }
    return render_template('bslm.html', **context)


@csrf.exempt
@flask_app.route('/route_update_cell', methods=['POST'])
def route_update_cell():
    pay = session.get('pay', [])
    tsp = session.get('tsp', [])
    months = get_months(pay)
    headers = session.get('headers', [])

    cell_header = request.form.get('header', '')
    cell_month = request.form.get('month', '')
    cell_value = request.form.get('value', 0)
    cell_repeat = request.form.get('repeat', False).lower() == "true"

    cell_field = get_row_value(pay, cell_header, 'field')

    if cell_field == "int":
        cell_value = int(cell_value)
    elif cell_field == "float":
        cell_value = round((float(cell_value) * get_row_value(pay, cell_header, 'sign')), 2)

    cell = {
        "header": cell_header,
        "month": cell_month,
        "value": cell_value,
        "repeat": cell_repeat
    }

    pay, tsp = update_months(pay, tsp, months, cell=cell)

    session['pay'] = pay
    session['tsp'] = tsp

    config_js = {
        'pay': pay,
        'tsp': tsp,
        'recommendations': add_recommendations(pay, months),
    }
    context = {
        'config_js': config_js,
        'pay': pay,
        'tsp': tsp,
        'months': months,
        'headers': headers,
    }
    return render_template('budgets.html', **context)


@csrf.exempt
@flask_app.route('/route_update_account', methods=['POST'])
def route_update_account():
    pay = session.get('pay', [])
    tsp = session.get('tsp', [])
    months = get_months(pay)
    headers = session.get('headers', [])

    header = request.form.get('header', '')
    initial = float(request.form.get('initial', 0.0))

    if header == "Direct Deposit Account":
        update_account(pay, header, months=months, initial=initial)
    elif header == "TSP Account":
        update_account(tsp, header, months=months, initial=initial)
    else:
        return jsonify({'message': "Invalid account header"}), 400

    session['pay'] = pay
    session['tsp'] = tsp

    config_js = {
        'pay': pay,
        'tsp': tsp,
        'months': months,
    }
    context = {
        'config_js': config_js,
        'pay': pay,
        'tsp': tsp,
        'months': months,
        'headers': headers,
    }
    return render_template('budgets.html', **context)


@csrf.exempt
@flask_app.route('/route_change_months', methods=['POST'])
def route_change_months():
    pay = session.get('pay', [])
    tsp = session.get('tsp', [])
    headers = session.get('headers', [])
    months = get_months(pay)

    old_months_num = len(months)
    new_months_num = int(request.form.get('months_num', flask_app.config['DEFAULT_MONTHS_NUM']))

    if old_months_num > new_months_num:
        pay, tsp, months = remove_months(pay, tsp, new_months_num)
    elif old_months_num < new_months_num:
        pay, tsp, months = add_months(pay, tsp, months[-1], new_months_num)

    session['pay'] = pay
    session['tsp'] = tsp

    config_js = {
        'pay': pay,
        'tsp': tsp,
        'months': months,
        'recommendations': add_recommendations(pay, months),
    }
    context = {
        'config_js': config_js,
        'pay': pay,
        'tsp': tsp,
        'months': months,
        'headers': headers,
    }
    return render_template('budgets.html', **context)


@csrf.exempt
@flask_app.route('/route_insert_row', methods=['POST'])
def route_insert_row():
    pay = session.get('pay', [])
    tsp = session.get('tsp', [])
    months = get_months(pay)
    headers = session.get('headers', [])

    insert = {
        'method': request.form.get('method', ''),
        'type': request.form.get('type', ''),
        'header': request.form.get('header', '').strip(),
        'value': request.form.get('value', '0').strip(),
        'tax': request.form.get('tax', 'false').lower() == 'true',
    }

    pay, headers = insert_row(pay, months, headers, insert)
    pay, tsp = update_months(pay, tsp, months)

    session['pay'] = pay
    session['tsp'] = tsp
    session['headers'] = headers

    config_js = {
        'pay': pay,
        'tsp': tsp,
        'headers': headers,
        'recommendations': add_recommendations(pay, months),
    }
    context = {
        'config_js': config_js,
        'pay': pay,
        'tsp': tsp,
        'months': months,
        'headers': headers,
    }
    return render_template('budgets.html', **context)


@csrf.exempt
@flask_app.route('/route_remove_row', methods=['POST'])
def route_remove_row():
    pay = session.get('pay', [])
    tsp = session.get('tsp', [])
    months = get_months(pay)
    headers = session.get('headers', [])

    header = request.form.get('header', '')

    pay, headers = remove_row(pay, headers, header)
    pay, tsp = update_months(pay, tsp, months)

    session['pay'] = pay
    session['tsp'] = tsp
    session['headers'] = headers

    config_js = {
        'pay': pay,
        'tsp': tsp,
        'headers': headers,
    }
    context = {
        'config_js': config_js,
        'pay': pay,
        'tsp': tsp,
        'months': months,
        'headers': headers,
        'recommendations': add_recommendations(pay, months),
    }
    return render_template('budgets.html', **context)


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


@flask_app.errorhandler(Exception)
def handle_exception(e):
    if e.args and isinstance(e.args[0], dict):
        error_context = e.args[0]
    else:
        traceback.print_exc()
        error_context = {
            "custom_message": str(e),
            "filepath": "",
            "function": "",
            "line": "",
            "error_type": type(e).__name__,
            "error_message": str(e),
        }
    return render_template("errors.html", code=500, error_context=error_context), 500