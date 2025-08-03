from flask import Flask
from flask import request, render_template, make_response, jsonify, session
from flask_session import Session
from config import Config
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
from datetime import datetime
from PIL import Image, ImageDraw
import pdfplumber
import io
import pandas as pd
import base64

app = Flask(__name__)
app.config.from_object(Config)
Session(app)



# =========================
# app routes
# =========================

@app.route('/')
def index():
    return render_template('home_group.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/leave_calculator')
def leave_calculator():
    return render_template('leave_calculator.html')

@app.route('/tsp_calculator')
def tsp_calculator():
    return render_template('tsp_calculator.html')



# =========================
# submit, validate, and process LES
# =========================

@app.route('/submit_les', methods=['POST'])
def submit_les():
    les_file = request.files.get('home-input')

    if not les_file:
        return render_template("home_form.html", message="No file submitted")

    valid, message = validate_file(les_file)
    if not valid:
        return render_template("home_form.html", message=message)

    valid, message, les_pdf = validate_les(les_file)
    if valid:
        context = process_les(les_pdf)
        return render_template('paydf_group.html', **context)
    else:
        return render_template("home_form.html", message=message)


@app.route('/submit_example', methods=['POST'])
def submit_example():
    EXAMPLE_LES = app.config['EXAMPLE_LES']

    valid, message, les_pdf = validate_les(EXAMPLE_LES)
    if valid:
        context = process_les(les_pdf)
        return render_template('paydf_group.html', **context)
    else:
        return render_template("home_form.html", message=message)


def validate_les(les_file):
    with pdfplumber.open(les_file) as les_pdf:
        title_crop = les_pdf.pages[0].crop((18, 18, 593, 29))
        title_text = title_crop.extract_text_simple()
        if title_text == "DEFENSE FINANCE AND ACCOUNTING SERVICE MILITARY LEAVE AND EARNINGS STATEMENT":
            return True, None, les_pdf
        else:
            return False, "File is not a valid LES", les_pdf


def process_les(les_pdf):
    LES_RECTANGLES = app.config['LES_RECTANGLES']
    les_page = les_pdf.pages[0].crop((0, 0, 612, 630))

    context = {}
    context['les_image'], context['rect_overlay'] = create_les_image(LES_RECTANGLES, les_page)
    les_text = read_les(LES_RECTANGLES, les_page)
    context['paydf'], context['col_headers'], context['row_headers'], context['options'], context['months_display'] = build_paydf(les_text)
    return context


def create_les_image(les_rectangles, les_page):
    LES_IMAGE_SCALE = app.config['LES_IMAGE_SCALE']

    temp_image = les_page.to_image(resolution=300).original
    new_width = int(temp_image.width * LES_IMAGE_SCALE)
    new_height = int(temp_image.height * LES_IMAGE_SCALE)
    resized_image = temp_image.resize((new_width, new_height), Image.LANCZOS)

    #create whiteout rectangle over SSN
    whiteout_coords = (710, 165, 980, 220)
    draw = ImageDraw.Draw(resized_image)
    x1 = int(whiteout_coords[0] * LES_IMAGE_SCALE)
    y1 = int(whiteout_coords[1] * LES_IMAGE_SCALE)
    x2 = int(whiteout_coords[2] * LES_IMAGE_SCALE)
    y2 = int(whiteout_coords[3] * LES_IMAGE_SCALE)
    draw.rectangle([x1, y1, x2, y2], fill="white")

    img_io = io.BytesIO()
    resized_image.save(img_io, format='PNG')
    img_io.seek(0)
    les_image = base64.b64encode(img_io.read()).decode("utf-8")

    rect_overlay = []
    for rect in les_rectangles.to_dict(orient="records"):
        rect_overlay.append({
            "index": rect["index"],
            "x1": rect["x1"] * LES_IMAGE_SCALE,
            "y1": rect["y1"] * LES_IMAGE_SCALE,
            "x2": rect["x2"] * LES_IMAGE_SCALE,
            "y2": rect["y2"] * LES_IMAGE_SCALE,
            "title": rect["title"],
            "modal": rect["modal"],
            "tooltip": rect["tooltip"]
        })
    return les_image, rect_overlay


def read_les(les_rectangles, les_page):
    LES_COORD_SCALE = app.config['LES_COORD_SCALE']
    les_text = ["text per rectangle"]

    for i, row in les_rectangles.iterrows():
        x0 = float(row['x1']) * LES_COORD_SCALE
        x1 = float(row['x2']) * LES_COORD_SCALE
        y0 = float(row['y1']) * LES_COORD_SCALE
        y1 = float(row['y2']) * LES_COORD_SCALE
        top = min(y0, y1)
        bottom = max(y0, y1)

        les_rect_text = les_page.within_bbox((x0, top, x1, bottom)).extract_text()
        les_text.append(les_rect_text.replace("\n", " ").split())

    return les_text



# =========================
# initialize and build paydf
# =========================

def build_paydf(les_text):
    DEFAULT_MONTHS_DISPLAY = app.config['DEFAULT_MONTHS_DISPLAY']

    paydf = initialize_paydf(les_text)
    session['paydf_json'] = paydf.to_json()

    options = build_options(paydf=paydf)

    paydf = expand_paydf(paydf, options, DEFAULT_MONTHS_DISPLAY)

    col_headers = paydf.columns.tolist()
    row_headers = paydf['header'].tolist()

    return paydf, col_headers, row_headers, options, DEFAULT_MONTHS_DISPLAY


def initialize_paydf(les_text):
    initial_month = les_text[8][3]
    paydf = pd.DataFrame(columns=["header", initial_month])

    paydf = add_variables(paydf, les_text)
    paydf = add_entitlements(paydf, les_text)
    paydf = add_deductions(paydf, les_text)
    paydf = add_allotments(paydf, les_text)
    paydf = add_calculations(paydf)

    return paydf


def add_variables(paydf, les_text):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'V']

    for _, row in var_rows.iterrows():
        header = row['header']
        dtype = row['dtype']
        default = row['default']
        value = default

        if header == 'Year':
            value = int('20' + les_text[8][4])
        elif header == 'Grade':
            value = str(les_text[2][1])
        elif header == 'Months in Service':
            paydate = datetime.strptime(les_text[3][2], '%y%m%d')
            lesdate = pd.to_datetime(datetime.strptime((les_text[8][4] + les_text[8][3] + "1"), '%y%b%d'))
            mis = months_in_service(lesdate, paydate)
            value = int(mis)
        elif header == 'Zip Code':
            if les_text[48][2] != "00000":
                value = les_text[48][2]
        elif header == 'Military Housing Area':
            value = calculate_mha(les_text[48][2])
        elif header == 'Tax Residency State':
            if les_text[39][1] != "98":
                value = les_text[39][1]
        elif header == 'Federal Filing Status':
            if les_text[24][1] == "S":
                value = "Single"
            elif header == 'M':
                value = "Married"
            elif header == 'H':
                value = "Head of Household"
        elif header == 'State Filing Status':
            if les_text[42][1] == "S":
                value = "Single"
            elif les_text[42][1] == "M":
                value = "Married"
        elif header == 'Dependents':
            value = int(les_text[53][1])
        elif header == 'Combat Zone':
            value = "No"
        elif header == 'Traditional TSP Rate':
            ttsp_fields = [int(les_text[60][3]), int(les_text[62][3]), int(les_text[64][3]), int(les_text[66][3])]
            value = next((val for val in ttsp_fields if val > 0), 0)
        elif header == 'Roth TSP Rate':
            rtsp_fields = [int(les_text[69][3]), int(les_text[71][3]), int(les_text[73][3]), int(les_text[75][3])]
            value = next((val for val in rtsp_fields if val > 0), 0)

        value = cast_dtype(value, dtype)
        paydf.loc[len(paydf)] = [header, value]

    return paydf


def add_entitlements(paydf, les_text):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'E']

    # Map type to section index and value sign
    type_section = [('E', les_text[9], 1), ('D', les_text[10], -1)]

    for row_type, section, sign in type_section:
        for _, row in var_rows.iterrows():
            if row['type'] == row_type:
                value = None
                found = False
                short = str(row['shortname'])
                matches = find_multiword_matches(section, short)

                for idx in matches:
                    for j in range(idx + 1, len(section)):
                        s = section[j]
                        is_num = s.replace('.', '', 1).replace('-', '', 1).isdigit() or (s.startswith('-') and s[1:].replace('.', '', 1).isdigit())
                        if is_num:
                            v = Decimal(section[j])
                            value = sign * round(abs(v), 2)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    if bool(row['required']):
                        value = row['default']
                    else:
                        continue

                value = cast_dtype(value, row['dtype'])
                paydf.loc[len(paydf)] = [row['header'], value]

    return paydf


def add_deductions(paydf, les_text):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'D']

    # Map type to section index and value sign
    type_section = [('E', les_text[9], 1), ('D', les_text[10], -1)]

    for row_type, section, sign in type_section:
        for _, row in var_rows.iterrows():
            if row['type'] == row_type:
                value = None
                found = False
                short = str(row['shortname'])
                matches = find_multiword_matches(section, short)

                for idx in matches:
                    for j in range(idx + 1, len(section)):
                        s = section[j]
                        is_num = s.replace('.', '', 1).replace('-', '', 1).isdigit() or (s.startswith('-') and s[1:].replace('.', '', 1).isdigit())
                        if is_num:
                            v = Decimal(section[j])
                            value = sign * round(abs(v), 2)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    if bool(row['required']):
                        value = row['default']
                    else:
                        continue

                value = cast_dtype(value, row['dtype'])
                paydf.loc[len(paydf)] = [row['header'], value]

    return paydf


def add_allotments(paydf, les_text):
    return paydf


def add_calculations(paydf):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    var_rows = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'C']

    taxable, nontaxable = calculate_taxed_income(paydf, 1)

    for _, row in var_rows.iterrows():
        header = row['header']
        value = 0

        if header == "Taxable Income":
            value = taxable
        elif header == "Non-Taxable Income":
            value = nontaxable
        elif header == "Total Taxes":
            value = calculate_total_taxes(paydf, 1)
        elif header == "Gross Pay":
            value = calculate_gross_pay(paydf, 1)
        elif header == "Net Pay":
            value = calculate_net_pay(paydf, 1)
        elif header == "Difference":
            value = 0

        value = cast_dtype(value, row['dtype'])
        paydf.loc[len(paydf)] = [header, value]
    return paydf



# =========================
# build options
# =========================

def build_options(paydf, form=None):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    MONTHS_SHORT = app.config['MONTHS_SHORT']
    options = []

    def add_option(header, varname):
        if form:
            value = form.get(f"{varname}_f", "")
            month = form.get(f"{varname}_m", "")
        else:
            row_idx = paydf[paydf['header'] == header].index[0]
            first_month_col = paydf.columns[1]
            value = paydf.at[row_idx, first_month_col]
            first_month_idx = MONTHS_SHORT.index(first_month_col)
            month = MONTHS_SHORT[(first_month_idx + 1) % 12]

        options.append([header, value, month])


    for _, row in PAYDF_TEMPLATE.iterrows():
        if not row.get('option', False):
            continue

        header = row['header']
        varname = row['varname']
        required = bool(row['required'])

        if required:
            add_option(header, varname)
        else:
            if header in paydf['header'].values:
                add_option(header, varname)

    return options



# =========================
# expand paydf
# =========================

def expand_paydf(paydf, options, months_display):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    MONTHS_SHORT = app.config['MONTHS_SHORT']
    initial_month = paydf.columns[1]
    month_idx = MONTHS_SHORT.index(initial_month)

    for i in range(1, months_display):
        month_idx = (month_idx + 1) % 12
        new_month = MONTHS_SHORT[month_idx]

        defaults = []
        for _, row in paydf.iterrows():
            header = row['header']
            match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]
            defaults.append(cast_dtype(match.iloc[0]['default'], match.iloc[0]['dtype']))

        paydf[new_month] = defaults

        paydf = update_variables(paydf, new_month, options)
        paydf = update_entitlements(paydf, new_month, options)
        paydf = update_calculations(paydf, new_month, only_taxable=True)
        paydf = update_deductions(paydf, new_month, options)
        paydf = update_allotments(paydf, new_month, options)
        paydf = update_calculations(paydf, new_month, only_taxable=False)

    return paydf


def update_variables(paydf, month, options):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'V']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    MONTHS_SHORT = app.config['MONTHS_SHORT']
    option_headers = set(opt[0] for opt in options)

    for row_idx, row in rows.iterrows():
        header = row['header']
        columns = paydf.columns.tolist()
        col_idx = columns.index(month)
        prev_month = paydf.columns[col_idx - 1]
        prev_value = paydf.at[row_idx, prev_month]

        if header in option_headers:
            future_value, future_month = get_option(header, options)
            if future_month in columns:
                future_col_idx = columns.index(future_month)
                current_col_idx = columns.index(month)
                if current_col_idx >= future_col_idx:
                    paydf.at[row_idx, month] = future_value
                else:
                    paydf.at[row_idx, month] = prev_value
            else:
                paydf.at[row_idx, month] = prev_value
            continue

        elif header == 'Year':
            if MONTHS_SHORT.index(month) == 0 and MONTHS_SHORT.index(prev_month) == 11:
                paydf.at[row_idx, month] = prev_value + 1
            else:
                paydf.at[row_idx, month] = prev_value
            continue

        elif header == 'Months in Service':
            paydf.at[row_idx, month] = prev_value + 1
            continue

        elif header == 'Military Housing Area':
            zip_code = paydf.at[row_idx - 1, month]
            paydf.at[row_idx, month] = calculate_mha(zip_code)
            continue

    return paydf


def update_entitlements(paydf, month, options):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'E']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    columns = paydf.columns.tolist()

    for row_idx, row in rows.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]
        
        onetime = bool(match.iloc[0].get('onetime', False))
        standard = bool(match.iloc[0].get('standard', False))

        if onetime:
            paydf.at[row_idx, month] = 0
            continue

        elif standard:
            future_value, future_month = get_option(header, options)
            col_idx = columns.index(month)
            prev_month = columns[col_idx - 1]
            prev_value = paydf.at[row_idx, prev_month]

            if future_month in columns:
                future_col_idx = columns.index(future_month)
                current_col_idx = columns.index(month)

                if future_col_idx is not None and current_col_idx >= future_col_idx:
                    paydf.at[row_idx, month] = future_value
                else:
                    paydf.at[row_idx, month] = prev_value
            else:
                paydf.at[row_idx, month] = prev_value
            continue

        elif header == 'Base Pay':
            paydf.at[row_idx, month] = calculate_base_pay(paydf, month)
        elif header == 'BAS':
            paydf.at[row_idx, month] = calculate_bas(paydf, month)
        elif header == 'BAH':
            paydf.at[row_idx, month] = calculate_bah(paydf, month)

    return paydf


def update_deductions(paydf, month, options):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'D']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    columns = paydf.columns.tolist()

    for row_idx, row in rows.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]
        
        onetime = bool(match.iloc[0].get('onetime', False))
        standard = bool(match.iloc[0].get('standard', False))

        if onetime:
            paydf.at[row_idx, month] = 0
            continue

        elif standard:
            future_value, future_month = get_option(header, options)
            col_idx = columns.index(month)
            prev_month = columns[col_idx - 1]
            prev_value = paydf.at[row_idx, prev_month]

            if future_month in columns:
                future_col_idx = columns.index(future_month)
                current_col_idx = columns.index(month)

                if future_col_idx is not None and current_col_idx >= future_col_idx:
                    paydf.at[row_idx, month] = future_value
                else:
                    paydf.at[row_idx, month] = prev_value
            else:
                paydf.at[row_idx, month] = prev_value
            continue

        elif header == 'Federal Taxes':
            paydf.at[row_idx, month] = calculate_federal_taxes(paydf, month)
        elif header == 'FICA - Social Security':
            paydf.at[row_idx, month] = calculate_fica_social_security(paydf, month)
        elif header == 'FICA - Medicare':
            paydf.at[row_idx, month] = calculate_fica_medicare(paydf, month)
        elif header == 'SGLI':
            paydf.at[row_idx, month] = calculate_sgli(paydf, row_idx, month, options)
        elif header == 'State Taxes':
            paydf.at[row_idx, month] = calculate_state_taxes(paydf, month)
        elif header == 'Traditional TSP':
            paydf.at[row_idx, month] = calculate_traditional_tsp(paydf, month)
        elif header == 'Roth TSP':
            paydf.at[row_idx, month] = calculate_roth_tsp(paydf, month)

    return paydf


def update_allotments(paydf, month, options):
    return paydf


def update_calculations(paydf, month, only_taxable):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'C']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    columns = paydf.columns.tolist()
    col_idx = columns.index(month)

    for row_idx, row in rows.iterrows():
        header = row['header']

        if only_taxable:
            taxable, nontaxable = calculate_taxed_income(paydf, col_idx)
            if header == "Taxable Income":
                paydf.at[row_idx, month] = taxable
            elif header == "Non-Taxable Income":
                paydf.at[row_idx, month] = nontaxable
        else:
            if header == "Total Taxes":
                paydf.at[row_idx, month] = calculate_total_taxes(paydf, col_idx)
            elif header == "Gross Pay":
                paydf.at[row_idx, month] = calculate_gross_pay(paydf, col_idx)
            elif header == "Net Pay":
                paydf.at[row_idx, month] = calculate_net_pay(paydf, col_idx)
            elif header == "Difference":
                paydf.at[row_idx, month] = calculate_difference(paydf, col_idx)
    return paydf



# =========================
# calculate non-standard rows
# =========================

def calculate_base_pay(paydf, month):
    PAY_ACTIVE = app.config['PAY_ACTIVE']
    row_headers = paydf['header'].tolist()
    grade = paydf.at[row_headers.index("Grade"), month]
    months_in_service = paydf.at[row_headers.index("Months in Service"), month]
    pay_active_headers = [int(col) for col in PAY_ACTIVE.columns[1:]]
    pay_active_row = PAY_ACTIVE[PAY_ACTIVE["grade"] == grade]

    col_idx = 0
    for i, mis in enumerate(pay_active_headers):
        if months_in_service < mis:
            break
        col_idx = i

    col_name = str(pay_active_headers[col_idx])
    value = pay_active_row[col_name].values[0]

    return round(Decimal(value), 2)


def calculate_bas(paydf, month):
    BAS_AMOUNT = app.config['BAS_AMOUNT']
    row_headers = paydf['header'].tolist()
    grade = paydf.at[row_headers.index("Grade"), month]

    if str(grade).startswith("E"):
        bas_value = BAS_AMOUNT[1]
    else:
        bas_value = BAS_AMOUNT[0]

    return round(Decimal(bas_value), 2)


def calculate_bah(paydf, month):
    row_headers = paydf['header'].tolist()
    grade = paydf.at[row_headers.index("Grade"), month]
    military_housing_area = paydf.at[row_headers.index("Military Housing Area"), month]
    dependents = paydf.at[row_headers.index("Dependents"), month]

    if int(dependents) > 0:
        BAH_DF = app.config['BAH_WITH_DEPENDENTS']
    else:
        BAH_DF = app.config['BAH_WITHOUT_DEPENDENTS']

    if military_housing_area == "Not Found":
            return Decimal(0)

    bah_row = BAH_DF[BAH_DF["mha"] == military_housing_area]

    value = bah_row[grade].values[0]
    return round(Decimal(str(value)), 2)


def calculate_federal_taxes(paydf, month):
    STANDARD_DEDUCTIONS = app.config['STANDARD_DEDUCTIONS']
    FEDERAL_TAX_RATE = app.config['FEDERAL_TAX_RATE']
    row_headers = paydf['header'].tolist()
    filing_status = paydf.at[row_headers.index("Federal Filing Status"), month]
    taxable_income = paydf.at[row_headers.index("Taxable Income"), month]
    taxable_income = Decimal(taxable_income) * 12
    tax = Decimal(0)

    if filing_status == "Single":
        taxable_income -= STANDARD_DEDUCTIONS[0]
    elif filing_status == "Married":
        taxable_income -= STANDARD_DEDUCTIONS[1]
    elif filing_status == "Head of Household":
        taxable_income -= STANDARD_DEDUCTIONS[2]
    
    taxable_income = max(taxable_income, 0)
    brackets = FEDERAL_TAX_RATE[FEDERAL_TAX_RATE['Status'].str.lower() == filing_status.lower()]
    brackets = brackets.sort_values(by='Bracket').reset_index(drop=True)

    for i in range(len(brackets)):
        lower_bracket = Decimal(str(brackets.at[i, 'Bracket']))
        rate = Decimal(str(brackets.at[i, 'Rate']))

        if i + 1 < len(brackets):
            upper_bracket = Decimal(str(brackets.at[i + 1, 'Bracket']))
        else:
            upper_bracket = Decimal('1e12')

        if taxable_income > lower_bracket:
            taxable_at_rate = min(taxable_income, upper_bracket) - lower_bracket
            tax += taxable_at_rate * rate

    tax = tax / 12
    return -round(tax, 2)


def calculate_fica_social_security(paydf, month):
    FICA_SOCIALSECURITY_TAX_RATE = app.config['FICA_SOCIALSECURITY_TAX_RATE']
    row_headers = paydf['header'].tolist()
    taxable_income = paydf.at[row_headers.index("Taxable Income"), month]

    return round(-Decimal(taxable_income) * FICA_SOCIALSECURITY_TAX_RATE, 2)


def calculate_fica_medicare(paydf, month):
    FICA_MEDICARE_TAX_RATE = app.config['FICA_MEDICARE_TAX_RATE']
    row_headers = paydf['header'].tolist()
    taxable_income = paydf.at[row_headers.index("Taxable Income"), month]

    return round(-Decimal(taxable_income) * FICA_MEDICARE_TAX_RATE, 2)


def calculate_sgli(paydf, row_idx, month, options):
    columns = paydf.columns.tolist()
    col_idx = columns.index(month)
    prev_value = paydf.at[row_idx, paydf.columns[col_idx - 1]]
    sgli_value, sgli_month = get_option('SGLI', options)

    if month >= sgli_month:
        return -abs(Decimal(sgli_value))
    
    return -abs(Decimal(prev_value))


def calculate_state_taxes(paydf, month):
    STATE_TAX_RATE = app.config['STATE_TAX_RATE']
    row_headers = paydf['header'].tolist()
    state = paydf.at[row_headers.index("Tax Residency State"), month]
    state_brackets = STATE_TAX_RATE[STATE_TAX_RATE['state'] == state]
    filing_status = paydf.at[row_headers.index("State Filing Status"), month]
    taxable_income = paydf.at[row_headers.index("Taxable Income"), month]
    taxable_income = Decimal(taxable_income) * 12
    tax = Decimal(0)

    if filing_status == "Single":
        brackets = state_brackets[['single_bracket', 'single_rate']].rename(columns={'single_bracket': 'bracket', 'single_rate': 'rate'})
    elif filing_status == "Married":
        brackets = state_brackets[['married_bracket', 'married_rate']].rename(columns={'married_bracket': 'bracket', 'married_rate': 'rate'})

    brackets = brackets.sort_values(by='bracket').reset_index(drop=True)
    
    for i in range(len(brackets)):
        lower_bracket = Decimal(str(brackets.at[i, 'bracket']))
        rate = Decimal(str(brackets.at[i, 'rate']))

        if i + 1 < len(brackets):
            upper_bracket = Decimal(str(brackets.at[i + 1, 'bracket']))
        else:
            upper_bracket = Decimal('1e12')

        if taxable_income > lower_bracket:
            taxable_rate = min(taxable_income, upper_bracket) - lower_bracket
            tax += taxable_rate * rate

    tax = tax / 12
    return -round(tax, 2)


def calculate_traditional_tsp(paydf, month):
    row_headers = paydf['header'].tolist()
    base_pay = paydf.at[row_headers.index("Base Pay"), month]
    tsp_rate = paydf.at[row_headers.index("Traditional TSP Rate"), month]

    value = Decimal(base_pay) * Decimal(tsp_rate) / Decimal(100)

    return -round(value, 2)


def calculate_roth_tsp(paydf, month):
    row_headers = paydf['header'].tolist()
    base_pay = paydf.at[row_headers.index("Base Pay"), month]
    tsp_rate = paydf.at[row_headers.index("Roth TSP Rate"), month]

    value = Decimal(base_pay) * Decimal(tsp_rate) / Decimal(100)

    return -round(value, 2)



# =========================
# calculation functions
# =========================

def calculate_taxed_income(paydf, col_idx):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    combat_zone_row = paydf[paydf['header'] == 'Combat Zone']
    combat_zone = combat_zone_row.iloc[0, col_idx] if not combat_zone_row.empty else "No"
    is_combat_zone = str(combat_zone).strip().upper() == 'YES'
    taxable = Decimal(0)
    nontaxable = Decimal(0)

    for _, row in paydf.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]

        row_type = match.iloc[0]['type']

        if row_type == 'E':
            value = row.iloc[col_idx]

            if value is None or value == '':
                value = Decimal(0)
            else:
                try:
                    value = Decimal(str(value))
                except Exception:
                    value = Decimal(0)

            tax_flag = match.iloc[0]['tax']

            if is_combat_zone:
                nontaxable += value
            else:
                if tax_flag:
                    taxable += value
                else:
                    nontaxable += value

    if is_combat_zone:
        taxable = Decimal(0)

    return round(taxable, 2), round(nontaxable, 2)


def calculate_total_taxes(paydf, col_idx):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'D']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    total = Decimal(0)

    for _, row in rows.iterrows():
        header = row['header']
        match = PAYDF_TEMPLATE[PAYDF_TEMPLATE['header'] == header]
        tax_flag = match.iloc[0]['tax']

        if tax_flag:
            value = row.iloc[col_idx]
            value = Decimal(str(value))
            total += value

    return round(total, 2)


def calculate_gross_pay(paydf, col_idx):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'E']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    total = Decimal(0)

    for _, row in rows.iterrows():
        value = row.iloc[col_idx]
        total += Decimal(value)

    return round(total, 2)


def calculate_net_pay(paydf, col_idx):
    PAYDF_TEMPLATE = app.config['PAYDF_TEMPLATE']
    row_headers = PAYDF_TEMPLATE[PAYDF_TEMPLATE['type'] == 'D']['header'].tolist()
    rows = paydf[paydf['header'].isin(row_headers)]
    row_headers = paydf['header'].tolist()
    gross_pay_current = paydf.iloc[row_headers.index("Gross Pay"), col_idx]
    total = Decimal(0)

    for i, row in rows.iterrows():
        value = row.iloc[col_idx]
        total += Decimal(value)

    total = gross_pay_current + total

    return round(total, 2)


def calculate_difference(paydf, col_idx):
    row_headers = paydf['header'].tolist()
    netpay_current = paydf.iloc[row_headers.index("Net Pay"), col_idx]
    netpay_prev = paydf.iloc[row_headers.index("Net Pay"), col_idx - 1]

    difference = Decimal(netpay_current) - Decimal(netpay_prev)
    return round(difference, 2)



# =========================
# update paydf
# =========================

@app.route('/update_paydf', methods=['POST'])
def update_paydf():
    months_display = int(request.form.get('months_display', 6))

    paydf = pd.read_json(io.StringIO(session['paydf_json']))
    options = build_options(paydf, form=request.form)
    paydf = expand_paydf(paydf, options, months_display)

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



# =========================
# helper functions
# =========================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def validate_file(file):
    if file.filename == '':
        return False, "No file submitted"
    if not allowed_file(file.filename):
        return False, "Invalid file type, only PDFs are accepted"
    return True, ""


def cast_dtype(value, dtype):
    if dtype == 'int':
        return int(value)
    elif dtype == 'str':
        return str(value)
    elif dtype == 'Decimal':
        return Decimal(value)
    elif dtype == 'bool':
        return bool(value)
    return value


def find_multiword_matches(section, shortname):
    short_words = shortname.split()
    n = len(short_words)
    matches = []

    for i in range(len(section) - n + 1):
        candidate = ' '.join(section[i:i+n])
        if candidate == shortname:
            matches.append(i + n - 1)

    return matches


def months_in_service(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def calculate_mha(zipcode):
    MHA_ZIPCODES = app.config['MHA_ZIPCODES']

    if zipcode != "00000" and zipcode != "" and zipcode != "Not Found":
        mha_search = MHA_ZIPCODES[MHA_ZIPCODES.isin([int(zipcode)])].stack()
        mha_search_row = mha_search.index[0][0]
        mha = MHA_ZIPCODES.loc[mha_search_row, "mha"]
    else:
        mha = "Not Found"

    return mha


def get_option(header, options):
    for opt in options:
        if opt[0] == header:
            return opt[1], opt[2]
    return None, None



# =========================
# flask helper functions
# =========================

@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return 'File is too large', 413


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)