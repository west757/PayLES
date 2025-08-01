from flask import Flask
from flask import request, render_template, make_response, jsonify, session
from flask_session import Session
from config import Config
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
from datetime import datetime
from PIL import Image
import pdfplumber
import io
import pandas as pd
import base64

app = Flask(__name__)
app.config.from_object(Config)
Session(app)


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

@app.route('/leave')
def leave():
    return render_template('leave.html')





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
    example_les = app.config['EXAMPLE_LES']

    valid, message, les_pdf = validate_les(example_les)
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
    les_rectangles = app.config['LES_RECTANGLES']
    les_page = les_pdf.pages[0].crop((0, 0, 612, 630))

    context = {}
    context['les_image'], context['rect_overlay'] = create_les_image(les_rectangles, les_page)
    les_text = read_les(les_rectangles, les_page)
    context['paydf'], context['col_headers'], context['row_headers'], context['options'], context['months_display'] = build_paydf(les_text)
    return context


def create_les_image(les_rectangles, les_page):
    les_image_scale = app.config['LES_IMAGE_SCALE']

    temp_image = les_page.to_image(resolution=300).original
    new_width = int(temp_image.width * les_image_scale)
    new_height = int(temp_image.height * les_image_scale)
    resized_image = temp_image.resize((new_width, new_height), Image.LANCZOS)

    img_io = io.BytesIO()
    resized_image.save(img_io, format='PNG')
    img_io.seek(0)
    les_image = base64.b64encode(img_io.read()).decode("utf-8")

    rect_overlay = []
    for rect in les_rectangles.to_dict(orient="records"):
        rect_overlay.append({
            "index": rect["index"],
            "x1": rect["x1"] * les_image_scale,
            "y1": rect["y1"] * les_image_scale,
            "x2": rect["x2"] * les_image_scale,
            "y2": rect["y2"] * les_image_scale,
            "title": rect["title"],
            "modal": rect["modal"],
            "tooltip": rect["tooltip"]
        })
    return les_image, rect_overlay


def read_les(les_rectangles, les_page):
    les_coord_scale = app.config['LES_COORD_SCALE']
    les_text = ["text per rectangle"]

    for i, row in les_rectangles.iterrows():
        x0 = float(row['x1']) * les_coord_scale
        x1 = float(row['x2']) * les_coord_scale
        y0 = float(row['y1']) * les_coord_scale
        y1 = float(row['y2']) * les_coord_scale
        top = min(y0, y1)
        bottom = max(y0, y1)

        les_rect_text = les_page.within_bbox((x0, top, x1, bottom)).extract_text()
        les_text.append(les_rect_text.replace("\n", " ").split())

    return les_text


def build_paydf(les_text):
    months_display = app.config['MONTHS_DISPLAY']

    paydf = initialize_paydf(les_text)
    session['paydf_json'] = paydf.to_json()

    options = build_options(paydf=paydf)
    paydf = expand_paydf(paydf, options, months_display)

    col_headers = paydf.columns.tolist()
    row_headers = paydf['Header'].tolist()

    return paydf, col_headers, row_headers, options, months_display



def initialize_paydf(les_text):
    initial_month = les_text[10][3]
    paydf = pd.DataFrame(columns=["Header", initial_month])

    paydf = add_variables(paydf, les_text)
    paydf = add_entitlements_deductions(paydf, les_text)
    paydf = add_allotments(paydf, les_text)
    paydf = add_calculations(paydf)

    return paydf



def add_variables(paydf, les_text):
    paydf_template = app.config['PAYDF_TEMPLATE']
    var_rows = paydf_template[paydf_template['type'] == 'V']

    for _, row in var_rows.iterrows():
        header = row['header']
        dtype = row['dtype']
        default = row['default']
        value = default

        if header == 'Year':
            value = int('20' + les_text[10][4])
        elif header == 'Grade':
            value = str(les_text[4][1])
        elif header == 'Months in Service':
            paydate = datetime.strptime(les_text[5][2], '%y%m%d')
            lesdate = pd.to_datetime(datetime.strptime((les_text[10][4] + les_text[10][3] + "1"), '%y%b%d'))
            mis = months_in_service(lesdate, paydate)
            value = int(mis)
        elif header == 'Zip Code':
            if les_text[50][2] != "00000":
                value = les_text[50][2]
        elif header == 'MHA Code':
            mhac, mhan = calculate_mha(les_text[50][2])
            value = str(mhac)
        elif header == 'MHA Name':
            value = str(mhan)
        elif header == 'Tax Residency State':
            if les_text[41][1] != "98":
                value = les_text[41][1]
        elif header == 'Federal Filing Status':
            if les_text[26][1] == "S":
                value = "Single"
            elif header == 'M':
                value = "Married"
            elif header == 'H':
                value = "Head of Household"
        elif header == 'State Filing Status':
            if les_text[44][1] == "S":
                value = "Single"
            elif les_text[44][1] == "M":
                value = "Married"
        elif header == 'Dependents':
            value = int(les_text[55][1])
        elif header == 'JFTR':
            if len(les_text[54]) == 2:
                value = les_text[54][1]
        elif header == 'JFTR 2':
            if len(les_text[56]) == 3:
                value = les_text[56][2]
        elif header == 'Combat Zone':
            value = False
        elif header == 'BAQ Type':
            if len(les_text[48]) == 3:
                value = (les_text[48][2])[0] + (les_text[48][2])[1:].lower()
        elif header == 'BAS Type':
            if len(les_text[57]) == 3:
                value = (les_text[57][2])[0] + (les_text[57][2])[1:].lower()
        elif header == 'Traditional TSP Rate':
            ttsp_fields = [int(les_text[62][3]), int(les_text[64][3]), int(les_text[66][3]), int(les_text[68][3])]
            value = next((val for val in ttsp_fields if val > 0), 0)
        elif header == 'Roth TSP Rate':
            rtsp_fields = [int(les_text[71][3]), int(les_text[73][3]), int(les_text[75][3]), int(les_text[77][3])]
            value = next((val for val in rtsp_fields if val > 0), 0)

        value = cast_dtype(value, dtype)
        paydf.loc[len(paydf)] = [header, value]

    return paydf


def add_entitlements_deductions(paydf, les_text):
    paydf_template = app.config['PAYDF_TEMPLATE']

    # Map type to section index and value sign
    type_section = [('E', les_text[11], 1), ('D', les_text[12], -1)]

    for row_type, section, sign in type_section:
        for _, row in paydf_template.iterrows():
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
    paydf_template = app.config['PAYDF_TEMPLATE']

    for _, row in paydf_template.iterrows():
        if row['type'] == 'C':
            header = row['header']
            value = 0

            if header == "Taxable Pay":
                value = calculate_taxablepay(paydf, 1)
            elif header == "Non-Taxable Pay":
                value = calculate_nontaxablepay(paydf, 1)
            elif header == "Total Taxes":
                value = calculate_totaltaxes(paydf, 1)
            elif header == "Gross Pay":
                value = calculate_grosspay(paydf, 1)
            elif header == "Net Pay":
                value = calculate_netpay(paydf, 1)
            elif header == "Difference":
                value = 0

            value = cast_dtype(value, row['dtype'])
            paydf.loc[len(paydf)] = [header, value]
    return paydf



def build_options(paydf=None, form=None):
    paydf_template = app.config['PAYDF_TEMPLATE']
    options = []

    if paydf is not None:
        for _, row in paydf_template.iterrows():

            if not row.get('option', False):
                continue

            header = row['header']
            varname = row['varname']
            required = row.get('required', False)

            if required:
                row_idx = paydf[paydf['Header'] == header].index[0]
                first_month_col = paydf.columns[1]
                value = paydf.at[row_idx, first_month_col]
                options.append([header, value, ""])
            else:
                if header in paydf['Header'].values:
                    row_idx = paydf[paydf['Header'] == header].index[0]
                    first_month_col = paydf.columns[1]
                    value = paydf.at[row_idx, first_month_col]
                    options.append([header, value, ""])


    elif form is not None:
        for _, row in paydf_template.iterrows():
            header = row['header']
            varname = row['varname']
            value_key = f"{varname}_f"
            month_key = f"{varname}_m"
            value = form.get(value_key, "")
            month = form.get(month_key, "")
            options.append([header, value, month])

    return options






def expand_paydf(paydf, options, months_display):
    paydf_template = app.config['PAYDF_TEMPLATE']
    months_short = app.config['MONTHS_SHORT']

    col_headers = paydf.columns.tolist()
    initial_month = col_headers[1]
    month_idx = months_short.index(initial_month)

    for i in range(1, months_display):
        month_idx = (month_idx + 1) % 12
        new_month = months_short[month_idx]

        defaults = []
        for row_idx, row in paydf.iterrows():
            header = row['Header']
            match = paydf_template[paydf_template['header'] == header]
            if not match.empty:
                defaults.append(cast_dtype(match.iloc[0]['default'], match.iloc[0]['dtype']))
            else:
                defaults.append(None)
        paydf[new_month] = defaults

        paydf = update_variables(paydf, new_month, options)
        paydf = update_entitlements_deductions(paydf, new_month, options)
        paydf = update_calculations(paydf, new_month, only_taxable=True)
        paydf = update_allotments(paydf, new_month, options)
        paydf = update_calculations(paydf, new_month, only_taxable=False)

    return paydf




def update_variables(paydf, month, options):
    months_short = app.config['MONTHS_SHORT']
    col_headers = paydf.columns.tolist()
    initial_month = col_headers[1]
    month_idx = months_short.index(initial_month)

    option_headers = set(opt[0] for opt in options)

    for i in range(1, len(col_headers)):
        month_idx = (month_idx + 1) % 12
        for row_idx, row in paydf.iterrows():
            header = row['Header']
            columns = paydf.columns.tolist()
            col_idx = columns.index(month)
            prev_month = paydf.columns[col_idx - 1]
            prev_value = paydf.at[row_idx, prev_month]

            if header in option_headers:
                future_value, future_month = get_option(header, options)
                future_col_idx = columns.index(future_month) if future_month in columns else None
                current_col_idx = columns.index(month)
                if not future_value or not future_month:
                    paydf.at[row_idx, month] = prev_value
                else:
                    if header in {'MHA Code', 'MHA Name'}:
                        if future_col_idx is not None and current_col_idx >= future_col_idx:
                            mhac, mhan = calculate_mha(future_value)
                            paydf.at[row_idx, month] = mhac if header == 'MHA Code' else mhan
                        else:
                            paydf.at[row_idx, month] = prev_value
                    else:
                        if future_col_idx is not None and current_col_idx >= future_col_idx:
                            paydf.at[row_idx, month] = future_value
                        else:
                            paydf.at[row_idx, month] = prev_value
                continue

            if header == 'Year':
                if months_short.index(month) == 0 and months_short.index(prev_month) == 11:
                    paydf.at[row_idx, month] = prev_value + 1
                else:
                    paydf.at[row_idx, month] = prev_value
                continue
            if header == 'Months in Service':
                paydf.at[row_idx, month] = prev_value + 1
                continue
            if header == 'JFTR':
                paydf.at[row_idx, month] = prev_value
                continue
            if header == 'JFTR 2':
                paydf.at[row_idx, month] = prev_value
                continue
            if header == 'BAQ Type':
                paydf.at[row_idx, month] = prev_value
                continue
            if header == 'BAS Type':
                paydf.at[row_idx, month] = prev_value
                continue
            paydf.at[row_idx, month] = prev_value
    return paydf



def update_entitlements_deductions(paydf, month, options):
    paydf_template = app.config['PAYDF_TEMPLATE']
    columns = paydf.columns.tolist()

    for row_idx, row in paydf.iterrows():
        header = row['Header']
        match = paydf_template[paydf_template['header'] == header]
        if match.empty:
            continue
        onetime = bool(match.iloc[0].get('onetime', False))
        standard = bool(match.iloc[0].get('standard', False))

        if onetime:
            paydf.at[row_idx, month] = 0
            continue

        if standard:
            future_value, future_month = get_option(header, options)
            col_idx = columns.index(month)
            prev_month = columns[col_idx - 1]
            prev_value = paydf.at[row_idx, prev_month]
            if not future_value or not future_month:
                paydf.at[row_idx, month] = prev_value
            else:
                future_col_idx = columns.index(future_month) if future_month in columns else None
                current_col_idx = columns.index(month)
                if future_col_idx is not None and current_col_idx >= future_col_idx:
                    paydf.at[row_idx, month] = future_value
                else:
                    paydf.at[row_idx, month] = prev_value
            continue

        if header == 'Base Pay':
            paydf.at[row_idx, month] = calculate_basepay(paydf, row_idx, month)
        elif header == 'BAS':
            paydf.at[row_idx, month] = calculate_bas(paydf, row_idx, month)
        elif header == 'BAH':
            paydf.at[row_idx, month] = calculate_bah(paydf, row_idx, month)
        elif header == 'Federal Taxes':
            paydf.at[row_idx, month] = calculate_federaltaxes(paydf, row_idx, month)
        elif header == 'FICA - Social Security':
            paydf.at[row_idx, month] = calculate_ficasocialsecurity(paydf, row_idx, month)
        elif header == 'FICA - Medicare':
            paydf.at[row_idx, month] = calculate_ficamedicare(paydf, row_idx, month)
        elif header == 'SGLI':
            paydf.at[row_idx, month] = calculate_sgli(paydf, row_idx, month, options)
        elif header == 'State Taxes':
            paydf.at[row_idx, month] = calculate_statetaxes(paydf, row_idx, month)
        elif header == 'Roth TSP':
            paydf.at[row_idx, month] = calculate_rothtsp(paydf, row_idx, month)
        # else: leave as is
    return paydf



def update_allotments(paydf, month, options):
    return paydf



def update_calculations(paydf, month, only_taxable):
    for row_idx, row in paydf.iterrows():
        header = row['Header']
        columns = paydf.columns.tolist()
        col_idx = columns.index(month)
        
        if only_taxable:
            if header == "Taxable Pay":
                paydf.at[row_idx, month] = calculate_taxablepay(paydf, col_idx)
            elif header == "Non-Taxable Pay":
                paydf.at[row_idx, month] = calculate_nontaxablepay(paydf, col_idx)
        else:
            if header == "Total Taxes":
                paydf.at[row_idx, month] = calculate_totaltaxes(paydf, col_idx)
            elif header == "Gross Pay":
                paydf.at[row_idx, month] = calculate_grosspay(paydf, col_idx)
            elif header == "Net Pay":
                paydf.at[row_idx, month] = calculate_netpay(paydf, col_idx)
            elif header == "Difference":
                paydf.at[row_idx, month] = calculate_difference(paydf, col_idx)
    return paydf







def calculate_basepay(paydf, row_idx, month):
    pay_active = app.config['PAY_ACTIVE']

    columns = paydf.columns.tolist()
    col_idx = columns.index(month)
    row_headers = paydf['Header'].tolist()

    grade_row_idx = row_headers.index("Grade")
    mis_row_idx = row_headers.index("Months in Service")

    grade = paydf.at[grade_row_idx, month]

    months_in_service_val = paydf.at[mis_row_idx, month]
    if months_in_service_val is None or months_in_service_val == '':
        months_in_service = 0
    else:
        months_in_service = int(months_in_service_val)

    pay_active_headers = [int(col) for col in pay_active.columns[1:]]
    pay_active_row = pay_active[pay_active["grade"] == grade]
    if pay_active_row.empty:
        return Decimal(0)

    # Find the correct column for months in service
    col_idx = 0
    for i, mis in enumerate(pay_active_headers):
        if months_in_service < mis:
            break
        col_idx = i
    # The column headers in PAY_ACTIVE are strings, so convert to str
    col_name = str(pay_active_headers[col_idx])
    value = pay_active_row[col_name].values[0]
    return round(Decimal(value), 2)




def calculate_bas(paydf, row_idx, month):
    bas_amount = app.config['BAS_AMOUNT']
    row_headers = paydf['Header'].tolist()
    grade_row_idx = row_headers.index("Grade")
    grade = paydf.at[grade_row_idx, month]

    if str(grade).startswith("E"):
        bas_value = bas_amount[1]
    else:
        bas_value = bas_amount[0]
    return round(Decimal(bas_value), 2)



def calculate_bah(paydf, row_idx, month):
    columns = paydf.columns.tolist()
    row_headers = paydf['Header'].tolist()
    # Get MHA code, dependents, and grade for this column
    mha_row_idx = row_headers.index("MHA Code")
    dependents_row_idx = row_headers.index("Dependents")
    grade_row_idx = row_headers.index("Grade")
    mha_code = paydf.at[mha_row_idx, month]
    dependents = paydf.at[dependents_row_idx, month]
    grade = paydf.at[grade_row_idx, month]

    # If MHA code is missing or invalid, return previous value
    if not mha_code or mha_code == "no mha code found":
        col_idx = columns.index(month)
        return paydf.at[row_idx, paydf.columns[col_idx - 1]]

    # Choose correct BAH table based on dependents
    if int(dependents) > 0:
        bah_df = app.config['BAH_WITH_DEPENDENTS']
    else:
        bah_df = app.config['BAH_WITHOUT_DEPENDENTS']

    # Find the row for the MHA code
    bah_row = bah_df[bah_df["MHA"] == mha_code]
    if bah_row.empty or grade not in bah_df.columns:
        col_idx = columns.index(month)
        return paydf.at[row_idx, paydf.columns[col_idx - 1]]

    value = bah_row[grade].values[0]
    return round(Decimal(str(value)), 2)







def calculate_federaltaxes(paydf, row_idx, month):
    standard_deductions = app.config['STANDARD_DEDUCTIONS']
    federal_tax_rate = app.config['FEDERAL_TAX_RATE']

    row_headers = paydf['Header'].tolist()
    # Get taxable pay and federal filing status for this month
    taxable_pay_row_idx = row_headers.index("Taxable Pay")
    filing_status_row_idx = row_headers.index("Federal Filing Status")
    taxable_pay = paydf.at[taxable_pay_row_idx, month]
    filing_status = paydf.at[filing_status_row_idx, month]
    if taxable_pay is None or taxable_pay == '':
        taxable_pay = 0
    if not filing_status:
        return Decimal(0)
    # Annualize taxable pay
    taxable_income = Decimal(taxable_pay) * 12
    # Apply standard deduction
    if filing_status == "Single":
        taxable_income -= standard_deductions[0]
    elif filing_status == "Married":
        taxable_income -= standard_deductions[1]
    elif filing_status == "Head of Household":
        taxable_income -= standard_deductions[2]
    else:
        return Decimal(0)
    taxable_income = max(taxable_income, 0)
    # Get brackets for this status
    brackets = federal_tax_rate[federal_tax_rate['Status'].str.lower() == filing_status.lower()]
    brackets = brackets.sort_values(by='Bracket').reset_index(drop=True)
    tax = Decimal(0)
    for i in range(len(brackets)):
        lower = Decimal(str(brackets.at[i, 'Bracket']))
        rate = Decimal(str(brackets.at[i, 'Rate']))
        if i + 1 < len(brackets):
            upper = Decimal(str(brackets.at[i + 1, 'Bracket']))
        else:
            upper = Decimal('1e12')
        if taxable_income > lower:
            taxable_at_this_rate = min(taxable_income, upper) - lower
            tax += taxable_at_this_rate * rate
    # Convert annual tax to monthly and return as negative
    tax = tax / 12
    return -round(tax, 2)


def calculate_ficasocialsecurity(paydf, row_idx, month):
    row_headers = paydf['Header'].tolist()
    taxable_pay_row_idx = row_headers.index("Taxable Pay")
    taxable_pay = paydf.at[taxable_pay_row_idx, month]
    if taxable_pay is None or taxable_pay == '':
        taxable_pay = 0
    return round(-Decimal(taxable_pay) * app.config['FICA_SOCIALSECURITY_TAX_RATE'], 2)


def calculate_ficamedicare(paydf, row_idx, month):
    row_headers = paydf['Header'].tolist()
    taxable_pay_row_idx = row_headers.index("Taxable Pay")
    taxable_pay = paydf.at[taxable_pay_row_idx, month]
    if taxable_pay is None or taxable_pay == '':
        taxable_pay = 0
    return round(-Decimal(taxable_pay) * app.config['FICA_MEDICARE_TAX_RATE'], 2)




def calculate_sgli(paydf, row_idx, month, options):
    columns = paydf.columns.tolist()
    col_idx = columns.index(month)
    prev_value = paydf.at[row_idx, paydf.columns[col_idx - 1]]

    sgli_value, sgli_month = get_option('SGLI', options)
    if sgli_value is not None and sgli_month and month >= sgli_month:
        return -Decimal(sgli_value)
    return prev_value



def calculate_statetaxes(paydf, row_idx, month):
    state_tax_rate = app.config['STATE_TAX_RATE']

    row_headers = paydf['Header'].tolist()
    # Get taxable pay, state, and filing status for this month
    taxable_pay_row_idx = row_headers.index("Taxable Pay")
    state_row_idx = row_headers.index("Tax Residency State")
    filing_status_row_idx = row_headers.index("State Filing Status")
    taxable_pay = paydf.at[taxable_pay_row_idx, month]
    state = paydf.at[state_row_idx, month]
    filing_status = paydf.at[filing_status_row_idx, month]
    if taxable_pay is None or taxable_pay == '':
        taxable_pay = 0
    if not state or not filing_status:
        return Decimal(0)
    # Annualize taxable pay
    taxable_income = Decimal(taxable_pay) * 12
    # Get state brackets
    state_brackets = state_tax_rate[state_tax_rate['State'] == state]
    if state_brackets.empty:
        return Decimal(0)
    # Select correct columns for filing status
    if filing_status == "Single":
        brackets = state_brackets[['SingleBracket', 'SingleRate']].rename(columns={'SingleBracket': 'Bracket', 'SingleRate': 'Rate'})
    elif filing_status == "Married":
        brackets = state_brackets[['MarriedBracket', 'MarriedRate']].rename(columns={'MarriedBracket': 'Bracket', 'MarriedRate': 'Rate'})
    else:
        return Decimal(0)
    brackets = brackets.sort_values(by='Bracket').reset_index(drop=True)
    tax = Decimal(0)
    for i in range(len(brackets)):
        lower = Decimal(str(brackets.at[i, 'Bracket']))
        rate = Decimal(str(brackets.at[i, 'Rate']))
        if i + 1 < len(brackets):
            upper = Decimal(str(brackets.at[i + 1, 'Bracket']))
        else:
            upper = Decimal('1e12')
        if taxable_income > lower:
            taxable_rate = min(taxable_income, upper) - lower
            tax += taxable_rate * rate
    # Convert annual tax to monthly and return as negative
    tax = tax / 12
    return -round(tax, 2)



def calculate_rothtsp(paydf, row_idx, month):
    columns = paydf.columns.tolist()
    col_idx = columns.index(month)
    return paydf.at[row_idx, paydf.columns[col_idx - 1]]





def calculate_taxablepay(paydf, col_idx):
    paydf_template = app.config['PAYDF_TEMPLATE']
    total = Decimal(0)
    combat_zone_row = paydf[paydf['Header'] == 'Combat Zone']
    combat_zone = None
    if not combat_zone_row.empty:
        combat_zone = combat_zone_row.iloc[0, col_idx]
    for i, row in paydf.iterrows():
        header = row['Header']
        match = paydf_template[paydf_template['header'] == header]
        if match.empty:
            continue
        row_type = match.iloc[0]['type']
        if row_type == 'E':
            if combat_zone == 'Yes' and header == 'Base Pay':
                continue
            if match.iloc[0]['tax'] == 'Y':
                value = row.iloc[col_idx]
                if value is None or value == '':
                    value = 0
                total += Decimal(value)
    return round(total, 2)


def calculate_nontaxablepay(paydf, col_idx):
    paydf_template = app.config['PAYDF_TEMPLATE']
    total = Decimal(0)
    for i, row in paydf.iterrows():
        header = row['Header']
        match = paydf_template[paydf_template['header'] == header]
        if match.empty:
            continue
        row_type = match.iloc[0]['type']
        if row_type == 'E':
            if match.iloc[0]['tax'] == 'N':
                value = row.iloc[col_idx]
                if value is None or value == '':
                    value = 0
                total += Decimal(value)
    return round(total, 2)


def calculate_totaltaxes(paydf, col_idx):
    paydf_template = app.config['PAYDF_TEMPLATE']
    total = Decimal(0)
    for i, row in paydf.iterrows():
        header = row['Header']
        match = paydf_template[paydf_template['header'] == header]
        if match.empty:
            continue
        row_type = match.iloc[0]['type']
        if row_type == 'D':
            if match.iloc[0]['tax'] == 'Y':
                value = row.iloc[col_idx]
                if value is None or value == '':
                    value = 0
                total += Decimal(value)
    return round(total, 2)


def calculate_grosspay(paydf, col_idx):
    paydf_template = app.config['PAYDF_TEMPLATE']
    total = Decimal(0)
    for i, row in paydf.iterrows():
        header = row['Header']
        match = paydf_template[paydf_template['header'] == header]
        if match.empty:
            continue
        row_type = match.iloc[0]['type']
        if row_type == 'E':
            value = row.iloc[col_idx]
            if value is None or value == '':
                value = 0
            try:
                total += Decimal(value)
            except Exception:
                total += Decimal(0)
    return round(total, 2)


def calculate_netpay(paydf, col_idx):
    paydf_template = app.config['PAYDF_TEMPLATE']
    total = Decimal(0)
    for i, row in paydf.iterrows():
        header = row['Header']
        match = paydf_template[paydf_template['header'] == header]
        if match.empty:
            continue
        row_type = match.iloc[0]['type']
        if row_type in ['E', 'D', 'A']:
            value = row.iloc[col_idx]
            if value is None or value == '':
                value = 0
            try:
                total += Decimal(value)
            except Exception:
                total += Decimal(0)
    return round(total, 2)


def calculate_difference(paydf, col_idx):
    netpay_current = calculate_netpay(paydf, col_idx)
    netpay_prev = calculate_netpay(paydf, col_idx - 1)
    try:
        diff = Decimal(netpay_current) - Decimal(netpay_prev)
    except Exception:
        diff = Decimal(0)
    return round(diff, 2)







@app.route('/update_paydf', methods=['POST'])
def update_paydf():
    months_display = int(request.form.get('months_display', 6))

    paydf = pd.read_json(io.StringIO(session['paydf_json']))
    options = build_options(form=request.form)
    paydf = expand_paydf(paydf, options, months_display)

    col_headers = paydf.columns.tolist()
    row_headers = paydf['Header'].tolist()

    context = {
        'paydf': paydf,
        'col_headers': col_headers,
        'row_headers': row_headers,
        'options': options,
        'months_display': months_display,
    }

    return render_template('paydf_table.html', **context)

    #return jsonify({
    #    'paydf_table': render_template('paydf_table.html', **context),
    #    'options_table': render_template('options_table.html', **context),
    #    'settings_table': render_template('settings_table.html', **context),
    #})




@app.route('/export', methods=['POST'])
def export_dataframe():
    return None
    



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
            matches.append(i + n - 1)  # index of last word in match
    return matches


def months_in_service(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def calculate_mha(zipcode):
    mha_zipcodes = app.config['MHA_ZIPCODES']
    if zipcode != "00000" or zipcode != "" or zipcode is not None:
        mha_search = mha_zipcodes[mha_zipcodes.isin([int(zipcode)])].stack()
        mha_search_row = mha_search.index[0][0]
        mhac = mha_zipcodes.loc[mha_search_row, "MHA"]
        mhan = mha_zipcodes.loc[mha_search_row, "MHA_NAME"]
    else:
        mhac = "no mha code found"
        mhan = "no mha name found"
    return mhac, mhan


def get_option(header, options):
    for opt in options:
        if opt[0] == header:
            return opt[1], opt[2]
    return None, None



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