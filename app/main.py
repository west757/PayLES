from flask import Flask
from flask import request, render_template, make_response, jsonify, session, send_file, flash
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
    return render_template('index.html')

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

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/404')
def page404():
    return render_template('404.html')





@app.route('/submit_les', methods=['POST'])
def submit_les():
    les_file = request.files.get('submit-input')
    if not les_file:
        return render_template("submit.html", error="No file part in form")

    valid, message = validate_file(les_file)
    if not valid:
        return render_template("submit.html", error=message)

    with pdfplumber.open(les_file) as les_pdf:
        title_crop = les_pdf.pages[0].crop((18, 18, 593, 29))
        title_text = title_crop.extract_text_simple()
        les_pdf.close()
        if title_text == "DEFENSE FINANCE AND ACCOUNTING SERVICE MILITARY LEAVE AND EARNINGS STATEMENT":
            read_les(les_file)
            return render_template('les.html')
        else:
            return render_template("submit.html", error="File is not a valid LES")




@app.route('/submit_example', methods=['POST'])
def submit_example():
    read_les(app.config['EXAMPLE_LES'])
    return render_template('les.html')



@app.route('/read_les', methods=['POST'])
def read_les(les_file):
    reset_session_defaults()

    with pdfplumber.open(les_file) as les_pdf:
        les_page = les_pdf.pages[0].crop((0, 0, 612, 630))
        les_text = ["text per rectangle"]

        #create image
        temp_image = les_page.to_image(resolution=300).original
        new_width = int(temp_image.width * app.config['LES_IMAGE_SCALE'])
        new_height = int(temp_image.height * app.config['LES_IMAGE_SCALE'])
        resized_image = temp_image.resize((new_width, new_height), Image.LANCZOS)

        img_io = io.BytesIO()
        resized_image.save(img_io, format='PNG')
        img_io.seek(0)
        encoded_img = base64.b64encode(img_io.read()).decode("utf-8")

        scaled_rects = []
        for rect in app.config['RECTANGLES'].to_dict(orient="records"):
            scaled_rects.append({
                "index": rect["index"],
                "x1": rect["x1"] * app.config['LES_IMAGE_SCALE'],
                "y1": rect["y1"] * app.config['LES_IMAGE_SCALE'],
                "x2": rect["x2"] * app.config['LES_IMAGE_SCALE'],
                "y2": rect["y2"] * app.config['LES_IMAGE_SCALE'],
                "title": rect["title"],
                "modal": rect["modal"],
                "tooltip": rect["tooltip"]
            })
        session['les_image'] = encoded_img
        session['rect_overlay'] = scaled_rects


        #parse text
        for i, row in app.config['RECTANGLES'].iterrows():
            x0 = float(row['x1']) * app.config['LES_COORD_SCALE']
            x1 = float(row['x2']) * app.config['LES_COORD_SCALE']
            y0 = float(row['y1']) * app.config['LES_COORD_SCALE']
            y1 = float(row['y2']) * app.config['LES_COORD_SCALE']
            top = min(y0, y1)
            bottom = max(y0, y1)

            les_rect_text = les_page.within_bbox((x0, top, x1, bottom)).extract_text()
            les_text.append(les_rect_text.replace("\n", " ").split())


    #build dataframe
    paydf = build_paydf(les_text)

    #expand dataframe
    paydf = expand_paydf(paydf)
    print(paydf)

    col_headers = paydf.columns.tolist()
    row_headers = paydf['Header'].tolist()

    session['paydf'] = paydf
    session['col_headers'] = col_headers
    session['row_headers'] = row_headers

    les_pdf.close()

    return render_template('les.html')




def build_paydf(les_text):
    initial_month = les_text[10][3]
    df = pd.DataFrame(columns=["Header", "Type", initial_month])
    row_idx = 0

    row_idx = len(df)

    for header, value in add_variables(les_text):
        df.loc[row_idx] = [header, "V", value]
        row_idx += 1

    for header, value in add_entitlements(les_text):
        df.loc[row_idx] = [header, "E", value]
        row_idx += 1

    for header, value in add_deductions(les_text):
        df.loc[row_idx] = [header, "D", value]
        row_idx += 1

    for header, value in add_allotments(les_text):
        df.loc[row_idx] = [header, "A", value]
        row_idx += 1

    for header, value in add_calculations(df):
        df.loc[row_idx] = [header, "C", value]
        row_idx += 1

    return df


def add_variables(les_text):
    paydate = datetime.strptime(les_text[5][2], '%y%m%d')
    lesdate = pd.to_datetime(datetime.strptime((les_text[10][4] + les_text[10][3] + "1"), '%y%b%d'))
    mis = months_in_service(lesdate, paydate)

    if les_text[50][2] != "00000":
        zc = les_text[50][2]
    else:
        zc = "Not Found"

    mhac, mhan = calculate_mha(les_text[50][2])

    if les_text[41][1] != "98":
        trs = les_text[41][1]
    else:
        trs = "Not Found"

    if les_text[26][1] == "S":
        ffs = "Single"
    elif les_text[26][1] == "M":
        ffs = "Married"
    elif les_text[26][1] == "H":
        ffs = "Head of Household"
    else:
        ffs = "no federal filing status found"

    if les_text[44][1] == "S":
        sfs = "Single"
    elif les_text[44][1] == "M":
        sfs = "Married"
    else:
        sfs = "no state filing status found"

    if len(les_text[54]) == 2:
        jftr = les_text[54][1]
    else:
        jftr = "None"

    if len(les_text[56]) == 3:
        jftr2 = les_text[56][2]
    else:
        jftr2 = "None"

    cz = "No"

    if len(les_text[48]) == 3:
        baqt = (les_text[48][2])[0] + (les_text[48][2])[1:].lower()
    else:
        baqt = "None"

    if len(les_text[57]) == 3:
        bast = les_text[57][2]
    else:
        bast = "None"

    ttsp_fields = [int(les_text[62][3]), int(les_text[64][3]), int(les_text[66][3]), int(les_text[68][3])]
    for val in ttsp_fields:
        if val > 0:
            ttsp = val
            break
        else:
            ttsp = 0

    rtsp_fields = [int(les_text[71][3]), int(les_text[73][3]), int(les_text[75][3]), int(les_text[77][3])]
    for val in rtsp_fields:
        if val > 0:
            rtsp = val
            break
        else:
            rtsp = 0

    variables = [
        ("Year", int(les_text[10][4])),
        ("Rank", les_text[4][1]),
        ("Months in Service", mis),
        ("Zip Code", zc),
        ("MHA Code", mhac),
        ("MHA Name", mhan),
        ("Tax Residency State", trs),
        ("Federal Filing Status", ffs),
        ("State Filing Status", sfs),
        ("Dependents", int(les_text[55][1])),
        ("JFTR", jftr),
        ("JFTR 2", jftr2),
        ("Combat Zone", cz),
        ("BAQ Type", baqt),
        ("BAS Type", bast),
        ("Traditional TSP Rate", ttsp),
        ("Roth TSP Rate", rtsp),
    ]
    return variables





def add_entitlements(les_text):
    entitlements = []
    section = les_text[11]
    for i, row in app.config['PAYDF'].iterrows():
        if row['type'] == 'E':
            short = str(row['shortname'])
            matches = find_multiword_matches(section, short)
            for idx in matches:
                # Look for the first numeric value after the match
                for j in range(idx + 1, len(section)):
                    if section[j].replace('.', '', 1).isdigit():
                        value = Decimal(section[j])
                        entitlements.append((row['header'], value))
                        break
    return entitlements

def add_deductions(les_text):
    deductions = []
    section = les_text[12]
    for i, row in app.config['PAYDF'].iterrows():
        if row['type'] == 'D':
            short = str(row['shortname'])
            matches = find_multiword_matches(section, short)
            for idx in matches:
                for j in range(idx + 1, len(section)):
                    if section[j].replace('.', '', 1).isdigit():
                        value = Decimal(section[j])
                        deductions.append((row['header'], value))
                        break
    return deductions

def add_allotments(les_text):
    allotments = []
    section = les_text[13]
    for i, row in app.config['PAYDF'].iterrows():
        if row['type'] == 'A':
            short = str(row['shortname'])
            matches = find_multiword_matches(section, short)
            for idx in matches:
                for j in range(idx + 1, len(section)):
                    if section[j].replace('.', '', 1).isdigit():
                        value = Decimal(section[j])
                        allotments.append((row['header'], value))
                        break
    return allotments



def add_calculations(paydf):
    calculations = [
        ("Taxable Pay", calculate_taxablepay(paydf, 2)),
        ("Non-Taxable Pay", calculate_nontaxablepay(paydf, 2)),
        ("Total Taxes", calculate_totaltaxes(paydf, 2)),
        ("Gross Pay", calculate_grosspay(paydf, 2)),
        ("Net Pay", calculate_netpay(paydf, 2)),
        ("Difference", "-")
    ]
    return calculations





def expand_paydf(paydf):
    col_headers = paydf.columns.tolist()
    initial_month = col_headers[2]
    month_idx = app.config['MONTHS_SHORT'].index(initial_month)
    #expand out months_num-1 new columns (since first month is already present)
    for i in range(1, session['months_num']):
        #determine new month and add as column header with blank values for each row
        month_idx = (month_idx + 1) % 12
        new_month = app.config['MONTHS_SHORT'][month_idx]
        paydf[new_month] = None

        col_values = []
        calc_row_indices = []
        for row_idx, row in paydf.iterrows():
            if row['Type'] == 'C':
                col_values.append(None)
                calc_row_indices.append(row_idx)
            elif row['Type'] == 'V':
                value = update_variables(paydf, row_idx, new_month)
                col_values.append(value)
            elif row['Type'] == 'E':
                value = update_entitlements(paydf, row_idx, new_month)
                col_values.append(value)
            elif row['Type'] == 'D':
                value = update_deductions(paydf, row_idx, new_month)
                col_values.append(value)
            elif row['Type'] == 'A':
                value = update_allotments(paydf, row_idx, new_month)
                col_values.append(value)
            else:
                value = paydf.iloc[row_idx, 2 + i - 1]
                col_values.append(value)
        paydf[new_month] = col_values
        for row_idx in calc_row_indices:
            value = update_calculations(paydf, row_idx, new_month)
            paydf.at[row_idx, new_month] = value

    return paydf


def update_variables(paydf, row_idx, month):
    header = paydf.at[row_idx, 'Header']
    columns = paydf.columns.tolist()
    prev_month = paydf.columns[-2]
    prev_value = paydf.at[row_idx, prev_month]
    
    if header == 'Year':
        #if current month is JAN and previous month is DEC, increment year
        if app.config['MONTHS_SHORT'].index(month) == 0 and app.config['MONTHS_SHORT'].index(prev_month) == 11:
            return prev_value + 1
        else:
            return prev_value


    if header == 'Rank':
        future_value = session.get('rank_future', '')
        future_month = session.get('rank_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if future_col_idx is not None and current_col_idx >= future_col_idx:
            return future_value
        return prev_value
    

    if header == 'Months in Service':
        return prev_value + 1
    


    if header == 'Zip Code' or header == 'MHA Code' or header == 'MHA Name':
        future_value = session.get('zipcode_future', '')
        future_month = session.get('zipcode_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if header == 'Zip Code':
            if future_col_idx is not None and current_col_idx >= future_col_idx:
                return future_value
        else:
            mhac, mhan = calculate_mha(future_value)
            return mhac if header == 'MHA Code' else mhan
        return prev_value

        

    if header == 'Tax Residency State':
        future_value = session.get('state_future', '')
        future_month = session.get('state_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if future_col_idx is not None and current_col_idx >= future_col_idx:
            return future_value
        return prev_value


    if header == 'Federal Filing Status':
        future_value = session.get('federal_filing_status_future', '')
        future_month = session.get('federal_filing_status_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if future_col_idx is not None and current_col_idx >= future_col_idx:
            return future_value
        return prev_value



    if header == 'State Filing Status':
        future_value = session.get('state_filing_status_future', '')
        future_month = session.get('state_filing_status_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if future_col_idx is not None and current_col_idx >= future_col_idx:
            return future_value
        return prev_value
    

    if header == 'Dependents':
        future_value = session.get('dependents_future', '')
        future_month = session.get('dependents_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if future_col_idx is not None and current_col_idx >= future_col_idx:
            return future_value
        return prev_value


    if header == 'JFTR':
        return prev_value
    

    if header == 'JFTR 2':
        return prev_value


    if header == 'Combat Zone':
        future_value = session.get('combat_zone_future', '')
        future_month = session.get('combat_zone_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if future_col_idx is not None and current_col_idx >= future_col_idx:
            return future_value
        return prev_value


    if header == 'BAQ Type':
        return prev_value
    

    if header == 'BAS Type':
        return prev_value


    if header == 'Traditional TSP Rate':
        future_value = session.get('traditional_tsp_rate_future', '')
        future_month = session.get('traditional_tsp_rate_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if future_col_idx is not None and current_col_idx >= future_col_idx:
            return future_value
        return prev_value


    if header == 'Roth TSP Rate':
        future_value = session.get('roth_tsp_rate_future', '')
        future_month = session.get('roth_tsp_rate_future_month', '')

        #if no future value or month is set, return previous value
        if not future_value or not future_month:
            return prev_value

        #gets the future month index from the columns, if not created yet then is none
        future_col_idx = columns.index(future_month) if future_month in columns else None
        current_col_idx = columns.index(month)

        if future_col_idx is not None and current_col_idx >= future_col_idx:
            return future_value
        return prev_value

    #default to return previous value
    return prev_value



def update_entitlements(paydf, row_idx, month):
    # TODO: Implement entitlement update logic
    return paydf.at[row_idx, paydf.columns[-2]]


def update_deductions(paydf, row_idx, month):
    # TODO: Implement deduction update logic
    return paydf.at[row_idx, paydf.columns[-2]]


def update_allotments(paydf, row_idx, month):
    # TODO: Implement allotment update logic
    return paydf.at[row_idx, paydf.columns[-2]]



def update_calculations(paydf, row_idx, month):
    header = paydf.at[row_idx, 'Header']
    columns = paydf.columns.tolist()
    col_idx = columns.index(month)

    if header == "Taxable Pay":
        return calculate_taxablepay(paydf, col_idx)
    elif header == "Non-Taxable Pay":
        return calculate_nontaxablepay(paydf, col_idx)
    elif header == "Total Taxes":
        return calculate_totaltaxes(paydf, col_idx)
    elif header == "Gross Pay":
        return calculate_grosspay(paydf, col_idx)
    elif header == "Net Pay":
        return calculate_netpay(paydf, col_idx)
    elif header == "Difference":
        return calculate_difference(paydf, col_idx)
    else:
        #default to return previous value
        return paydf.at[row_idx, paydf.columns[col_idx - 1]]




@app.route('/updatepaydf', methods=['POST'])
def update_paydf():
    session['months_num'] = request.form['months_num']
    session['rank_future'] = request.form['rank_future']
    session['rank_future_month'] = request.form['rank_future_month']
    session['zipcode_future'] = request.form['zipcode_future']
    session['zipcode_future_month'] = request.form['zipcode_future_month']
    session['state_future'] = request.form['state_future']
    session['state_future_month'] = request.form['state_future_month']
    session['sgli_future'] = int(request.form['sgli_future'])
    session['sgli_future_month'] = request.form['sgli_future_month']
    session['dependents_future'] = int(request.form['dependents_future'])
    session['dependents_future_month'] = request.form['dependents_future_month']
    session['federal_filing_status_future'] = request.form['federal_filing_status_future']
    session['federal_filing_status_future_month'] = request.form['federal_filing_status_future_month']
    session['state_filing_status_future'] = request.form['state_filing_status_future']
    session['state_filing_status_future_month'] = request.form['state_filing_status_future_month']
    session['combat_zone_future'] = request.form['combat_zone_future']
    session['combat_zone_future_month'] = request.form['combat_zone_future_month']
    session['traditional_tsp_rate_future'] = int(request.form['traditional_tsp_rate_future'])
    session['traditional_tsp_rate_future_month'] = request.form['traditional_tsp_rate_future_month']    
    session['roth_tsp_rate_future'] = int(request.form['roth_tsp_rate_future'])
    session['roth_tsp_rate_future_month'] = request.form['roth_tsp_rate_future_month']


    columns = session['paydf'].columns.tolist()

    #session['paydf'] = expand_paydf(session['paydf'], session['initial_month'], session['months_num'], entitlements_text, deductions_text, allotments_text)

    session['zipcode_future'] = f'{session['zipcode_future']:05}'
    return render_template('les.html')





def calculate_taxablepay(paydf, col_idx):
    total = Decimal(0)
    # Find if combat zone is 'Yes' for this column
    combat_zone_row = paydf[paydf['Header'] == 'Combat Zone']
    combat_zone = None
    if not combat_zone_row.empty:
        combat_zone = combat_zone_row.iloc[0, col_idx]
    for i, row in paydf.iterrows():
        header = row.iloc[0]
        type = row.iloc[1]
        if type == 'E':
            match = app.config['PAYDF'][app.config['PAYDF']['header'] == header]
            if not match.empty:
                # If combat zone is Yes, skip BASE PAY for taxable pay
                if combat_zone == 'Yes' and header == 'Base Pay':
                    continue
                if match.iloc[0]['tax'] == 'Y':
                    value = row.iloc[col_idx]
                    if value is None or value == '':
                        value = 0
                    total += Decimal(value)
    return round(total, 2)


def calculate_nontaxablepay(paydf, col_idx):
    total = Decimal(0)
    for i, row in paydf.iterrows():
        header = row.iloc[0]
        type = row.iloc[1]

        if type == 'E':
            #get the row in the template paydf file that matches the current row header
            match = app.config['PAYDF'][app.config['PAYDF']['header'] == header]

            #if the matching row has a N for tax
            if match.iloc[0]['tax'] == 'N':
                value = row.iloc[col_idx]
                if value is None or value == '':
                    value = 0
                total += Decimal(value)

    return round(total, 2)


def calculate_totaltaxes(paydf, col_idx):
    total = Decimal(0)
    for i, row in paydf.iterrows():
        header = row.iloc[0]
        type = row.iloc[1]

        if type == 'D':
            match = app.config['PAYDF'][app.config['PAYDF']['header'] == header]

            #if the matching row has a Y for tax
            if match.iloc[0]['tax'] == 'Y':
                value = row.iloc[col_idx]
                if value is None or value == '':
                    value = 0
                total += Decimal(value)

    return round(total, 2)


def calculate_grosspay(paydf, col_idx):
    total = Decimal(0)
    for i, row in paydf.iterrows():
        type = row.iloc[1]

        if type == 'E':
            value = row.iloc[col_idx]
            if value is None or value == '':
                value = 0
            total += Decimal(value)

    return round(total, 2)


def calculate_netpay(paydf, col_idx):
    gross = calculate_grosspay(paydf, col_idx)
    loss = Decimal(0)
    for i, row in paydf.iterrows():
        type = row.iloc[1]

        if type in ['D', 'A']:
            value = row.iloc[col_idx]
            if value is None or value == '':
                value = 0
            loss += Decimal(value)

    return round(gross - loss, 2)


def calculate_difference(paydf, col_idx):
    netpay_current = calculate_netpay(paydf, col_idx)
    netpay_prev = calculate_netpay(paydf, col_idx - 1)
    return round(netpay_current - netpay_prev, 2)




def months_in_service(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def calculate_mha(zipcode):
    if zipcode != "00000" or zipcode != "" or zipcode is not None:
        mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([int(zipcode)])].stack()
        mha_search_row = mha_search.index[0][0]
        mhac = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
        mhan = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]
    else:
        mhac = "no mha code found"
        mhan = "no mha name found"
    return mhac, mhan


def find_multiword_matches(section, shortname):
    short_words = shortname.split()
    n = len(short_words)
    matches = []
    for i in range(len(section) - n + 1):
        candidate = ' '.join(section[i:i+n])
        if candidate == shortname:
            matches.append(i + n - 1)  # index of last word in match
    return matches



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def validate_file(file):
    if file.filename == '':
        return False, "No file selected"
    if not allowed_file(file.filename):
        return False, "Invalid file type, only PDF is accepted"
    return True, ""


def reset_session_defaults():
    session.clear()
    for key, value in app.config['SESSION_DEFAULTS'].items():
        session[key] = value


@app.route('/export', methods=['POST'])
def export_dataframe():
    filetype = request.form.get('filetype')

    if filetype not in ['csv', 'xlsx']:
        return "Invalid file type requested", 400

    buffer = io.BytesIO()

    if filetype == 'csv':
        session['paydf'].to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name='payles.csv',
            mimetype='text/csv'
        )
    else:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            session['paydf'].to_excel(writer, index=False, sheet_name='Sheet1')
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name='payles.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    

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