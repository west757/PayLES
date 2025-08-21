from flask import request, render_template, session, jsonify

from app import flask_app
from app.utils import (
    load_json,
    validate_file,
)
from app.les import (
    validate_les, 
    process_les,
)
from app.budget import (
    build_budget,
    expand_budget,
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
        budget_core = build_budget(les_text)

        for row in budget_core:
            print(row)

        budget = expand_budget(flask_app.config['DEFAULT_MONTHS_NUM'])

        LES_REMARKS = load_json(flask_app.config['LES_REMARKS_JSON'])
        MODALS = load_json(flask_app.config['MODALS_JSON'])

        context = {
            'les_image': les_image,
            'rect_overlay': rect_overlay,
            'budget': budget,
            'LES_REMARKS': LES_REMARKS,
            'MODALS': MODALS,
        }
        return render_template('content.html', **context)
    else:
        return jsonify({'message': message}), 400
    

@flask_app.route('/update_budget', methods=['POST'])
def update_budget():
    months_num = int(request.form.get('months_display', flask_app.config['DEFAULT_MONTHS_NUM']))
    budget = expand_budget(months_num)

    context = {
        'budget': budget,
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
