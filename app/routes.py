from flask import request, render_template, session
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
    parse_custom_rows,
)
from app.forms import (
    HomeForm,
    SettingsForm,
    build_options_form,
)


@flask_app.route('/')
def index():
    home_form = HomeForm()
    return render_template('home_group.html', home_form=home_form)


@flask_app.route('/submit_les', methods=['POST'])
def submit_les():
    DEFAULT_MONTHS_DISPLAY = flask_app.config['DEFAULT_MONTHS_DISPLAY']
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    VARIABLE_TEMPLATE = flask_app.config['VARIABLE_TEMPLATE']

    home_form = HomeForm()
    if not home_form.validate_on_submit():
        return render_template("home_form.html", home_form=home_form, message="Invalid submission")

    if home_form.submit_les.data:
        les_file = home_form.home_input.data
        if not les_file:
            return render_template("home_form.html", home_form=home_form, message="No file submitted")
        valid, message = validate_file(les_file)
        if not valid:
            return render_template("home_form.html", home_form=home_form, message=message)
        valid, message, les_pdf = validate_les(les_file)

    elif home_form.submit_example.data:
        valid, message, les_pdf = validate_les(flask_app.config['EXAMPLE_LES'])
    else:
        return render_template("home_form.html", home_form=home_form, message="Unknown action, no LES or example submitted")

    if valid:
        les_image, rect_overlay, les_text = process_les(les_pdf)
        paydf = build_paydf(PAYDF_TEMPLATE, les_text)
        paydf, col_headers, row_headers = expand_paydf(PAYDF_TEMPLATE, VARIABLE_TEMPLATE, paydf, DEFAULT_MONTHS_DISPLAY, form={})

        LES_REMARKS = load_json(flask_app.config['LES_REMARKS_JSON'])
        PAYDF_MODALS = load_json(flask_app.config['PAYDF_MODALS_JSON'])
        
        options_form = build_options_form(
            PAYDF_TEMPLATE,
            VARIABLE_TEMPLATE,
            paydf,
            col_headers,
            row_headers,
            GRADES=flask_app.config['GRADES'],
            DEPENDENTS_MAX=flask_app.config['DEPENDENTS_MAX'],
            HOME_OF_RECORDS=flask_app.config['HOME_OF_RECORDS'],
            ROTH_TSP_RATE_MAX=flask_app.config['ROTH_TSP_RATE_MAX'],
            SGLI_RATES=flask_app.config['SGLI_RATES'],
            TAX_FILING_TYPES_DEDUCTIONS=flask_app.config['TAX_FILING_TYPES_DEDUCTIONS'],
            TRAD_TSP_RATE_MAX=flask_app.config['TRAD_TSP_RATE_MAX'],
        )

        settings_form = SettingsForm()
        settings_form.months_display.data = str(flask_app.config['DEFAULT_MONTHS_DISPLAY'])

        context = {
            'les_image': les_image,
            'rect_overlay': rect_overlay,
            'paydf': paydf,
            'col_headers': col_headers,
            'row_headers': row_headers,
            'LES_REMARKS': LES_REMARKS,
            'PAYDF_MODALS': PAYDF_MODALS,
            'options_form': options_form,
            'settings_form': settings_form,
        }
        return render_template('paydf_group.html', **context)
    else:
        return render_template("home_form.html", home_form=home_form, message=message)


@flask_app.route('/update_paydf', methods=['POST'])
def update_paydf():
    PAYDF_TEMPLATE = flask_app.config['PAYDF_TEMPLATE']
    VARIABLE_TEMPLATE = flask_app.config['VARIABLE_TEMPLATE']
    initial_month = session.get('initial_month', None)
    months_display = int(request.form.get('months_display', flask_app.config['DEFAULT_MONTHS_DISPLAY']))

    core_custom_list, custom_rows = parse_custom_rows(PAYDF_TEMPLATE, request.form)

    paydf = pd.DataFrame(core_custom_list, columns=["header", initial_month])
    paydf, col_headers, row_headers = expand_paydf(PAYDF_TEMPLATE, VARIABLE_TEMPLATE, paydf, months_display, form=request.form, custom_rows=custom_rows)

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
    return render_template('faq.html', FAQS=FAQS)


@flask_app.route('/resources')
def resources():
    RESOURCES = load_json(flask_app.config['RESOURCES_JSON'])
    return render_template('resources.html', RESOURCES=RESOURCES)


@flask_app.route('/leave_calculator')
def leave_calculator():
    return render_template('leave_calculator.html')
