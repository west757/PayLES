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
    build_options, 
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
    STATIC_FOLDER = flask_app.config['STATIC_FOLDER']
    ALLOWED_EXTENSIONS = flask_app.config['ALLOWED_EXTENSIONS']
    EXAMPLE_LES = flask_app.config['EXAMPLE_LES']
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
        context, les_text = process_les(STATIC_FOLDER, les_pdf)
        context['paydf'], context['col_headers'], context['row_headers'], context['options'], context['months_display'] = build_paydf(les_text)
        context['modals'] = load_json(STATIC_FOLDER, flask_app.config['PAYDF_MODALS_JSON_FILE'])
        return render_template('paydf_group.html', **context)
    else:
        return render_template("home_form.html", message=message)


@flask_app.route('/update_paydf', methods=['POST'])
def update_paydf():
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    months_display = int(request.form.get('months_display', flask_app.config['DEFAULT_MONTHS_DISPLAY']))
    paydf = pd.read_json(io.StringIO(session['paydf_json']))
    options = build_options(PAYDF_TEMPLATE, paydf, form=request.form)

    custom_rows_json = request.form.get('custom_rows', None)
    custom_rows = parse_custom_rows(custom_rows_json)

    remove_custom_template_rows(PAYDF_TEMPLATE)
    add_custom_template_rows(PAYDF_TEMPLATE, custom_rows)
    paydf = add_custom_row(paydf, custom_rows)
    paydf = expand_paydf(PAYDF_TEMPLATE, paydf, options, months_display, custom_rows=custom_rows)

    col_headers = paydf.columns.tolist()
    row_headers = paydf['header'].tolist()

    context = {
        'paydf': paydf,
        'col_headers': col_headers,
        'row_headers': row_headers,
        'options': options,
        'months_display': months_display,
    }
    
    return render_template('paydf_table.html', **context)


@flask_app.route('/about')
def about():
    return render_template('about.html')


@flask_app.route('/faq')
def faq():
    STATIC_FOLDER = flask_app.config['STATIC_FOLDER']
    faqs = load_json(STATIC_FOLDER, flask_app.config['FAQ_JSON_FILE'])
    return render_template('faq.html', faqs=faqs)


@flask_app.route('/resources')
def resources():
    STATIC_FOLDER = flask_app.config['STATIC_FOLDER']
    resources = load_json(STATIC_FOLDER, flask_app.config['RESOURCES_JSON_FILE'])
    return render_template('resources.html', resources=resources)


@flask_app.route('/leave_calculator')
def leave_calculator():
    return render_template('leave_calculator.html')


@flask_app.route('/tsp_calculator')
def tsp_calculator():
    return render_template('tsp_calculator.html')