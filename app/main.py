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
import numpy as np

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

@app.route('/')
def index():

    #entitlements
    session['basepay'] = [0, 0, 0, 0, 0, 0, 0]
    session['bas'] = [0, 0, 0, 0, 0, 0, 0]
    session['bah'] = [0, 0, 0, 0, 0, 0, 0]
    session['ueainitial'] = [0, 0, 0, 0, 0, 0, 0]
    session['advancedebt'] = [0, 0, 0, 0, 0, 0, 0]
    session['pcsmember'] = [0, 0, 0, 0, 0, 0, 0]

    #deductions
    session['federaltaxes'] = [0, 0, 0, 0, 0, 0, 0]
    session['ficasocsecurity'] = [0, 0, 0, 0, 0, 0, 0]
    session['ficamedicare'] = [0, 0, 0, 0, 0, 0, 0]
    session['sgli'] = [0, 0, 0, 0, 0, 0, 0]
    session['statetaxes'] = [0, 0, 0, 0, 0, 0, 0]
    session['rothtsp'] = [0, 0, 0, 0, 0, 0, 0]
    session['midmonthpay'] = 0
    session['debt'] = [0, 0, 0, 0, 0, 0, 0]
    session['partialpay'] = [0, 0, 0, 0, 0, 0, 0]
    session['pcsmembers'] = [0, 0, 0, 0, 0, 0, 0]


    session['months'] = ["", "", "", "", "", "", ""]
    session['state_current'] = ""
    session['state_future'] = ""
    session['state_future_month'] = ""
    session['rank_current'] = ""
    session['rank_future'] = ""
    session['rank_future_month'] = ""
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

    session['taxablepay'] = [0, 0, 0, 0, 0, 0, 0]
    session['nontaxablepay'] = [0, 0, 0, 0, 0, 0, 0]
    session['totaltaxes'] = [0, 0, 0, 0, 0, 0, 0]
    session['grosspay'] = [0, 0, 0, 0, 0, 0, 0]
    session['netpay'] = [0, 0, 0, 0, 0, 0, 0]

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
                        for i in range(session['months_display']+1):
                           matrix_months.append(app.config['MONTHS_SHORT'][(app.config['MONTHS_SHORT'].index(x)+i) % 12])

                        for i in range(len(session['months'])):
                            session['months'][i] = app.config['MONTHS_SHORT'][(app.config['MONTHS_SHORT'].index(x)+i) % 12]
                        session['state_future_month'] = session['months'][1]
                        session['rank_future_month'] = session['months'][1]
                        session['zipcode_future_month'] = session['months'][1]
                        session['sgli_future_month'] = session['months'][1]
                        session['rothtsp_future_month'] = session['months'][1]
                        session['dependents_future_month'] = session['months'][1]
                        break
                    else:
                        for i in range(len(session['months'])):
                            session['months[i]'] = "no month"

                #find rank
                for x in app.config['RANKS_SHORT']:
                    if x in les_text and les_text[les_text.index(x)+9] == "ENTITLEMENTS":
                        session['rank_current'] = x
                        break
                    else:
                        session['rank_current'] = "no rank found"
                session['rank_future'] = session['rank_current']

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
                    for i in range(session['months_display']+1):
                        matrix_basepay.append(Decimal(les_text[(les_text.index('BASE')+2)]))
                        
                    matrix_basepay2 = [matrix_basepay]
                    session['matrix'] = pd.DataFrame(matrix_basepay2, columns=matrix_months)

                    #session['matrix'].loc[len(session['matrix'])] = matrix_basepay


                    for i in range(len(session['basepay'])):
                        session['basepay'][i] = Decimal(les_text[(les_text.index('BASE')+2)])
                else:
                    for i in range(len(session['basepay'])):
                        session['basepay'][i] = 0

                


                #find BAS
                if 'BAS' in les_text:
                    row = ["BAS"]
                    for i in range(session['months_display']+1):
                        row.append(Decimal(les_text[(les_text.index('BAS')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row


                    for i in range(len(session['bas'])):
                        session['bas'][i] = Decimal(les_text[(les_text.index('BAS')+1)])
                else:
                    for i in range(len(session['bas'])):
                        session['bas'][i] = 0

                #find BAH
                if 'BAH' in les_text:
                    row = ["BAH"]
                    for i in range(session['months_display']+1):
                        row.append(Decimal(les_text[(les_text.index('BAH')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row

                    for i in range(len(session['bah'])):
                        session['bah'][i] = Decimal(les_text[(les_text.index('BAH')+1)])
                else:
                    for i in range(len(session['bah'])):
                        session['bah'][i] = 0

                #find uea initial
                if 'UEA' in les_text and les_text[les_text.index('UEA')+1] == "INITIAL":
                    row = ["UEA Initial", Decimal(les_text[(les_text.index('UEA')+2)])]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                    session['ueainitial'][0] = Decimal(les_text[(les_text.index('UEA')+2)])
                else:
                    session['ueainitial'][0] = 0

                #find advance debt
                if 'ADVANCE' in les_text and les_text[les_text.index('ADVANCE')+1] == "DEBT":
                    row = ["Advance Debt", Decimal(les_text[(les_text.index('ADVANCE')+2)])]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                    session['advancedebt'][0] = Decimal(les_text[(les_text.index('ADVANCE')+2)])
                else:
                    session['advancedebt'][0] = 0

                #find pcs member
                if 'PCS' in les_text and les_text[les_text.index('PCS')+1] == "MEMBER":
                    row = ["PCS Member", Decimal(les_text[(les_text.index('PCS')+2)])]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row

                    session['pcsmember'][0] = Decimal(les_text[(les_text.index('PCS')+2)])
                else:
                    session['pcsmember'][0] = 0




                #find federal taxes
                if 'FEDERAL' in les_text and les_text[les_text.index('FEDERAL')+1] == "TAXES":
                    row = ["Federal Taxes"]
                    for i in range(session['months_display']+1):
                        row.append(-Decimal(les_text[(les_text.index('FEDERAL')+2)]))
                    session['matrix'].loc[len(session['matrix'])] = row


                    for i in range(len(session['federaltaxes'])):
                        session['federaltaxes'][i] = Decimal(les_text[(les_text.index('FEDERAL')+2)])
                else:
                    for i in range(len(session['federaltaxes'])):
                        session['federaltaxes'][i] = 0

                #find FICA - Social Security
                if 'SECURITY' in les_text:
                    row = ["FICA - Social Security"]
                    for i in range(session['months_display']+1):
                        row.append(-Decimal(les_text[(les_text.index('SECURITY')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row


                    for i in range(len(session['ficasocsecurity'])):
                        session['ficasocsecurity'][i] = Decimal(les_text[(les_text.index('SECURITY')+1)])
                else:
                    for i in range(len(session['ficasocsecurity'])):
                        session['ficasocsecurity'][i] = 0

                #find FICA - Medicare
                if 'FICA-MEDICARE' in les_text:
                    row = ["FICA - Medicare"]
                    for i in range(session['months_display']+1):
                        row.append(-Decimal(les_text[(les_text.index('FICA-MEDICARE')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row


                    for i in range(len(session['ficamedicare'])):
                        session['ficamedicare'][i] = Decimal(les_text[(les_text.index('FICA-MEDICARE')+1)])
                else:
                    for i in range(len(session['ficamedicare'])):
                        session['ficamedicare'][i] = 0

                #find SGLI
                if 'SGLI' in les_text:
                    row = ["SGLI"]
                    for i in range(session['months_display']+1):
                        row.append(-Decimal(les_text[(les_text.index('SGLI')+1)]))
                    session['matrix'].loc[len(session['matrix'])] = row


                    for i in range(len(session['sgli'])):
                        session['sgli'][i] = Decimal(les_text[(les_text.index('SGLI')+1)])
                    session['sgli_future'] = session['sgli'][1]
                else:
                    for i in range(len(session['sgli'])):
                        session['sgli'][i] = 0
                session['sgli_future'] = session['sgli'][0]

                #find state taxes
                if 'STATE' in les_text and les_text[les_text.index('STATE')+1] == "TAXES":
                    row = ["State Taxes"]
                    for i in range(session['months_display']+1):
                        row.append(-Decimal(les_text[(les_text.index('STATE')+2)]))
                    session['matrix'].loc[len(session['matrix'])] = row


                    for i in range(len(session['statetaxes'])):
                        session['statetaxes'][i] = Decimal(les_text[(les_text.index('STATE')+2)])
                else:
                    row = ["State Taxes"]
                    for i in range(session['months_display']+1):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row
                    
                    
                    for i in range(len(session['statetaxes'])):
                        session['statetaxes'][i] = 0

                #find Roth TSP
                if 'ROTH' in les_text:
                    row = ["Roth TSP"]
                    for i in range(session['months_display']+1):
                        row.append(-Decimal(les_text[(les_text.index('ROTH')+2)]))
                    session['matrix'].loc[len(session['matrix'])] = row


                    for i in range(len(session['rothtsp'])):
                        session['rothtsp'][i] = Decimal(les_text[(les_text.index('ROTH')+2)])
                else:
                    for i in range(len(session['rothtsp'])):
                        session['rothtsp'][i] = 0
                session['rothtsp_future'] = session['rothtsp'][0]

                #find mid-month-pay
                if 'MID-MONTH-PAY' in les_text:


                    session['midmonthpay'] = Decimal(les_text[(les_text.index('MID-MONTH-PAY')+1)])
                else:
                    session['midmonthpay'] = 0

                #find partial pay
                if 'PARTIAL' in les_text and les_text[les_text.index('PARTIAL')+1] == "PAY":
                    row = ["Partial Pay", -Decimal(les_text[(les_text.index('PARTIAL')+2)])]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                    session['partialpay'][0] = Decimal(les_text[(les_text.index('PARTIAL')+2)])
                else:
                    session['partialpay'][0] = 0

                #find pcs members
                if 'PCS' in les_text and les_text[les_text.index('PCS')+1] == "MEMBERS":
                    row = ["PCS Members", -Decimal(les_text[(les_text.index('PCS')+2)])]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                    session['pcsmembers'][0] = Decimal(les_text[(les_text.index('PCS')+2)])
                else:
                    session['pcsmembers'][0] = 0

                #find debt
                if 'DEBT' in les_text and les_text[les_text.index('DEBT')-1] != "ADVANCE":
                    row = ["Debt", -Decimal(les_text[(les_text.index('DEBT')+1)])]
                    for i in range(session['months_display']):
                        row.append(0)
                    session['matrix'].loc[len(session['matrix'])] = row


                    session['debt'][0] = Decimal(les_text[(les_text.index('DEBT')+1)])
                else:
                    session['debt'][0] = 0



                #update total taxes
                for i in range(len(session['totaltaxes'])):
                    session['totaltaxes'][i] = session['federaltaxes'][i] + session['statetaxes'][i]

                #update gross pay:
                for i in range(len(session['grosspay'])):
                    session['grosspay'][i] = session['basepay'][i] + session['bas'][i] + session['bah'][i] + session['ueainitial'][i] + session['advancedebt'][i] + session['pcsmember'][i]

                #update net pay:
                for i in range(len(session['netpay'])):
                    session['netpay'][i] = session['grosspay'][i] - session['federaltaxes'][i] - session['ficasocsecurity'][i] - session['ficamedicare'][i] - session['sgli'][i] - session['statetaxes'][i] - session['rothtsp'][i] - session['debt'][i] - session['partialpay'][i] - session['pcsmembers'][i]



                #taxable pay
                row = ["Taxable Pay"]
                for i in range(session['months_display']+1):
                    x = 0
                    row.append(x)
                session['matrix'].loc[len(session['matrix'])] = row

                #non-taxable pay
                row = ["Non-Taxable Pay"]
                for i in range(session['months_display']+1):
                    x = 0
                    row.append(x)
                session['matrix'].loc[len(session['matrix'])] = row

                #total taxes
                row = ["Total Taxes"]
                for i in range(session['months_display']+1):
                    x = 0
                    row.append(x)
                session['matrix'].loc[len(session['matrix'])] = row

                #gross pay
                row_grosspay = ["Gross Pay"]
                for column in session['matrix'].columns[1:]:
                    total = session['matrix'][column][:-3][session['matrix'][column][:-3] > 0].sum()
                    row_grosspay.append(total)
                session['matrix'].loc[len(session['matrix'])] = row_grosspay


                #net pay
                row_netpay = ["Net Pay"]
                for column in session['matrix'].columns[1:]:
                    net_pay = session['matrix'][column][:-4].sum()
                    row_netpay.append(net_pay)
                session['matrix'].loc[len(session['matrix'])] = row_netpay

                



                session['matrix_html'] = session['matrix'].to_html()



                les_pdf.close()

            return render_template('les.html')

    return 'File upload failed'



@app.route('/updatematrix', methods=['POST'])
def updatematrix():

    col_headers = list(session['matrix'].columns)
    row_headers = list(session['matrix'][session['matrix'].columns[0]])

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




    #update bah
    mha_search = app.config['MHA_ZIPCODES'][app.config['MHA_ZIPCODES'].isin([session['zipcode_future']])].stack()
    mha_search_row = mha_search.index[0][0]
    mha_search_col = mha_search.index[0][1]
    session['mha_future'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA"]
    session['mha_future_name'] = app.config['MHA_ZIPCODES'].loc[mha_search_row, "MHA_NAME"]

    if session['dependents_future'] > 0:
        bah_search_row = app.config['BAH_WITH_DEPENDENTS'][app.config['BAH_WITH_DEPENDENTS']["MHA"] == session['mha_future']].index
        bah_search_col = app.config['BAH_WITH_DEPENDENTS'].loc[bah_search_row, session['rank_future']]
        for i in range(len(session['bah'])):
            if i > 0 and i >= session['months'].index(session['zipcode_future_month']):
                session['bah'][i] = bah_search_col.apply(Decimal)
            else:
                session['bah'][i] = session['bah'][0]
    else:
        bah_search_row = app.config['BAH_WITHOUT_DEPENDENTS'][app.config['BAH_WITHOUT_DEPENDENTS']["MHA"] == session['mha_future']].index
        bah_search_col = app.config['BAH_WITHOUT_DEPENDENTS'].loc[bah_search_row, session['rank_future']]
        for i in range(len(session['bah'])):
            if i > 0 and i >= session['months'].index(session['zipcode_future_month']):
                session['bah'][i] = bah_search_col.apply(Decimal)
            else:
                session['bah'][i] = session['bah'][0]


    #update sgli
    for i in range(1, len(session['matrix'].columns)):
        if i >= col_headers.index(session['sgli_future_month']):
            session['matrix'].at[row_headers.index("SGLI"), col_headers[i]] = -session['sgli_future']
        else:
            session['matrix'].at[row_headers.index("SGLI"), col_headers[i]] = session['matrix'].at[row_headers.index("SGLI"), col_headers[1]]



    #update SGLI
    for i in range(len(session['sgli'])):
        if i > 0 and i >= session['months'].index(session['sgli_future_month']):
            session['sgli'][i] = Decimal(session['sgli_future'])
        else:
            session['sgli'][i] = session['sgli'][0]


    #update total taxes
    for i in range(len(session['totaltaxes'])):
        session['totaltaxes'][i] = session['federaltaxes'][i] + session['statetaxes'][i]

    #update gross pay:
    for i in range(len(session['grosspay'])):
        session['grosspay'][i] = session['basepay'][i] + session['bas'][i] + session['bah'][i] + session['ueainitial'][i] + session['advancedebt'][i] + session['pcsmember'][i]

    #update net pay:
    for i in range(len(session['netpay'])):
        session['netpay'][i] = session['grosspay'][i] - session['federaltaxes'][i] - session['ficasocsecurity'][i] - session['ficamedicare'][i] - session['sgli'][i] - session['statetaxes'][i] - session['rothtsp'][i] - session['debt'][i] - session['partialpay'][i] - session['pcsmembers'][i]


    session['matrix_html'] = session['matrix'].to_html()

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