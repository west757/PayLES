from flask import Flask
from flask import request, render_template, make_response, jsonify, session, send_file, flash
from flask_session import Session
from config import Config
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
from datetime import datetime
from PIL import Image
import pdfplumber
import os
import io
import pandas as pd
import base64
import re

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit_les', methods=['POST'])
def submit_les():
    les_file = request.files.get('submit-input')
    if not les_file:
        return render_template("submit.html", error="No file part in form")

    valid, message = validate_file(les_file)
    if not valid:
        return render_template("submit.html", error=message)

    read_les(les_file)
    return None


@app.route('/submit_example', methods=['POST'])
def submit_example():
    read_les(app.config['EXAMPLE_LES'])
    return render_template('les.html')


@app.route('/read_les', methods=['POST'])
def read_les(les_file):
    session['months_num'] = app.config['DEFAULT_MONTHS_NUM']
    session['les_image'] = None
    session['rect_overlay'] = 0
    session['export_type'] = ""
    session['showallvariables'] = False

    session['rank_future'] = ""
    session['rank_future_month'] = ""
    session['zipcode_future'] = 0
    session['zipcode_future_month'] = ""
    session['mha_current'] = ""
    session['mha_current_name'] = ""
    session['mha_future'] = ""
    session['mha_future_name'] = ""
    session['sgli_future'] = 0
    session['sgli_future_month'] = ""
    session['state_future'] = ""
    session['state_future_month'] = ""
    session['rothtsp_future'] = 0
    session['rothtsp_future_month'] = ""
    session['dependents_future'] = 0
    session['dependents_future_month'] = ""
    session['federal_filing_status_future'] = ""
    session['federal_filing_status_future_month'] = ""
    session['state_filing_status_future'] = ""
    session['state_filing_status_future_month'] = ""

    session['traditional_tsp_rate_future'] = 0
    session['traditional_tsp_rate_future_month'] = ""
    session['roth_tsp_rate_future'] = 0
    session['roth_tsp_rate_future_month'] = ""



    with pdfplumber.open(les_file) as les_pdf:
        les_page = les_pdf.pages[0].crop((0, 0, 612, 630))
        title_crop = les_page.crop((18, 18, 593, 29))
        title_text = title_crop.extract_text_simple()
        if title_text == "DEFENSE FINANCE AND ACCOUNTING SERVICE MILITARY LEAVE AND EARNINGS STATEMENT":
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

            #rect_num = 0
            #for x in les_text:
            #    print("rectangle ",rect_num,": ",x)
            #    rect_num += 1


            #entitlements
            entitlements_crop = les_page.crop((44, 88, 184, 200))
            entitlements_text = string_to_array(entitlements_crop.extract_text_simple())

            #deductions
            deductions_crop = les_page.crop((184, 88, 320, 200))
            deductions_text = string_to_array(deductions_crop.extract_text_simple())

            #remove mid month pay if present


            #allotments
            allotments_crop = les_page.crop((320, 88, 456, 200))
            allotments_text = string_to_array(allotments_crop.extract_text_simple())
            
            #print("entitlements_text: ", entitlements_text)
            #print("deductions_text: ", deductions_text)
            #print("allotments_text: ", allotments_text)



            #validate check with if
            session['initial_month'] = les_text[10][3]

            
            session['paydf'] = build_paydf(session['initial_month'], les_text, entitlements_text, deductions_text, allotments_text)
            session['paydf'] = expand_paydf(session['paydf'], session['initial_month'], session['months_num'], entitlements_text, deductions_text, allotments_text)

            session['col_headers'] = list(session['paydf'].columns)
            session['row_headers'] = list(session['paydf'][session['paydf'].columns[0]])

            les_pdf.close()
            return render_template('les.html')
        else:
            les_pdf.close()
            return render_template("submit.html", error="File is not a valid LES")






#set things to int if necessary
#initial month variable set


def build_paydf(initial_month, les_text, entitlements_text, deductions_text, allotments_text):
    rows = []

    #variables
    row = ["Year"]
    if len(les_text[10]) == 5:
        value = les_text[10][4]
        if value != "":
            row.append("20" + value)
        else:
            row.append("no year found")
    else:
        row.append("no year found")
    rows.append(row)

    row = ["Rank"]
    if len(les_text[4]) == 2:
        value = les_text[4][1]
        if value in app.config['RANKS_SHORT']:
            row.append(value)
        else:
            row.append("no rank found")
    else:
        row.append("no rank found")
    rows.append(row)
    session['rank_future'] = row[1]

    row = ["Months in Service"]
    if len(les_text[5]) == 3:
        paydate = datetime.strptime(les_text[5][2], '%y%m%d')
        lesdate = pd.to_datetime(datetime.strptime((les_text[10][4] + les_text[10][3] + "1"), '%y%b%d'))
        value = months_in_service(lesdate, paydate)
        if value != "":
            row.append(value)
        else:
            row.append("no pay date found")
    else:
        row.append("no pay date found")
    rows.append(row)

    row = ["Zip Code"]
    if len(les_text[5]) == 3:
        value = les_text[50][2]
        if value != "00000":
            row.append(value)
        else:
            row.append("no zip code found")
    else:
        row.append("no zip code found")
    rows.append(row)
    session['zipcode_future'] = row[1]

    row = ["Dependents"]
    if len(les_text[55]) == 2:
        value = les_text[55][1]
        if value != "":
            row.append(value)
        else:
            row.append("no dependents found")
    else:
        row.append("no dependents found")
    rows.append(row)
    session['dependents_future'] = row[1]

    row = ["Federal Filing Status"]
    if len(les_text[26]) == 2:
        value = les_text[26][1]
        if value == "S":
            row.append("Single")
        elif value == "M":
            row.append("Married")
        elif value == "H":
            row.append("Head of Household")
        else:
            row.append("no federal filing status found")
    else:
        row.append("no federal filing status found")
    rows.append(row)
    session['federal_filing_status_future'] = row[1]

    row = ["State Filing Status"]
    if len(les_text[44]) == 2:
        value = les_text[44][1]
        if value == "S":
            row.append("Single")
        elif value == "M":
            row.append("Married")
        else:
            row.append("no state filing status found")
    else:
        row.append("no state filing status found")
    rows.append(row)
    session['state_filing_status_future'] = row[1]

    row = ["Tax Residency State"]
    if len(les_text[54]) == 2:
        value = les_text[41][1]
        if value != "98" and value != "":
            row.append(value)
        else:
            row.append("no tax residency state found")
    else:
        row.append("no tax residency state found")
    rows.append(row)
    session['state_future'] = row[1]

    row = ["JFTR"]
    if len(les_text[54]) == 2:
        value = les_text[54][1]
        if value != "":
            row.append(value)
        else:
            row.append("no JFTR found")
    else:
        row.append("no JFTR found")
    rows.append(row)

    row = ["JFTR 2"]
    if len(les_text[56]) == 3:
        value = les_text[56][2]
        if value != "":
            row.append(value)
        else:
            row.append("no JFTR 2 found")
    else:
        row.append("no JFTR 2 found")
    rows.append(row)

    row = ["BAS Type"]
    if len(les_text[57]) == 3:
        value = les_text[57][2]
        if value != "":
            row.append(value)
        else:
            row.append("no BAS type found")
    else:
        row.append("no BAS type found")
    rows.append(row)

    row = ["BAQ Type"]
    if len(les_text[48]) == 3:
        value = (les_text[48][2])[0] + (les_text[48][2])[1:].lower()
        if value != "":
            row.append(value)
        else:
            row.append("no BAQ type found")
    else:
        row.append("no BAQ type found")
    rows.append(row)


    #find MHA
    if les_text[50][2] != "00000":
        mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([int(les_text[50][2])])].stack()
        mha_search_row = mha_search.index[0][0]
        session['mha_current'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
        session['mha_current_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]
        session['mha_future'] = session['mha_current']
        session['mha_future_name'] = session['mha_current_name']
    else:
        session['mha_current'] = "no MHA found"
        session['mha_current_name'] = "no MHA found"
        session['mha_future'] = "no MHA found"
        session['mha_future_name'] = "no MHA found"
        

    #tsp rates
    row = ["Traditional TSP Rate"]
    if len(les_text[62]) == 4:
        value = les_text[62][3]
        if value != "":
            row.append(value)
        else:
            row.append("no traditional TSP rate found")
    else:
        row.append("no traditional TSP rate found")
    rows.append(row)
    session['traditional_tsp_rate_future'] = row[1]

    row = ["Roth TSP Rate"]
    if len(les_text[71]) == 4:
        value = les_text[71][3]
        if value != "":
            row.append(value)
        else:
            row.append("no roth TSP rate found")
    else:
        row.append("no roth TSP rate found")
    rows.append(row)
    session['roth_tsp_rate_future'] = row[1]

    
    #entitlements, deductions, allotments
    for entitlement in entitlements_text:
        header, value = entitlement
        rows.append([header, value])

    for deduction in deductions_text:
        if deduction[0].upper() == "MID-MONTH-PAY":
            continue
        header, value = deduction
        rows.append([header, value])

    for allotment in allotments_text:
        header, value = allotment
        rows.append([header, value])


    df = pd.DataFrame(rows, columns=["month", initial_month])
    return df







def expand_paydf(df, initial_month, months_number, entitlement_headers, deduction_headers, allotment_headers):
    start_idx = app.config['MONTHS_SHORT'].index(initial_month.upper())
    month_columns = [app.config['MONTHS_SHORT'][(start_idx + i) % 12] for i in range(months_number)]
    df.columns = ["month", month_columns[0]]

    calc_function_map = {
        "Year": calculate_year,
        "Rank": calculate_rank,
        "Months in Service": calculate_months_in_service,
        "Zip Code": calculate_zipcode,
        "Dependents": calculate_dependents,
        "Federal Filing Status": calculate_federal_filing_status,
        "State Filing Status": calculate_state_filing_status,
        "Tax Residency State": calculate_state,
        "JFTR": calculate_jftr,
        "JFTR2": calculate_jftr,
        "BAS Type": calculate_bas_type,
        "BAQ Type": calculate_baq_type,
        "Traditional TSP Rate": calculate_traditional_tsp_rate,
        "Roth TSP Rate": calculate_roth_tsp_rate,
        "BASE PAY": calculate_base_pay,
        "BAS": calculate_bas,
        "BAH": calculate_bah,
        "FEDERAL TAXES": calculate_federal_taxes,
        "FICA-SOC SECURITY": calculate_fica_soc_security,
        "FICA-MEDICARE": calculate_fica_medicare,
        "STATE TAXES": calculate_state_taxes,
        "SGLI": calculate_sgli,
        "TRADITIONAL TSP": calculate_traditional_tsp,
        "ROTH TSP": calculate_roth_tsp
    }

    for i in range(1, months_number):
        current_month = month_columns[i]
        prev_month = month_columns[i - 1]
        new_col = []

        for idx, row in df.iterrows():
            label = row["month"]
            try:
                prev_val = float(df.at[idx, prev_month])
            except:
                new_col.append("")
                continue

            if label in calc_function_map:
                new_val = calc_function_map[label](prev_val, current_month)
            else:
                new_val = prev_val
            new_col.append(new_val)

        df[current_month] = new_col


    deduction_row_headers = [x for x in deduction_row_headers if x.upper() != "MID-MONTH-PAY"]

    def sum_rows(row_names, month):
        return df[df["month"].isin(row_names)][month].astype(float).sum()


    df = calculate_tax_rows(df, month_columns, entitlement_headers)

    gross = [sum_rows(entitlement_headers, m) for m in month_columns]
    df.loc[len(df)] = ["Gross Pay"] + gross

    net = [
        g - sum_rows(deduction_headers, m) - sum_rows(allotment_headers, m)
        for g, m in zip(gross, month_columns)
    ]
    df.loc[len(df)] = ["Net Pay"] + net



    diff = ["Difference"]
    for i in range(months_number):
        if i == 0:
            diff.append(0)
        else:
            diff.append(round(net[i] - net[i - 1], 2))
    df.loc[len(df)] = diff

    ordered_labels = entitlement_headers + deduction_headers + allotment_headers
    calc_labels = ["Taxable Pay", "Non-Taxable Pay", "Total Taxes", "Gross Pay", "Net Pay", "Difference"]
    hardcoded_labels = [label for label in df["month"] if label not in ordered_labels + calc_labels]
    final_order = hardcoded_labels + ordered_labels + calc_labels

    final_rows = []
    for label in final_order:
        match = df[df["month"] == label]
        if not match.empty:
            final_rows.append(match.iloc[0].tolist())

    return pd.DataFrame(final_rows, columns=["month"] + month_columns)



def calculate_tax_rows(df, month_columns, pay_row_headers):
    taxablepay_sources = ["Base Pay"]
    nontaxablepay_sources = [src for src in pay_row_headers if src not in taxablepay_sources]

    taxablepay = [df[df["month"].isin(taxablepay_sources)][m].astype(float).sum() for m in month_columns]
    df.loc[len(df)] = ["Taxable Pay"] + taxablepay

    nontaxablepay = [df[df["month"].isin(nontaxablepay_sources)][m].astype(float).sum() for m in month_columns]
    df.loc[len(df)] = ["Non-Taxable Pay"] + nontaxablepay

    total_taxes = [t1 + t2 for t1, t2 in zip(taxablepay, nontaxablepay)]
    df.loc[len(df)] = ["Total Taxes"] + total_taxes

    return df


#needs fix
def calculate_year():
    paydf_year = ["Year"]
    current_year = int(les_text[10][4])
    prev_month_index = app.config['MONTHS_SHORT'].index(paydf_month[1])
    for month in paydf_month[1:]:
        month_index = app.config['MONTHS_SHORT'].index(month)
        if month_index < prev_month_index:
                current_year += 1
         
    paydf_year.append("20" + str(current_year))
    prev_month_index = month_index
    return None


def calculate_rank(prev_value, current_month):
    if session['rank_future_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['rank_future_month']):
            return session['rank_future']
    return prev_value


#needs fix
def calculate_months_in_service():
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def calculate_zipcode(prev_value, current_month):
    if session['zipcode_future_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['zipcode_future_month']):
            return f'{session['zipcode_future']:05}'
    return prev_value


def calculate_dependents(prev_value, current_month):
    if session['dependents_future_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['dependents_future_month']):
            return session['dependents_future']
    return prev_value

def calculate_federal_filing_status(prev_value, current_month):
    if session['federal_filing_status_future_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['federal_filing_status_future_month']):
            return session['federal_filing_status_future']
    return prev_value

def calculate_state_filing_status(prev_value, current_month):
    if session['state_filing_status_future_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['state_filing_status_future_month']):
            return session['state_filing_status_future']
    return prev_value

def calculate_state(prev_value, current_month):
    if session['state_future_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['state_future_month']):
            return session['state_future']
    return prev_value

def calculate_jftr(prev_value, current_month):
    return prev_value

def calculate_jftr2(prev_value, current_month):
    return prev_value

def calculate_bas_type(prev_value, current_month):
    return prev_value

def calculate_baq_type(prev_value, current_month):
    return prev_value

def calculate_traditional_tsp_rate(prev_value, current_month):
    if session['traditional_tsp_rate_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['traditional_tsp_rate_month']):
            return session['traditional_tsp_rate']
    return prev_value

def calculate_roth_tsp_rate(prev_value, current_month):
    if session['roth_tsp_rate_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['roth_tsp_rate_month']):
            return session['roth_tsp_rate']
    return prev_value




def calculate_base_pay(prev_value, current_month):
    basepay_col = 0
    for i in range(len(app.config['PAY_ACTIVE_HEADERS'])):
        if app.config['PAY_ACTIVE_HEADERS'][i] <= session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Months in Service"), current_month] < app.config['PAY_ACTIVE_HEADERS'][i+1]:
            basepay_col = app.config['PAY_ACTIVE_HEADERS'][i]

    basepay_value = app.config['PAY_ACTIVE'].loc[app.config['PAY_ACTIVE']["Rank"] == session['rank_future'], str(basepay_col)]
    return round(Decimal(basepay_value.iloc[0]), 2)


def calculate_bas(prev_value, current_month):
    if session['rank_future_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['rank_future_month']):
                rank_index = app.config['RANKS_SHORT'].index(session['rank_future'])
                if rank_index > 8:
                    bas_value = app.config['BAS_AMOUNT'][0]
                else:
                    bas_value = app.config['BAS_AMOUNT'][1]
            return round(bas_value, 2)
    return prev_value


def calculate_bah(prev_value, current_month):
    if session['paydf'].at[session['row_headers'].index("Zip Code"), session['col_headers'][i]] != "Not Found" and session['paydf'].at[session['row_headers'].index("Zip Code"), session['col_headers'][i]] != "00000":
        mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([int(session['zipcode_future'])])].stack()
        mha_search_row = mha_search.index[0][0]
        session['mha_future'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
        session['mha_future_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]
        
        if session['paydf'].at[session['row_headers'].index("Dependents"), session['col_headers'][current_month]] > 0:
            bah_df = app.config['BAH_WITH_DEPENDENTS']
        else:
            bah_df = app.config['BAH_WITHOUT_DEPENDENTS']

        bah_value = bah_df.loc[bah_df["MHA"] == session['mha_future'], session['paydf'].at[session['row_headers'].index("Rank"), session['col_headers'][i]]]
        bah_value = Decimal(float(bah_value.iloc[0]))
    return round(bah_value, 2)


def calculate_federal_taxes(prev_value, current_month):
    taxable_income = session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Taxable Pay"), current_month] * 12
    taxable_income = round(taxable_income, 2)
    tax = Decimal(0)

    if session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Federal Filing Status"), current_month] == "Single":
        taxable_income -= app.config['STANDARD_DEDUCTIONS'][0]
    elif session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Federal Filing Status"), current_month] == "Married":
        taxable_income -= app.config['STANDARD_DEDUCTIONS'][1]
    elif session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Federal Filing Status"), current_month] == "Head of Household":
        taxable_income -= app.config['STANDARD_DEDUCTIONS'][2]
    else:
        print("no standard deduction found")

    brackets = app.config['FEDERAL_TAX_RATE'][app.config['FEDERAL_TAX_RATE']['Status'].str.lower() == session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Federal Filing Status"), column].lower()]
    brackets = brackets.sort_values(by='Bracket').reset_index(drop=True)

    for i in range(len(brackets)):
        lower = brackets.at[i, 'Bracket']
        rate = brackets.at[i, 'Rate']

        if i + 1 < len(brackets):
            upper = brackets.at[i + 1, 'Bracket']
        else:
            upper = float('inf')

        if taxable_income > Decimal(float(lower)):
            taxable_amount = min(taxable_income, upper) - lower
            tax += taxable_amount * Decimal(rate)

    tax = tax / 12
    return round(-tax, 2)


def calculate_fica_soc_security(prev_value, current_month):
    return round(-Decimal(prev_value * app.config['FICA_SOCIALSECURITY_TAX_RATE']), 2)


def calculate_fica_medicare(prev_value, current_month):
    return round(-Decimal(prev_value * app.config['FICA_MEDICARE_TAX_RATE']), 2)


def calculate_state_taxes(prev_value, current_month):
    taxable_income = session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Taxable Pay"), column] * 12
    taxable_income = round(taxable_income, 2)
    tax = Decimal(0)

    state_brackets = app.config['STATE_TAX_RATE'][app.config['STATE_TAX_RATE']['State'] == session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Tax Residency State"), column]]
        
    if session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("State Filing Status"), column] == "Single":
        brackets = state_brackets[['SingleBracket', 'SingleRate']].rename(columns={'SingleBracket': 'Bracket', 'SingleRate': 'Rate'})
    elif session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("State Filing Status"), column] == "Married":
        brackets = state_brackets[['MarriedBracket', 'MarriedRate']].rename(columns={'MarriedBracket': 'Bracket', 'MarriedRate': 'Rate'})
    else:
        print("no state filing status found")
        
    brackets = brackets.sort_values(by='Bracket')
    brackets = brackets.reset_index(drop=True)

    for i in range(len(brackets)):
        lower = brackets.loc[i, 'Bracket']
        rate = brackets.loc[i, 'Rate']

        if i + 1 < len(brackets):
            upper = brackets.loc[i + 1, 'Bracket']
        else:
            upper = float('inf')

        if taxable_income > Decimal(float(lower)):
            taxable_at_this_rate = min(taxable_income, upper) - lower
            tax += taxable_at_this_rate * Decimal(rate)

    tax = tax / 12
    return round(-tax, 2)


def calculate_sgli(prev_value, current_month):
    if session['sgli_future_month']:
        if app.config['MONTHS_SHORT'].index(current_month) >= app.config['MONTHS_SHORT'].index(session['sgli_future_month']):
            return -session['sgli_future']
    return prev_value


def calculate_traditional_tsp(prev_value, current_month):
    return prev_value

def calculate_roth_tsp(prev_value, current_month):
    return prev_value









@app.route('/showallvariables', methods=['POST'])
def showallvariables():
    if session['showallvariables']:
        session['showallvariables'] = False
    else:
        session['showallvariables'] = bool(request.form['showallvariables'])
    return render_template('les.html')


@app.route('/updatepaydf', methods=['POST'])
def updatepaydf():
    session['rank_future'] = request.form['rank_future']
    session['rank_future_month'] = request.form['rank_future_month']
    session['federal_filing_status_future'] = request.form['federal_filing_status_future']
    session['federal_filing_status_future_month'] = request.form['federal_filing_status_future_month']
    session['state_filing_status_future'] = request.form['state_filing_status_future']
    session['state_filing_status_future_month'] = request.form['state_filing_status_future_month']
    session['state_future'] = request.form['state_future']
    session['state_future_month'] = request.form['state_future_month']
    session['zipcode_future'] = Decimal(request.form['zipcode_future'])
    session['zipcode_future_month'] = request.form['zipcode_future_month']
    session['dependents_future'] = Decimal(request.form['dependents_future'])
    session['dependents_future_month'] = request.form['dependents_future_month']
    session['sgli_future'] = Decimal(request.form['sgli_future'])
    session['sgli_future_month'] = request.form['sgli_future_month']
    session['rothtsp_future'] = request.form['rothtsp_future']
    session['rothtsp_future_month'] = request.form['rothtsp_future_month']

    columns = session['paydf'].columns.tolist()

    session['paydf'] = expand_paydf(session['paydf'], session['initial_month'], session['months_num'], entitlements_text, deductions_text, allotments_text)

    session['zipcode_future'] = f'{session['zipcode_future']:05}'
    return render_template('les.html')




@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/leave')
def leave():
    return render_template('leave.html')

@app.route('/404')
def page404():
    return render_template('404.html')




def clean_word(word):
    # Remove numeric prefix and newline, keep only the part after \n if present
    return re.sub(r'^\d+\n', '', word)

def string_to_array(input_str):
    # Replace newlines with spaces
    input_str = input_str.replace('\n', ' ')

    # Match one or two words (with optional dashes), followed by a decimal number
    pattern = r'((?:[\w-]+\s)?[\w-]+)\s+(\d+\.\d+)'
    matches = re.findall(pattern, input_str)

    # Clean words and assemble the result
    result = [[clean_word(text), number] for text, number in matches]
    return result



def months_in_service(d1, d2):



def calculate_basepay(column):



def calculate_federaltaxes(column):



def calculate_statetaxes(column):





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




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_file(file):
    if file.filename == '':
        return False, "No file selected"
    if not allowed_file(file.filename):
        return False, "Invalid file type, only PDF is accepted"
    return True, ""


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