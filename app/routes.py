from flask import request, render_template, session, jsonify
import pandas as pd

from app import flask_app
from app.utils import (
    load_json,
    validate_file,
)
from app.les import (
    validate_les, 
    process_les,
)
from app.paydf import (
    build_paydf,
    expand_paydf,
)
from app.forms import (
    HomeForm,
    SettingsForm,
)


@flask_app.route('/')
def index():
    home_form = HomeForm()
    return render_template('home.html', home_form=home_form)


@flask_app.route('/submit_les', methods=['POST'])
def submit_les():
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    VARIABLE_TEMPLATE = flask_app.config['VARIABLE_TEMPLATE']

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
        paydf = build_paydf(PAYDF_TEMPLATE, VARIABLE_TEMPLATE, les_text)
        paydf, col_headers, row_headers = expand_paydf(PAYDF_TEMPLATE, VARIABLE_TEMPLATE, paydf, flask_app.config['DEFAULT_MONTHS_DISPLAY'], form={})

        LES_REMARKS = load_json(flask_app.config['LES_REMARKS_JSON'])
        PAYDF_MODALS = load_json(flask_app.config['PAYDF_MODALS_JSON'])

        settings_form = SettingsForm()
        settings_form.months_display.data = str(flask_app.config['DEFAULT_MONTHS_DISPLAY'])

        paydf_rows = paydf.to_dict(orient='records')

        context = {
            'les_image': les_image,
            'rect_overlay': rect_overlay,
            'paydf': paydf_rows,
            'col_headers': col_headers,
            'row_headers': row_headers,
            'LES_REMARKS': LES_REMARKS,
            'PAYDF_MODALS': PAYDF_MODALS,
            'settings_form': settings_form,
        }
        return render_template('content.html', **context)
    else:
        return jsonify({'message': message}), 400
    

@flask_app.route('/update_paydf', methods=['POST'])
def update_paydf():
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    VARIABLE_TEMPLATE = flask_app.config['VARIABLE_TEMPLATE']
    initial_month = session.get('initial_month', None)
    months_display = int(request.form.get('months_display', flask_app.config['DEFAULT_MONTHS_DISPLAY']))
    core_list = session.get('core_list', [])
    paydf = pd.DataFrame(core_list, columns=["header", initial_month])
    paydf, col_headers, row_headers = expand_paydf(PAYDF_TEMPLATE, VARIABLE_TEMPLATE, paydf, months_display, form=request.form)

    context = {
        'paydf': paydf,
        'col_headers': col_headers,
        'row_headers': row_headers,
    }
    return render_template('paydf.html', **context)


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
