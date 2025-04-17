from flask import Flask
from flask import request, render_template, make_response, jsonify, session
from flask_session import Session
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
from datetime import datetime
#from pdf2image import convert_from_path
import pdfplumber
import os
import pandas as pd

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    session['months_display'] = 6
    session['export_type'] = ""

    session['state_current'] = ""
    session['state_future'] = ""
    session['state_future_month'] = ""
    session['rank_current'] = ""
    session['rank_future'] = ""
    session['rank_future_month'] = ""
    session['pay_date'] = ""
    session['les_date'] = ""
    session['months_in_service'] = 0
    session['serviceyears_current'] = 0
    session['serviceyears_future'] = 0
    session['serviceyears_future_month'] = ""
    session['zipcode_current'] = 0
    session['zipcode_future'] = 0
    session['zipcode_future_month'] = ""
    session['mha_current'] = ""
    session['mha_current_name'] = ""
    session['mha_future'] = ""
    session['mha_future_name'] = ""
    session['sgli_future'] = 0
    session['sgli_future_month'] = ""
    session['rothtsp_future'] = 0
    session['rothtsp_future_month'] = ""
    session['dependents_current'] = 0
    session['dependents_future'] = 0
    session['dependents_future_month'] = ""
    session['federaltaxes_status_current'] = ""
    session['federaltaxes_status_future'] = ""
    session['federaltaxes_status_future_month'] = ""
    session['statetaxes_status_current'] = ""
    session['statetaxes_status_future'] = ""
    session['statetaxes_status_future_month'] = ""

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

            #image = convert_from_path(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #image[0].save(os.path.join(app.config['STATIC_FOLDER'], filename, 'a.jpg'))

            with pdfplumber.open(file) as les_pdf:
                les_page = les_pdf.pages[0]
                les_textstring = les_page.extract_text()
                les_text = les_textstring.split()

                #print(les_text)
                #les_rects = les_page.rects
                #print(les_rects)
                #print("")
                #print("")

                #x0, top, x1, bottom
                #bounding_box = (170, 43, 215, 53)
                #crop_area = les_page.crop(bounding_box)
                #crop_text = crop_area.extract_text().split('\n')
                #for text in crop_text:
                #    print(text)


                #rects_text = []
                #for x in les_rects:
                    #print(x)
                    #print("")
                #    rects_text.append(les_page.crop((x.x0, x.top, x.x1, x.bottom)).extract_text())
                
                #les_rect = les_page.crop((320, 52, 457, 66))
                #les_rect_textstring = les_rect.extract_text()
                #les_rect_text = les_rect_textstring.split()
                #print(les_rect_text)

                #print(rects_text)
                #session['paydate'] = les_page.crop((x0, top, x1, bottom)).extract_text()
                

                #find month
                for x in app.config['MONTHS_SHORT']:
                    if x in les_text:
                        matrix_months = [""]
                        for i in range(session['months_display']):
                            matrix_months.append(app.config['MONTHS_SHORT'][(app.config['MONTHS_SHORT'].index(x)+i) % 12])

                #find rank
                for x in app.config['RANKS_SHORT']:
                    if x in les_text and les_text[les_text.index(x)+9] == "ENTITLEMENTS":
                        session['rank_current'] = x
                        break
                    else:
                        session['rank_current'] = "no rank found"
                session['rank_future'] = session['rank_current']

                #find pay date
                session['pay_date'] = datetime.strptime(les_text[(les_text.index("ENTITLEMENTS")-8)], '%y%m%d')

                #find years of service
                session['serviceyears_current'] = Decimal(les_text[(les_text.index("ENTITLEMENTS")-7)])
                session['serviceyears_future'] = session['serviceyears_current']

                #find les date
                les_date_temp = les_text[(les_text.index("ENTITLEMENTS")-1)] + les_text[(les_text.index("ENTITLEMENTS")-2)] + "1"
                session['les_date'] = datetime.strptime(les_date_temp, '%y%b%d')

                #find months in service
                session['months_in_service'] = months_in_service(session['les_date'], session['pay_date'])

                #find zip code
                session['zipcode_current'] = Decimal(les_text[(les_text.index("PACIDN")+3)])
                session['zipcode_future'] = session['zipcode_current']

                #find MHA
                mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([session['zipcode_current']])].stack()
                mha_search_row = mha_search.index[0][0]

                session['mha_current'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
                session['mha_current_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]
                session['mha_future'] = session['mha_current']
                session['mha_future_name'] = session['mha_current_name']

                #find dependents
                session['dependents_current'] = Decimal(les_text[(les_text.index('PACIDN')+7)])
                session['dependents_future'] = session['dependents_current']

                #find state
                for x in app.config['STATES_SHORT']:
                    if x in les_text and les_text[(les_text.index(x)-1)] == "TAXES":
                        session['state_current'] = x
                        break
                    else:
                        session['state_current'] = "no state found"
                session['state_future'] = session['state_current']

                #find federal tax status
                if (les_text[les_text.index('Income')+6]) == "S":
                    session['federaltaxes_status_current'] = app.config['TAX_FILING_TYPES'][0]
                elif (les_text[les_text.index('Income')+6]) == "M":
                    session['federaltaxes_status_current'] = app.config['TAX_FILING_TYPES'][1]
                elif (les_text[les_text.index('Income')+6]) == "H":
                    session['federaltaxes_status_current'] = app.config['TAX_FILING_TYPES'][2]
                else:
                    session['federaltaxes_status_current'] = "no federal tax filing type found"
                
                session['federaltaxes_status_future'] = session['federaltaxes_status_current']

                #find state tax status
                if (les_text[les_text.index('BAQ')-4]) == "S":
                    session['statetaxes_status_current'] = app.config['TAX_FILING_TYPES'][0]
                elif (les_text[les_text.index('BAQ')-4]) == "M":
                    session['statetaxes_status_current'] = app.config['TAX_FILING_TYPES'][1]
                else:
                    session['statetaxes_status_current'] = "no state tax filing type found"

                session['statetaxes_status_future'] = session['statetaxes_status_current']


                #find base pay
                if "BASE" in les_text:
                    matrix_basepay = ["Base Pay"]
                    for i in range(session['months_display']):
                        matrix_basepay.append(Decimal(les_text[(les_text.index('BASE')+2)]))
                    matrix_basepay2 = [matrix_basepay]
                
                session['matrix'] = pd.DataFrame(matrix_basepay2, columns=matrix_months)

                #find BAS
                if "BAS" in les_text:
                    row = ["BAS"]
                    for i in range(session['months_display']):
                        row.append(Decimal(les_text[(les_text.index('BAS')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find BAH
                if "BAH" in les_text:
                    row = ["BAH"]
                    for i in range(session['months_display']):
                        row.append(Decimal(les_text[(les_text.index('BAH')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find uea initial
                if "UEA" in les_text and les_text[les_text.index('UEA')+1] == "INITIAL":
                    row = ["UEA Initial", Decimal(les_text[(les_text.index('UEA')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                #find advance debt
                if "ADVANCE" in les_text and les_text[les_text.index('ADVANCE')+1] == "DEBT":
                    row = ["Advance Debt", Decimal(les_text[(les_text.index('ADVANCE')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find pcs member
                if "PCS" in les_text and les_text[les_text.index('PCS')+1] == "MEMBER":
                    row = ["PCS Member", Decimal(les_text[(les_text.index('PCS')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                #find federal taxes
                if "FEDERAL" in les_text and les_text[les_text.index('FEDERAL')+1] == "TAXES":
                    row = ["Federal Taxes"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('FEDERAL')+2)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find FICA - Social Security
                if "SECURITY" in les_text:
                    row = ["FICA - Social Security"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('SECURITY')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find FICA - Medicare
                if "FICA-MEDICARE" in les_text:
                    row = ["FICA - Medicare"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('FICA-MEDICARE')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find SGLI
                if "SGLI" in les_text:
                    row = ["SGLI"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('SGLI')+1)]))
                    session['sgli_future'] = -row[1]
                    session['matrix'].loc[len(session['matrix'])] = row

                #find state taxes
                if "STATE" in les_text and les_text[les_text.index('STATE')+1] == "TAXES":
                    row = ["State Taxes"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('STATE')+2)]))
                    session['matrix'].loc[len(session['matrix'])] = row
                else:
                    row = ["State Taxes"]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find Roth TSP
                if "ROTH" in les_text:
                    row = ["Roth TSP"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('ROTH')+2)]))
                    session['matrix'].loc[len(session['matrix'])] = row
                else:
                    row = ["Roth TSP"]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find partial pay
                if "PARTIAL" in les_text and les_text[les_text.index('PARTIAL')+1] == "PAY":
                    row = ["Partial Pay", -Decimal(les_text[(les_text.index('PARTIAL')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find pcs members
                if "PCS" in les_text and les_text[les_text.index('PCS')+1] == "MEMBERS":
                    row = ["PCS Members", -Decimal(les_text[(les_text.index('PCS')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find debt
                if "DEBT" in les_text and les_text[les_text.index('DEBT')-1] != "ADVANCE":
                    row = ["Debt", -Decimal(les_text[(les_text.index('DEBT')+1)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                #taxable pay
                row = ["Taxable Pay"]
                for column in session['matrix'].columns[1:]:
                    row.append(calculate_taxablepay(column))
                session['matrix'].loc[len(session['matrix'])] = row

                #non-taxable pay
                row = ["Non-Taxable Pay"]
                for column in session['matrix'].columns[1:]:
                    row.append(calculate_nontaxablepay(column))
                session['matrix'].loc[len(session['matrix'])] = row

                #total taxes
                row = ["Total Taxes"]
                for column in session['matrix'].columns[1:]:
                    row.append(calculate_totaltaxes(column))
                session['matrix'].loc[len(session['matrix'])] = row

                #gross pay
                row = ["Gross Pay"]
                for column in session['matrix'].columns[1:]:
                    row.append(Decimal(session['matrix'][column][:-3][session['matrix'][column][:-3] > 0].sum()))
                session['matrix'].loc[len(session['matrix'])] = row

                #net pay
                row = ["Net Pay"]
                for column in session['matrix'].columns[1:]:
                    row.append(Decimal(session['matrix'][column][:-4].sum()))
                session['matrix'].loc[len(session['matrix'])] = row


                session['col_headers'] = list(session['matrix'].columns)
                session['row_headers'] = list(session['matrix'][session['matrix'].columns[0]])

                les_pdf.close()

                #matrix_csv = session['matrix'].to_csv("matrix.csv", index=False)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], matrix_csv))

            return render_template('les.html')

    return 'File upload failed'


@app.route('/updatematrixmonths', methods=['POST'])
def updatematrixmonths():
    session['months_display'] = int(request.form['months_display'])
    
    df = session['matrix'].copy()
    first_col = df.iloc[:, 0:1]
    other_cols = df.iloc[:, 1:]

    current_other_col_count = other_cols.shape[1]

    if session['months_display'] == current_other_col_count:
        df = df
    elif session['months_display'] < current_other_col_count:
        trimmed_other_cols = other_cols.iloc[:, :session['months_display']]
        df = pd.concat([first_col, trimmed_other_cols], axis=1)
    else:
        last_col = other_cols.iloc[:, -1]
        new_cols = {
            f"extra_col_{i+1}": last_col.copy() for i in range(session['months_display'] - current_other_col_count)
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

    session['matrix'] = df2
    session['col_headers'] = list(session['matrix'].columns)
    session['row_headers'] = list(session['matrix'][session['matrix'].columns[0]])

    return render_template('les.html')





@app.route('/updatematrix', methods=['POST'])
def updatematrix():
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
    session['federaltaxes_status_future'] = request.form['federaltaxes_status_future']
    session['federaltaxes_status_future_month'] = request.form['federaltaxes_status_future_month']
    session['statetaxes_status_future'] = request.form['statetaxes_status_future']
    session['statetaxes_status_future_month'] = request.form['statetaxes_status_future_month']


    #variables
    basepay_headers = list(map(int, app.config['PAY_ACTIVE'].columns[1:]))
    basepay_headers.append(504) #add check for over 40+ years
    basepay_col = 0


    for i in range(1, len(session['col_headers'])):

        #update base pay
        for j in range(len(session['col_headers'])):
            if basepay_headers[j] <= session['months_in_service'] < basepay_headers[j+1]:
                basepay_col = basepay_headers[j]

        basepay_value = app.config['PAY_ACTIVE'].loc[app.config['PAY_ACTIVE']["Rank"] == session['rank_future'], str(basepay_col)]
        basepay_value = Decimal(basepay_value.iloc[0])

        if i >= session['col_headers'].index(session['rank_future_month']):
            session['matrix'].at[session['row_headers'].index("Base Pay"), session['col_headers'][i]] = round(basepay_value, 2)
        else:
            session['matrix'].at[session['row_headers'].index("Base Pay"), session['col_headers'][i]] = round(session['matrix'].at[session['row_headers'].index("Base Pay"), session['col_headers'][1]], 2)


        #update bas
        if i >= session['col_headers'].index(session['rank_future_month']):
            rank_index = app.config['RANKS_SHORT'].index(session['rank_future'])
            if rank_index > 8:
                bas_value = app.config['BAS_AMOUNT'][0]
            else:
                bas_value = app.config['BAS_AMOUNT'][1]
            session['matrix'].at[session['row_headers'].index("BAS"), session['col_headers'][i]] = round(bas_value, 2)
        else:
            session['matrix'].at[session['row_headers'].index("BAS"), session['col_headers'][i]] = round(session['matrix'].at[session['row_headers'].index("BAS"), session['col_headers'][1]], 2)


    #update BAH
    rank_over_months = []
    zipcode_over_months = []
    dependents_over_months = []

    for i in range(1, len(session['col_headers'])):
        if i >= session['col_headers'].index(session['rank_future_month']):
            rank_over_months.append(session['rank_future'])
        else:
            rank_over_months.append(session['rank_current'])

        if i >= session['col_headers'].index(session['zipcode_future_month']):
            zipcode_over_months.append(session['zipcode_future'])
        else:
            zipcode_over_months.append(session['zipcode_current'])

        if i >= session['col_headers'].index(session['dependents_future_month']):
            dependents_over_months.append(session['dependents_future'])
        else:
            dependents_over_months.append(session['dependents_current'])

    for i in range(1, len(session['col_headers'])):
        mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([zipcode_over_months[i-1]])].stack()
        mha_search_row = mha_search.index[0][0]
        session['mha_future'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
        session['mha_future_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]
        
        if dependents_over_months[i-1] > 0:
            bah_df = app.config['BAH_WITH_DEPENDENTS']
        else:
            bah_df = app.config['BAH_WITHOUT_DEPENDENTS']

        bah_value = bah_df.loc[bah_df["MHA"] == session['mha_future'], rank_over_months[i-1]]
        bah_value = bah_value.iloc[0]
        bah_value = Decimal(float(bah_value))

        session['matrix'].at[session['row_headers'].index("BAH"), session['col_headers'][i]] = round(bah_value, 2)



    #update gross pay
    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("Gross Pay"), session['col_headers'][i]] = round(Decimal(session['matrix'][session['col_headers'][i]][:-5][session['matrix'][session['col_headers'][i]][:-5] > 0].sum()), 2)

    #update taxable pay
    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("Taxable Pay"), session['col_headers'][i]] = calculate_taxablepay(session['col_headers'][i])

    #update non-taxable pay
    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("Non-Taxable Pay"), session['col_headers'][i]] = calculate_nontaxablepay(session['col_headers'][i])



    #update federal tax rate
    session['federaltaxes_status_over_months'] = []
    for i in range(1, len(session['col_headers'])):
        if i >= session['col_headers'].index(session['federaltaxes_status_future_month']):
            session['federaltaxes_status_over_months'].append(session['federaltaxes_status_future'])
        else:
            session['federaltaxes_status_over_months'].append(session['federaltaxes_status_current'])

    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("Federal Taxes"), session['col_headers'][i]] = round(-Decimal(calculate_federaltaxes(session['col_headers'][i], i)), 2)


    #update state tax rate
    session['statetaxes_status_over_months'] = []
    for i in range(1, len(session['col_headers'])):
        if i >= session['col_headers'].index(session['statetaxes_status_future_month']):
            session['statetaxes_status_over_months'].append(session['statetaxes_status_future'])
        else:
            session['statetaxes_status_over_months'].append(session['stateltaxes_status_current'])

    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("State Taxes"), session['col_headers'][i]] = round(-Decimal(calculate_statetaxes(session['col_headers'][i], i)), 2)


    #update fica - social security
    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("FICA - Social Security"), session['col_headers'][i]] = round(-Decimal(session['matrix'].at[session['row_headers'].index("Taxable Pay"), session['col_headers'][i]] * app.config['FICA_SOCIALSECURITY_TAX_RATE']), 2)

    #update fica-medicare
    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("FICA - Medicare"), session['col_headers'][i]] = round(-Decimal(session['matrix'].at[session['row_headers'].index("Taxable Pay"), session['col_headers'][i]] * app.config['FICA_MEDICARE_TAX_RATE']), 2)

    #update sgli
    for i in range(1, len(session['col_headers'])):
        if i >= session['col_headers'].index(session['sgli_future_month']):
            session['matrix'].at[session['row_headers'].index("SGLI"), session['col_headers'][i]] = -session['sgli_future']
        else:
            session['matrix'].at[session['row_headers'].index("SGLI"), session['col_headers'][i]] = session['matrix'].at[session['row_headers'].index("SGLI"), session['col_headers'][1]]


    #update total taxes, net pay
    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("Total Taxes"), session['col_headers'][i]] = calculate_totaltaxes(session['col_headers'][i])
        session['matrix'].at[session['row_headers'].index("Net Pay"), session['col_headers'][i]] = round(Decimal(session['matrix'][session['col_headers'][i]][:-5].sum()), 2)

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





def calculate_statetaxes(column, i):
    i = i - 1
    taxable_income = session['matrix'].at[list(session['matrix'][session['matrix'].columns[0]]).index("Taxable Pay"), column] * 12
    taxable_income = round(taxable_income, 2)

    brackets = app.config['STATE_TAX_RATE'][app.config['STATE_TAX_RATE']['Status'].str.lower() == session['statetaxes_status_over_months'][i].lower()]
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
    tp += Decimal(session['matrix'].at[list(session['matrix'][session['matrix'].columns[0]]).index("Base Pay"), column])
    return round(tp, 2)

def calculate_nontaxablepay(column):
    ntp = 0
    ntp += session['matrix'].at[list(session['matrix'][session['matrix'].columns[0]]).index("BAS"), column]
    ntp += session['matrix'].at[list(session['matrix'][session['matrix'].columns[0]]).index("BAH"), column]
    return round(ntp, 2)

def calculate_totaltaxes(column):
    return Decimal((session['matrix'].at[list(session['matrix'][session['matrix'].columns[0]]).index("Federal Taxes"), column]) + (session['matrix'].at[list(session['matrix'][session['matrix'].columns[0]]).index("State Taxes"), column]))



def months_in_service(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


@app.route('/exportmatrix', methods=['POST'])
def exportmatrix():
    session['export_type'] = request.form['export_type']

    print("export type: ", session['export_type'])

    if session['export_type'] == "excel":
        session['matrix'].to_excel("payles.xlsx")
    elif session['export_type'] == "csv":
        session['matrix'].to_csv("payles.csv", index=False)
    else:
        print("no export type found")

    return ('', 204)




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