from decimal import Decimal
from flask import request, render_template, session
import io
import pandas as pd

from app import flask_app
from app.utils import (
    validate_file,
    load_json,
)
from app.les import (
    validate_les, 
    process_les,
)
from app.paydf import (
    build_paydf,
    remove_custom_template_rows, 
    add_custom_template_rows, 
    add_custom_row, 
    expand_paydf,
)


@flask_app.route('/')
def index():
    return render_template('home_group.html')


@flask_app.route('/submit_les', methods=['POST'])
def submit_les():
    DEFAULT_MONTHS_DISPLAY = flask_app.config['DEFAULT_MONTHS_DISPLAY']
    EXAMPLE_LES = flask_app.config['EXAMPLE_LES']
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']

    action = request.form.get('action')
    les_file = request.files.get('home-input')

    if action == "submit-les":
        if not les_file:
            return render_template("home_form.html", message="No file submitted")
        
        valid, message = validate_file(les_file)
        if not valid:
            return render_template("home_form.html", message=message)
        
        valid, message, les_pdf = validate_les(les_file)

    elif action == "submit-example":
        valid, message, les_pdf = validate_les(EXAMPLE_LES)
    else:
        return render_template("home_form.html", message="Unknown action, no LES or example submitted")

    if valid:
        remove_custom_template_rows(PAYDF_TEMPLATE)
        
        les_image, rect_overlay, les_text = process_les(les_pdf)
        paydf = build_paydf(PAYDF_TEMPLATE, les_text)
        paydf, col_headers, row_headers = expand_paydf(PAYDF_TEMPLATE, paydf, DEFAULT_MONTHS_DISPLAY, form={})
        LES_REMARKS = load_json(flask_app.config['LES_REMARKS_JSON'])
        PAYDF_MODALS = load_json(flask_app.config['PAYDF_MODALS_JSON'])

        context = {
            'les_image': les_image,
            'rect_overlay': rect_overlay,
            'paydf': paydf,
            'col_headers': col_headers,
            'row_headers': row_headers,
            'LES_REMARKS': LES_REMARKS,
            'PAYDF_MODALS': PAYDF_MODALS,
        }
        return render_template('paydf_group.html', **context)
    else:
        return render_template("home_form.html", message=message)


@flask_app.route('/update_paydf', methods=['POST'])
def update_paydf():
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    initial_month = session.get('initial_month', None)
    core_list = session.get('core_list', [])

    custom_rows_json = request.form.get('custom_rows', '[]')
    custom_rows =  custom_rows = pd.read_json(io.StringIO(custom_rows_json)).to_dict(orient='records')

    remove_custom_template_rows(PAYDF_TEMPLATE)
    core_custom_list = [row for row in core_list if not any(row[0] == cr['header'] for cr in custom_rows)]

    add_custom_template_rows(PAYDF_TEMPLATE, custom_rows)

    insert_idx = len(core_custom_list) - 6
    for idx, row in enumerate(custom_rows):
        new_row = [row['header'], Decimal("0.00")]
        core_custom_list = core_custom_list[:insert_idx + idx] + [new_row] + core_custom_list[insert_idx + idx:]

    paydf = pd.DataFrame(core_custom_list, columns=["header", initial_month])

    months_display = int(request.form.get('months_display', flask_app.config['DEFAULT_MONTHS_DISPLAY']))

    paydf, col_headers, row_headers = expand_paydf(PAYDF_TEMPLATE, paydf, months_display, form=request.form, custom_rows=custom_rows)

    context = {
        'paydf': paydf,
        'col_headers': col_headers,
        'row_headers': row_headers,
    }
    return render_template('paydf_table.html', **context)


@flask_app.route('/about')
def about():
    return render_template('about.html')


@flask_app.route('/faq')
def faq():
    FAQS = load_json(flask_app.config['FAQ_JSON'])
    return render_template('faq.html', FAQs=FAQS)


@flask_app.route('/resources')
def resources():
    RESOURCES = load_json(flask_app.config['RESOURCES_JSON'])
    return render_template('resources.html', RESOURCES=RESOURCES)


@flask_app.route('/leave_calculator')
def leave_calculator():
    return render_template('leave_calculator.html')
