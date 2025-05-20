from flask import Flask
from flask import request, render_template, make_response, jsonify, session, send_file
from flask_session import Session
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
from datetime import datetime
import pdfplumber
import os
import io
import pandas as pd
import io


app = Flask(__name__)
app.config.from_object(Config)
Session(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    session['months_num'] = app.config['DEFAULT_MONTHS_NUM']
    session['export_type'] = ""

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

    if 'file' not in request.files:
        return 'No file part in the request', 400

    if 'file' in request.files:
        file = request.files['file']

        if file.filename == '':
            return 'No selected file', 400

        if file and not allowed_file(file.filename):
            return 'File type not allowed', 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            with pdfplumber.open(file) as les_pdf:
                les_page = les_pdf.pages[0]
                les_text = ["text per rectangle"]

                for i, row in app.config['RECTANGLES'].iterrows():
                    x0 = float(row['x1']) * app.config['LES_COORD_SCALE']
                    x1 = float(row['x2']) * app.config['LES_COORD_SCALE']
                    y0 = float(row['y1']) * app.config['LES_COORD_SCALE']
                    y1 = float(row['y2']) * app.config['LES_COORD_SCALE']
                    top = min(y0, y1)
                    bottom = max(y0, y1)

                    les_rect_text = les_page.within_bbox((x0, top, x1, bottom)).extract_text()
                    les_text.append(les_rect_text.replace("\n", " ").split())

                #inum = 0
                #for x in les_text:
                #    print("rectangle ",inum,": ",x)
                #    inum += 1


                paydf_month = [""]
                for i in range(session['months_num']):
                    paydf_month.append(app.config['MONTHS_SHORT'][(app.config['MONTHS_SHORT'].index(les_text[11][3])+i) % 12])

                paydf_year = ["Year"]
                for i in range(session['months_num']):
                    paydf_year.append("20" + les_text[11][4])

                session['paydf'] = pd.DataFrame([paydf_year], columns=paydf_month)

                
                #variables
                row = ["Rank"]
                for i in range(session['months_num']):
                    row.append(les_text[5][1])
                session['paydf'].loc[len(session['paydf'])] = row
                session['rank_future'] = les_text[5][1]

                paydate = datetime.strptime(les_text[6][2], '%y%m%d')
                row = ["Months of Service"]
                for i in range(session['months_num']):
                    lesdate = pd.to_datetime(datetime.strptime((les_text[11][4] + les_text[11][3] + "1"), '%y%b%d'))+pd.DateOffset(months=i)
                    row.append(months_in_service(lesdate, paydate))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Federal Filing Status"]
                for i in range(session['months_num']):
                    row.append(les_text[39][1])
                session['paydf'].loc[len(session['paydf'])] = row
                session['federal_filing_status_future'] = les_text[39][1]

                row = ["Tax Residency State"]
                for i in range(session['months_num']):
                    row.append(les_text[54][1])
                session['paydf'].loc[len(session['paydf'])] = row
                session['state_future'] = les_text[54][1]

                row = ["State Filing Status"]
                for i in range(session['months_num']):
                    row.append(les_text[57][1])
                session['paydf'].loc[len(session['paydf'])] = row
                session['state_filing_status_future'] = les_text[57][1]

                row = ["BAQ Type"]
                if len(les_text[61]) == 3:
                    for i in range(session['months_num']):
                        row.append(les_text[61][2])
                else:
                    for i in range(session['months_num']):
                        row.append("")
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Zip Code"]
                for i in range(session['months_num']):
                    row.append(les_text[63][2])
                session['paydf'].loc[len(session['paydf'])] = row
                session['zipcode_future'] = les_text[63][2]

                #find MHA
                if les_text[63][2] != "00000":
                    mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([int(les_text[63][2])])].stack()
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

                row = ["JFTR"]
                if len(les_text[67]) == 2:
                    for i in range(session['months_num']):
                        row.append(les_text[67][1])
                else:
                    for i in range(session['months_num']):
                        row.append("")
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Dependents"]
                for i in range(session['months_num']):
                    row.append(int(les_text[68][1]))
                session['paydf'].loc[len(session['paydf'])] = row
                session['dependents_future'] = int(les_text[68][1])

                row = ["JFTR 2"]
                if len(les_text[69]) == 3:
                    for i in range(session['months_num']):
                        row.append(les_text[69][2])
                else:
                    for i in range(session['months_num']):
                        row.append("")
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["BAS Type"]
                if len(les_text[70]) == 3:
                    for i in range(session['months_num']):
                        row.append(les_text[70][2])
                else:
                    for i in range(session['months_num']):
                        row.append("")
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Traditional TSP Base Pay Rate"]
                for i in range(session['months_num']):
                    row.append(int(les_text[75][3]))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Traditional TSP Specialty Pay Rate"]
                for i in range(session['months_num']):
                    row.append(int(les_text[77][3]))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Traditional TSP Incentive Pay Rate"]
                for i in range(session['months_num']):
                    row.append(int(les_text[79][3]))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Traditional TSP Bonus Pay Rate"]
                for i in range(session['months_num']):
                    row.append(int(les_text[81][3]))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Roth TSP Base Pay Rate"]
                for i in range(session['months_num']):
                    row.append(int(les_text[84][3]))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Roth TSP Specialty Pay Rate"]
                for i in range(session['months_num']):
                    row.append(int(les_text[86][3]))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Roth TSP Incentive Pay Rate"]
                for i in range(session['months_num']):
                    row.append(int(les_text[88][3]))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Roth TSP Bonus Pay Rate"]
                for i in range(session['months_num']):
                    row.append(int(les_text[90][3]))
                session['paydf'].loc[len(session['paydf'])] = row
                

                #entitlements
                row = ["Base Pay"]
                if "BASE" in les_text[22]:
                    for i in range(session['months_num']):
                        row.append(Decimal(les_text[22][les_text[22].index("BASE")+2]))
                else:
                    for i in range(session['months_num']):
                        row.append(Decimal(0))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["BAS"]
                if "BAS" in les_text[22]:
                    for i in range(session['months_num']):
                        row.append(Decimal(les_text[22][les_text[22].index("BAS")+1]))
                else:
                    for i in range(session['months_num']):
                        row.append(Decimal(0))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["BAH"]
                if "BAH" in les_text[22]:
                    for i in range(session['months_num']):
                        row.append(Decimal(les_text[22][les_text[22].index("BAH")+1]))
                else:
                    for i in range(session['months_num']):
                        row.append(Decimal(0))
                session['paydf'].loc[len(session['paydf'])] = row

                if "UEA" in les_text[22]:
                    row = ["UEA Initial"]
                    for i in range(session['months_num']):
                        row.append(Decimal(les_text[22][les_text[22].index("UEA")+2]))
                    session['paydf'].loc[len(session['paydf'])] = row

                if "ADVANCE" in les_text[22]:
                    row = ["Advance Debt"]
                    for i in range(session['months_num']):
                        row.append(Decimal(les_text[22][les_text[22].index("ADVANCE")+2]))
                    session['paydf'].loc[len(session['paydf'])] = row

                if "PCS" in les_text[22]:
                    row = ["PCS Member"]
                    for i in range(session['months_num']):
                        row.append(Decimal(les_text[22][les_text[22].index("PCS")+2]))
                    session['paydf'].loc[len(session['paydf'])] = row


                #deductions
                if "FEDERAL" in les_text[23]:
                    row = ["Federal Taxes"]
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("FEDERAL")+2]))
                    session['paydf'].loc[len(session['paydf'])] = row

                if "FICA-SOC" in les_text[23]:
                    row = ["FICA - Social Security"]
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("FICA-SOC")+2]))
                    session['paydf'].loc[len(session['paydf'])] = row

                if "FICA-MEDICARE" in les_text[23]:
                    row = ["FICA - Medicare"]
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("FICA-MEDICARE")+1]))
                    session['paydf'].loc[len(session['paydf'])] = row

                row = ["SGLI"]
                if "SGLI" in les_text[23]:
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("SGLI")+1]))
                else:
                    for i in range(session['months_num']):
                        row.append(Decimal(0))
                session['paydf'].loc[len(session['paydf'])] = row
                session['sgli_future'] = Decimal(les_text[23][les_text[23].index("SGLI")+1])

                row = ["State Taxes"]
                if "STATE" in les_text[23]:
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("STATE")+2]))
                else:
                    for i in range(session['months_num']):
                        row.append(Decimal(0))
                session['paydf'].loc[len(session['paydf'])] = row

                if "ROTH" in les_text[23]:
                    row = ["Roth TSP"]
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("ROTH")+2]))
                    session['paydf'].loc[len(session['paydf'])] = row

                if "PARTIAL" in les_text[23]:
                    row = ["Partial Pay"]
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("PARTIAL")+2]))
                    session['paydf'].loc[len(session['paydf'])] = row

                if "PCS" in les_text[23]:
                    row = ["PCS Members"]
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("PCS")+2]))
                    session['paydf'].loc[len(session['paydf'])] = row

                if "DEBT" in les_text[23]:
                    row = ["Debt"]
                    for i in range(session['months_num']):
                        row.append(-Decimal(les_text[23][les_text[23].index("DEBT")+1]))
                    session['paydf'].loc[len(session['paydf'])] = row


                #calculations
                row = ["Taxable Pay"]
                for column in session['paydf'].columns[1:]:
                    row.append(calculate_taxablepay(column))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Non-Taxable Pay"]
                for column in session['paydf'].columns[1:]:
                    row.append(calculate_nontaxablepay(column))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Total Taxes"]
                for column in session['paydf'].columns[1:]:
                    row.append(-calculate_totaltaxes(column))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Gross Pay"]
                for column in session['paydf'].columns[1:]:
                    row.append(Decimal(session['paydf'][column][20:-3][session['paydf'][column][20:-3] > 0].sum()))
                session['paydf'].loc[len(session['paydf'])] = row

                row = ["Net Pay"]
                for column in session['paydf'].columns[1:]:
                    row.append(Decimal(session['paydf'][column][20:-4].sum()))
                session['paydf'].loc[len(session['paydf'])] = row


                session['col_headers'] = list(session['paydf'].columns)
                session['row_headers'] = list(session['paydf'][session['paydf'].columns[0]])

                les_pdf.close()

            return render_template('les.html')

    return 'File upload failed'



@app.route('/updatemonths', methods=['POST'])
def updatemonths():
    session['months_num'] = int(request.form['months_num'])
    
    df = session['paydf'].copy()
    first_col = df.iloc[:, 0:1]
    other_cols = df.iloc[:, 1:]

    current_other_col_count = other_cols.shape[1]

    if session['months_num'] == current_other_col_count:
        df = df
    elif session['months_num'] < current_other_col_count:
        trimmed_other_cols = other_cols.iloc[:, :session['months_num']]
        df = pd.concat([first_col, trimmed_other_cols], axis=1)
    else:
        last_col = other_cols.iloc[:, -1]
        new_cols = {
            f"extra_col_{i+1}": last_col.copy() for i in range(session['months_num'] - current_other_col_count)
        }
        df_new_cols = pd.DataFrame(new_cols, index=df.index)
        df = pd.concat([first_col, other_cols, df_new_cols], axis=1)

    df2 = df.copy()
    headers = df2.columns.tolist()
    start_month = headers[1]
    start_index = app.config['MONTHS_SHORT'].index(start_month)

    new_headers = [headers[0]]
    for i in range(1, len(headers)):
        month_index = (start_index + (i - 1)) % 12
        new_headers.append(app.config['MONTHS_SHORT'][month_index])

    df2.columns = new_headers

    session['paydf'] = df2
    session['col_headers'] = list(session['paydf'].columns)
    session['row_headers'] = list(session['paydf'][session['paydf'].columns[0]])

    return render_template('les.html')





@app.route('/updatepaydf', methods=['POST'])
def updatepaydf():
    session['rank_future'] = request.form['rank_future']
    session['rank_future_month'] = request.form['rank_future_month']
    session['zipcode_future'] = Decimal(request.form['zipcode_future'])
    session['zipcode_future_month'] = request.form['zipcode_future_month']
    session['dependents_future'] = Decimal(request.form['dependents_future'])
    session['dependents_future_month'] = request.form['dependents_future_month']
    session['sgli_future'] = Decimal(request.form['sgli_future'])
    session['sgli_future_month'] = request.form['sgli_future_month']
    session['state_future'] = request.form['state_future']
    session['state_future_month'] = request.form['state_future_month']
    session['rothtsp_future'] = request.form['rothtsp_future']
    session['rothtsp_future_month'] = request.form['rothtsp_future_month']
    session['federal_filing_status_future'] = request.form['federal_filing_status_future']
    session['federal_filing_status_future_month'] = request.form['federal_filing_status_future_month']
    session['state_filing_status_future'] = request.form['state_filing_status_future']
    session['state_filing_status_future_month'] = request.form['state_filing_status_future_month']


    #variables
    basepay_headers = list(map(int, app.config['PAY_ACTIVE'].columns[1:]))
    basepay_headers.append(504) #add check for over 40+ years
    basepay_col = 0


    for i in range(1, len(session['col_headers'])):

        #update base pay
        for j in range(len(session['col_headers'])):
            if basepay_headers[j] <= session['paydf'].at[session['row_headers'].index("Months of Service"), session['col_headers'][i]] < basepay_headers[j+1]:
                basepay_col = basepay_headers[j]

        basepay_value = app.config['PAY_ACTIVE'].loc[app.config['PAY_ACTIVE']["Rank"] == session['rank_future'], str(basepay_col)]
        basepay_value = Decimal(basepay_value.iloc[0])

        if i >= session['col_headers'].index(session['rank_future_month']):
            session['paydf'].at[session['row_headers'].index("Base Pay"), session['col_headers'][i]] = round(basepay_value, 2)
        else:
            session['paydf'].at[session['row_headers'].index("Base Pay"), session['col_headers'][i]] = round(session['paydf'].at[session['row_headers'].index("Base Pay"), session['col_headers'][1]], 2)


        #update bas
        if i >= session['col_headers'].index(session['rank_future_month']):
            rank_index = app.config['RANKS_SHORT'].index(session['rank_future'])
            if rank_index > 8:
                bas_value = app.config['BAS_AMOUNT'][0]
            else:
                bas_value = app.config['BAS_AMOUNT'][1]
            session['paydf'].at[session['row_headers'].index("BAS"), session['col_headers'][i]] = round(bas_value, 2)
        else:
            session['paydf'].at[session['row_headers'].index("BAS"), session['col_headers'][i]] = round(session['paydf'].at[session['row_headers'].index("BAS"), session['col_headers'][1]], 2)


    #update BAH
    for i in range(1, len(session['col_headers'])):
        mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([int(session['paydf'].at[session['row_headers'].index("Zip Code"), session['col_headers'][i]])])].stack()
        mha_search_row = mha_search.index[0][0]
        session['mha_future'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
        session['mha_future_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]
        
        if session['paydf'].at[session['row_headers'].index("Dependents"), session['col_headers'][i]] > 0:
            bah_df = app.config['BAH_WITH_DEPENDENTS']
        else:
            bah_df = app.config['BAH_WITHOUT_DEPENDENTS']

        bah_value = bah_df.loc[bah_df["MHA"] == session['mha_future'], session['paydf'].at[session['row_headers'].index("Rank"), session['col_headers'][i]]]
        bah_value = bah_value.iloc[0]
        bah_value = Decimal(float(bah_value))

        session['paydf'].at[session['row_headers'].index("BAH"), session['col_headers'][i]] = round(bah_value, 2)



    #update gross pay
    for i in range(1, len(session['col_headers'])):
        session['paydf'].at[session['row_headers'].index("Gross Pay"), session['col_headers'][i]] = round(Decimal(session['paydf'][session['col_headers'][i]][20:-5][session['paydf'][session['col_headers'][i]][20:-5] > 0].sum()), 2)

    #update taxable pay
    for i in range(1, len(session['col_headers'])):
        session['paydf'].at[session['row_headers'].index("Taxable Pay"), session['col_headers'][i]] = calculate_taxablepay(session['col_headers'][i])

    #update non-taxable pay
    for i in range(1, len(session['col_headers'])):
        session['paydf'].at[session['row_headers'].index("Non-Taxable Pay"), session['col_headers'][i]] = calculate_nontaxablepay(session['col_headers'][i])


    #update federal tax rate
    #session['federaltaxes_status_over_months'] = []
    #for i in range(1, len(session['col_headers'])):
    #    if i >= session['col_headers'].index(session['federaltaxes_status_future_month']):
    #        session['federaltaxes_status_over_months'].append(session['federaltaxes_status_future'])
    #    else:
    #        session['federaltaxes_status_over_months'].append(session['federaltaxes_status_current'])
#
#    for i in range(1, len(session['col_headers'])):
#        session['paydf'].at[session['row_headers'].index("Federal Taxes"), session['col_headers'][i]] = round(-Decimal(calculate_federaltaxes(session['col_headers'][i], i)), 2)


    #update fica - social security
    for i in range(1, len(session['col_headers'])):
        session['paydf'].at[session['row_headers'].index("FICA - Social Security"), session['col_headers'][i]] = round(-Decimal(session['paydf'].at[session['row_headers'].index("Taxable Pay"), session['col_headers'][i]] * app.config['FICA_SOCIALSECURITY_TAX_RATE']), 2)

    #update fica-medicare
    for i in range(1, len(session['col_headers'])):
        session['paydf'].at[session['row_headers'].index("FICA - Medicare"), session['col_headers'][i]] = round(-Decimal(session['paydf'].at[session['row_headers'].index("Taxable Pay"), session['col_headers'][i]] * app.config['FICA_MEDICARE_TAX_RATE']), 2)

    #update sgli
    for i in range(1, len(session['col_headers'])):
        if i >= session['col_headers'].index(session['sgli_future_month']):
            session['paydf'].at[session['row_headers'].index("SGLI"), session['col_headers'][i]] = -session['sgli_future']
        else:
            session['paydf'].at[session['row_headers'].index("SGLI"), session['col_headers'][i]] = session['paydf'].at[session['row_headers'].index("SGLI"), session['col_headers'][1]]


    #update total taxes, net pay
    for i in range(1, len(session['col_headers'])):
        session['paydf'].at[session['row_headers'].index("Total Taxes"), session['col_headers'][i]] = calculate_totaltaxes(session['col_headers'][i])
        session['paydf'].at[session['row_headers'].index("Net Pay"), session['col_headers'][i]] = round(Decimal(session['paydf'][session['col_headers'][i]][20:-5].sum()), 2)

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






def calculate_federaltaxes(column, i):
    i = i - 1
    taxable_income = session['matrix'].at[list(session['matrix'][session['matrix'].columns[0]]).index("Taxable Pay"), column] * 12
    taxable_income = round(taxable_income, 2)

    if session['federaltaxes_status_over_months'][i] == "Single":
        taxable_income -= app.config['STANDARD_DEDUCTIONS'][0]
    elif session['federaltaxes_status_over_months'][i] == "Married":
        taxable_income -= app.config['STANDARD_DEDUCTIONS'][1]
    elif session['federaltaxes_status_over_months'][i] == "Head of Household":
        taxable_income -= app.config['STANDARD_DEDUCTIONS'][2]
    else:
        print("no standard deduction found")

    brackets = app.config['FEDERAL_TAX_RATE'][app.config['FEDERAL_TAX_RATE']['Status'].str.lower() == session['federaltaxes_status_over_months'][i].lower()]
    brackets = brackets.sort_values(by='Bracket').reset_index(drop=True)

    tax = Decimal(0)

    for i in range(len(brackets)):
        lower = brackets.at[i, 'Bracket']
        rate = brackets.at[i, 'Rate']

        if i + 1 < len(brackets):
            upper = brackets.at[i + 1, 'Bracket']
        else:
            upper = float('inf')

        if taxable_income <= Decimal(float(lower)):
            break

        taxable_amount = min(taxable_income, upper) - lower
        tax += taxable_amount * Decimal(rate)

    tax = tax / 12
    return round(tax, 2)



def calculate_taxablepay(column):
    tp = 0
    tp += Decimal(session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Base Pay"), column])
    return round(tp, 2)

def calculate_nontaxablepay(column):
    ntp = 0
    ntp += session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("BAS"), column]
    ntp += session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("BAH"), column]
    return round(ntp, 2)

def calculate_totaltaxes(column):
    return Decimal((session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("Federal Taxes"), column]) + (session['paydf'].at[list(session['paydf'][session['paydf'].columns[0]]).index("State Taxes"), column]))




def months_in_service(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month




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