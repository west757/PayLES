from flask import Flask
from flask import request, render_template, make_response, jsonify, session
from flask_session import Session
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
#from pdf2image import convert_from_path
import pdfplumber
import os
import pandas as pd

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

@app.route('/')
def index():
    session['state_current'] = ""
    session['state_future'] = ""
    session['state_future_month'] = ""
    session['rank_current'] = ""
    session['rank_future'] = ""
    session['rank_future_month'] = ""
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

    session['months_display'] = 6

    return render_template('index.html')


@app.route('/uploadfile', methods=['POST'])
def uploadfile():

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

                #find month
                for x in app.config['MONTHS_SHORT']:
                    if x in les_text:
                        matrix_months = ["Variable"]
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

                #find years of service
                #if 'PACIDN' in les_text:
                #    session['zipcode_current'] = Decimal(les_text[(les_text.index('ENTITLEMENTS')+5)])
                #else:
                #    session['zipcode_current'] = 0
                #session['zipcode_future'] = session['zipcode_current']

                #find zip code
                if 'PACIDN' in les_text:
                    session['zipcode_current'] = Decimal(les_text[(les_text.index('PACIDN')+3)])
                else:
                    session['zipcode_current'] = 0
                session['zipcode_future'] = session['zipcode_current']

                #find MHA
                mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([session['zipcode_current']])].stack()
                mha_search_row = mha_search.index[0][0]
                mha_search_col = mha_search.index[0][1]

                session['mha_current'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
                session['mha_current_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]
                session['mha_future'] = session['mha_current']
                session['mha_future_name'] = session['mha_current_name']

                #find dependents
                if 'Depns' in les_text:
                    session['dependents_current'] = Decimal(les_text[(les_text.index('PACIDN')+7)])
                else:
                    session['dependents_current'] = 0
                session['dependents_future'] = session['dependents_current']

                #find state
                for x in app.config['STATES_SHORT']:
                    if x in les_text and les_text[(les_text.index(x)-1)] == "TAXES":
                        session['state_current'] = x
                        break
                    else:
                        session['state_current'] = "no state found"
                session['state_future'] = session['state_current']


                #find base pay
                if 'BASE' in les_text:
                    matrix_basepay = ["Base Pay"]
                    for i in range(session['months_display']):
                        matrix_basepay.append(Decimal(les_text[(les_text.index('BASE')+2)]))
                    matrix_basepay2 = [matrix_basepay]
                
                session['matrix'] = pd.DataFrame(matrix_basepay2, columns=matrix_months)

                #find BAS
                if 'BAS' in les_text:
                    row = ["BAS"]
                    for i in range(session['months_display']):
                        row.append(Decimal(les_text[(les_text.index('BAS')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find BAH
                if 'BAH' in les_text:
                    row = ["BAH"]
                    for i in range(session['months_display']):
                        row.append(Decimal(les_text[(les_text.index('BAH')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find uea initial
                if 'UEA' in les_text and les_text[les_text.index('UEA')+1] == "INITIAL":
                    row = ["UEA Initial", Decimal(les_text[(les_text.index('UEA')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                #find advance debt
                if 'ADVANCE' in les_text and les_text[les_text.index('ADVANCE')+1] == "DEBT":
                    row = ["Advance Debt", Decimal(les_text[(les_text.index('ADVANCE')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find pcs member
                if 'PCS' in les_text and les_text[les_text.index('PCS')+1] == "MEMBER":
                    row = ["PCS Member", Decimal(les_text[(les_text.index('PCS')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                #find federal taxes
                if 'FEDERAL' in les_text and les_text[les_text.index('FEDERAL')+1] == "TAXES":
                    row = ["Federal Taxes"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('FEDERAL')+2)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find FICA - Social Security
                if 'SECURITY' in les_text:
                    row = ["FICA - Social Security"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('SECURITY')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find FICA - Medicare
                if 'FICA-MEDICARE' in les_text:
                    row = ["FICA - Medicare"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('FICA-MEDICARE')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                #find SGLI
                if 'SGLI' in les_text:
                    row = ["SGLI"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('SGLI')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row


                #find state taxes
                if 'STATE' in les_text and les_text[les_text.index('STATE')+1] == "TAXES":
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
                if 'ROTH' in les_text:
                    row = ["Roth TSP"]
                    for i in range(session['months_display']):
                        row.append(-Decimal(les_text[(les_text.index('ROTH')+2)]))
                    session['matrix'].loc[len(session['matrix'])] = row
                else:
                    row = ["Roth TSP"]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find mid-month-pay
                #if 'MID-MONTH-PAY' in les_text:
                #    session['midmonthpay'] = Decimal(les_text[(les_text.index('MID-MONTH-PAY')+1)])
                #else:
                #    session['midmonthpay'] = 0

                #find partial pay
                if 'PARTIAL' in les_text and les_text[les_text.index('PARTIAL')+1] == "PAY":
                    row = ["Partial Pay", -Decimal(les_text[(les_text.index('PARTIAL')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find pcs members
                if 'PCS' in les_text and les_text[les_text.index('PCS')+1] == "MEMBERS":
                    row = ["PCS Members", -Decimal(les_text[(les_text.index('PCS')+2)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                #find debt
                if 'DEBT' in les_text and les_text[les_text.index('DEBT')-1] != "ADVANCE":
                    row = ["Debt", -Decimal(les_text[(les_text.index('DEBT')+1)])]
                    for i in range(session['months_display']-1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                #taxable pay
                row = ["Taxable Pay"]
                for i in range(session['months_display']):
                    x = 0
                    row.append(x)
                session['matrix'].loc[len(session['matrix'])] = row

                #non-taxable pay
                row = ["Non-Taxable Pay"]
                for i in range(session['months_display']):
                    x = 0
                    row.append(x)
                session['matrix'].loc[len(session['matrix'])] = row

                #total taxes
                row = ["Total Taxes"]
                for i in range(session['months_display']):
                    x = 0
                    row.append(x)
                session['matrix'].loc[len(session['matrix'])] = row

                #gross pay
                row_grosspay = ["Gross Pay"]
                for column in session['matrix'].columns[1:]:
                    row_grosspay.append(calculate_grosspay(column))
                session['matrix'].loc[len(session['matrix'])] = row_grosspay

                #net pay
                row_netpay = ["Net Pay"]
                for column in session['matrix'].columns[1:]:
                    row_netpay.append(calculate_netpay(column))
                session['matrix'].loc[len(session['matrix'])] = row_netpay


                session['col_headers'] = list(session['matrix'].columns)
                session['row_headers'] = list(session['matrix'][session['matrix'].columns[0]])

                les_pdf.close()

                #matrix_csv = session['matrix'].to_csv("matrix.csv", index=False)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], matrix_csv))

            return render_template('les.html') + render_template('inputs.html')

    return 'File upload failed'



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

    #update base pay
    #for i in range(1, len(session['col_headers'])):
    #    if i >= session['col_headers'].index(session['rank_future_month']):
    #        session['matrix'].at[session['row_headers'].index("Base Pay"), session['col_headers'][i]] = -session['sgli_future']
    #    else:
    #        session['matrix'].at[session['row_headers'].index("Base Pay"), session['col_headers'][i]] = session['matrix'].at[session['row_headers'].index("Base Pay"), session['col_headers'][1]]


    #update bah
    mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([session['zipcode_future']])].stack()
    mha_search_row = mha_search.index[0][0]
    session['mha_future'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
    session['mha_future_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]

    if session['dependents_future'] > 0:
        bah_df = app.config['BAH_WITH_DEPENDENTS']
    else:
        bah_df = app.config['BAH_WITHOUT_DEPENDENTS']

    # Find the BAH value based on MHA and rank
    bah_value = bah_df.loc[bah_df["MHA"] == session['mha_future'], session['rank_future']]
    print("bah value before iloc: ", bah_value)
    bah_value = bah_value.iloc[0]
    print("bah value after iloc: ", bah_value)
    print("")

    bah_row_index = session['row_headers'].index("BAH")

    for i in range(1, len(session['col_headers'])):
        # If the current month is greater than or equal to the future month of the zipcode or dependents
        if (i >= session['col_headers'].index(session['zipcode_future_month'])) or (i >= session['col_headers'].index(session['dependents_future_month'])):
            session['matrix'].at[bah_row_index, session['col_headers'][i]] = bah_value
        else:
            session['matrix'].at[bah_row_index, session['col_headers'][i]] = session['matrix'].at[bah_row_index, session['col_headers'][1]]



    #mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([session['zipcode_future']])].stack()
    #mha_search_row = mha_search.index[0][0]
    #mha_search_col = mha_search.index[0][1]
    #session['mha_future'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
    #session['mha_future_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]

    #if session['dependents_future'] > 0:
    #    bah_search_row = app.config['BAH_WITH_DEPENDENTS'][app.config['BAH_WITH_DEPENDENTS']["MHA"] == session['mha_future']].index
    #    bah_search_col = app.config['BAH_WITH_DEPENDENTS'].loc[bah_search_row, session['rank_future']]
    #    for i in range(1, len(session['col_headers'])):
    #        if i >= session['col_headers'].index(session['zipcode_future_month']):
    #            session['matrix'].at[session['row_headers'].index("BAH"), session['col_headers'][i]] = bah_search_col.apply(Decimal)
    #        else:
    #            session['matrix'].at[session['row_headers'].index("BAH"), session['col_headers'][i]] = session['matrix'].at[session['row_headers'].index("BAH"), session['col_headers'][1]]
            
            #if i > 0 and i >= session['months'].index(session['zipcode_future_month']):
            #    session['bah'][i] = bah_search_col.apply(Decimal)
            #else:
            #    session['bah'][i] = session['bah'][0]
    #else:
    #    bah_search_row = app.config['BAH_WITHOUT_DEPENDENTS'][app.config['BAH_WITHOUT_DEPENDENTS']["MHA"] == session['mha_future']].index
    #    bah_search_col = app.config['BAH_WITHOUT_DEPENDENTS'].loc[bah_search_row, session['rank_future']]
    #    for i in range(1, len(session['col_headers'])):
    #        if i >= session['col_headers'].index(session['zipcode_future_month']):
    #            session['matrix'].at[session['row_headers'].index("BAH"), session['col_headers'][i]] = bah_search_col.apply(Decimal)
    #        else:
    #            session['matrix'].at[session['row_headers'].index("BAH"), session['col_headers'][i]] = session['matrix'].at[session['row_headers'].index("BAH"), session['col_headers'][1]]
            #if i > 0 and i >= session['months'].index(session['zipcode_future_month']):
            #    session['bah'][i] = bah_search_col.apply(Decimal)
            #else:
            #    session['bah'][i] = session['bah'][0]


    #update sgli
    for i in range(1, len(session['col_headers'])):
        if i >= session['col_headers'].index(session['sgli_future_month']):
            session['matrix'].at[session['row_headers'].index("SGLI"), session['col_headers'][i]] = -session['sgli_future']
        else:
            session['matrix'].at[session['row_headers'].index("SGLI"), session['col_headers'][i]] = session['matrix'].at[session['row_headers'].index("SGLI"), session['col_headers'][1]]


    #update gross pay, net pay
    for i in range(1, len(session['col_headers'])):
        session['matrix'].at[session['row_headers'].index("Gross Pay"), session['col_headers'][i]] = calculate_grosspay(session['col_headers'][i])
        session['matrix'].at[session['row_headers'].index("Net Pay"), session['col_headers'][i]] = calculate_netpay(session['col_headers'][i])

    return render_template('les.html')



@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')


def calculate_grosspay(column):
    gp = session['matrix'][column][:-3][session['matrix'][column][:-3] > 0].sum()
    return gp

def calculate_netpay(column):
    np = session['matrix'][column][:-4].sum()
    return np


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