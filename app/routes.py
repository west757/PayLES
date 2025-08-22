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

        session['budget'] = budget

        LES_REMARKS = load_json(flask_app.config['LES_REMARKS_JSON'])
        MODALS = load_json(flask_app.config['MODALS_JSON'])

        context = {
            'les_image': les_image,
            'rect_overlay': rect_overlay,
            'budget': convert_numpy_types(budget),
            'month_headers': month_headers,
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
    row_header = request.form.get('row_header', '')
    col_month = request.form.get('col_month', '')
    value = request.form.get('value', 0)
    repeat = request.form.get('repeat', False)

    if col_month in month_headers:
        idx = month_headers.index(col_month)
        months_num = len(month_headers) - idx
        budget, month_headers = build_months(all_rows=False, budget=budget, prev_month=col_month, months_num=months_num, row_header=row_header, col_month=col_month, value=value, repeat=repeat)

    session['budget'] = budget

    context = {
        'budget': convert_numpy_types(budget),
        'month_headers': month_headers,
    }
    return render_template('budget.html', **context)


@csrf.exempt
@flask_app.route('/update_months', methods=['POST'])
def update_months():
    next_months_num = int(request.form.get('months_num', flask_app.config['DEFAULT_MONTHS_NUM']))
    budget = session.get('budget', [])
    month_headers = get_month_headers(budget)
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

    context = {
        'budget': convert_numpy_types(budget),
        'month_headers': month_headers,
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
