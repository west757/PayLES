from multiprocessing import context
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
    parse_custom_rows,
)


@flask_app.route('/')
def index():
    return render_template('home_group.html')


@flask_app.route('/submit_les', methods=['POST'])
def submit_les():
    ALLOWED_EXTENSIONS = flask_app.config['ALLOWED_EXTENSIONS']
    DEFAULT_MONTHS_DISPLAY = flask_app.config['DEFAULT_MONTHS_DISPLAY']
    EXAMPLE_LES = flask_app.config['EXAMPLE_LES']
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']

    action = request.form.get('action')
    les_file = request.files.get('home-input')

    if action == "submit-les":
        if not les_file:
            return render_template("home_form.html", message="No file submitted")
        
        valid, message = validate_file(les_file, ALLOWED_EXTENSIONS)
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
        les_remarks = load_json(flask_app.config['LES_REMARKS_JSON'])
        modals = load_json(flask_app.config['PAYDF_MODALS_JSON'])

        context = {
            'les_image': les_image,
            'rect_overlay': rect_overlay,
            'paydf': paydf,
            'col_headers': col_headers,
            'row_headers': row_headers,
            'les_remarks': les_remarks,
            'modals': modals,
        }
        return render_template('paydf_group.html', **context)
    else:
        return render_template("home_form.html", message=message)


@flask_app.route('/update_paydf', methods=['POST'])
def update_paydf():
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    core_list = session.get('core_list', [])
    initial_month = session.get('initial_month', None)

    remove_custom_template_rows(PAYDF_TEMPLATE)
    paydf = pd.DataFrame(core_list, columns=["header", initial_month])

    months_display = int(request.form.get('months_display', flask_app.config['DEFAULT_MONTHS_DISPLAY']))
    
    custom_rows_json = request.form.get('custom_rows', None)
    custom_rows = parse_custom_rows(custom_rows_json)
    add_custom_template_rows(PAYDF_TEMPLATE, custom_rows)
    paydf = add_custom_row(paydf, custom_rows)

    paydf, col_headers, row_headers = expand_paydf(PAYDF_TEMPLATE, paydf, months_display, form=request.form)

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
    faqs = load_json(flask_app.config['FAQ_JSON'])
    return render_template('faq.html', faqs=faqs)


@flask_app.route('/resources')
def resources():
    resources = load_json(flask_app.config['RESOURCES_JSON'])
    return render_template('resources.html', resources=resources)


@flask_app.route('/leave_calculator')
def leave_calculator():
    return render_template('leave_calculator.html')
