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

app = Flask(__name__)
app.config.from_object(Config)
Session(app)



#entitlements
basepay = [0, 0, 0, 0, 0, 0, 0]
bas = [0, 0, 0, 0, 0, 0, 0]
bah = [0, 0, 0, 0, 0, 0, 0]
ueainitial = [0, 0, 0, 0, 0, 0, 0]
advancedebt = [0, 0, 0, 0, 0, 0, 0]
pcsmember = [0, 0, 0, 0, 0, 0, 0]

#deductions
federaltaxes = [0, 0, 0, 0, 0, 0, 0]
ficasocsecurity = [0, 0, 0, 0, 0, 0, 0]
ficamedicare = [0, 0, 0, 0, 0, 0, 0]
sgli = [0, 0, 0, 0, 0, 0, 0]
statetaxes = [0, 0, 0, 0, 0, 0, 0]
rothtsp = [0, 0, 0, 0, 0, 0, 0]
midmonthpay = 0
debt = [0, 0, 0, 0, 0, 0, 0]
partialpay = [0, 0, 0, 0, 0, 0, 0]
pcsmembers = [0, 0, 0, 0, 0, 0, 0]

#allotments


#calculations
taxablepay = [0, 0, 0, 0, 0, 0, 0]
nontaxablepay = [0, 0, 0, 0, 0, 0, 0]
totaltaxes = [0, 0, 0, 0, 0, 0, 0]
grosspay = [0, 0, 0, 0, 0, 0, 0]
netpay = [0, 0, 0, 0, 0, 0, 0]



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
                    for i in range(len(session['basepay'])):
                        session['basepay'][i] = Decimal(les_text[(les_text.index('BASE')+2)])
                else:
                    for i in range(len(session['basepay'])):
                        session['basepay'][i] = 0

                #find BAS
                if 'BAS' in les_text:
                    for i in range(len(session['bas'])):
                        session['bas'][i] = Decimal(les_text[(les_text.index('BAS')+1)])
                else:
                    for i in range(len(session['bas'])):
                        session['bas'][i] = 0

                #find BAH
                if 'BAH' in les_text:
                    for i in range(len(session['bah'])):
                        session['bah'][i] = Decimal(les_text[(les_text.index('BAH')+1)])
                else:
                    for i in range(len(session['bah'])):
                        session['bah'][i] = 0

                #find uea initial
                if 'UEA' in les_text and les_text[les_text.index('UEA')+1] == "INITIAL":
                    session['ueainitial'][0] = Decimal(les_text[(les_text.index('UEA')+2)])
                else:
                    session['ueainitial'][0] = 0

                #find advance debt
                if 'ADVANCE' in les_text and les_text[les_text.index('ADVANCE')+1] == "DEBT":
                    session['advancedebt'][0] = Decimal(les_text[(les_text.index('ADVANCE')+2)])
                else:
                    session['advancedebt'][0] = 0

                #find pcs member
                if 'PCS' in les_text and les_text[les_text.index('PCS')+1] == "MEMBER":
                    session['pcsmember'][0] = Decimal(les_text[(les_text.index('PCS')+2)])
                else:
                    session['pcsmember'][0] = 0

                #find federal taxes
                if 'FEDERAL' in les_text and les_text[les_text.index('FEDERAL')+1] == "TAXES":
                    for i in range(len(session['federaltaxes'])):
                        session['federaltaxes'][i] = Decimal(les_text[(les_text.index('FEDERAL')+2)])
                else:
                    for i in range(len(session['federaltaxes'])):
                        session['federaltaxes'][i] = 0

                #find FICA - Social Security
                if 'SECURITY' in les_text:
                    for i in range(len(session['ficasocsecurity'])):
                        session['ficasocsecurity'][i] = Decimal(les_text[(les_text.index('SECURITY')+1)])
                else:
                    for i in range(len(session['ficasocsecurity'])):
                        session['ficasocsecurity'][i] = 0

                #find FICA - Medicare
                if 'FICA-MEDICARE' in les_text:
                    for i in range(len(session['ficamedicare'])):
                        session['ficamedicare'][i] = Decimal(les_text[(les_text.index('FICA-MEDICARE')+1)])
                else:
                    for i in range(len(session['ficamedicare'])):
                        session['ficamedicare'][i] = 0

                #find SGLI
                if 'SGLI' in les_text:
                    for i in range(len(sgli)):
                        session['sgli'][i] = Decimal(les_text[(les_text.index('SGLI')+1)])
                    sgli_selected = sgli[1]
                else:
                    for i in range(len(sgli)):
                        session['sgli'][i] = 0
                session['sgli_future'] = session['sgli'][0]

                #find state taxes
                if 'STATE' in les_text and les_text[les_text.index('STATE')+1] == "TAXES":
                    for i in range(len(statetaxes)):
                        session['statetaxes'][i] = Decimal(les_text[(les_text.index('STATE')+2)])
                else:
                    for i in range(len(statetaxes)):
                        session['statetaxes'][i] = 0

                #find Roth TSP
                if 'ROTH' in les_text:
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
                    session['partialpay'][0] = Decimal(les_text[(les_text.index('PARTIAL')+2)])
                else:
                    session['partialpay'][0] = 0

                #find pcs members
                if 'PCS' in les_text and les_text[les_text.index('PCS')+1] == "MEMBERS":
                    session['pcsmembers'][0] = Decimal(les_text[(les_text.index('PCS')+2)])
                else:
                    session['pcsmembers'][0] = 0

                #find debt
                if 'DEBT' in les_text and les_text[les_text.index('DEBT')-1] != "ADVANCE":
                    debt[0] = Decimal(les_text[(les_text.index('DEBT')+1)])
                else:
                    debt[0] = 0

                #update total taxes
                for i in range(len(session['totaltaxes'])):
                    session['totaltaxes'][i] = session['federaltaxes'][i] + session['statetaxes'][i]

                #update gross pay:
                for i in range(len(session['grosspay'])):
                    session['grosspay'][i] = session['basepay'][i] + session['bas'][i] + session['bah'][i] + session['ueainitial'][i] + session['advancedebt'][i] + session['pcsmember'][i]

                #update net pay:
                for i in range(len(session['netpay'])):
                    session['netpay'][i] = session['grosspay'][i] - session['federaltaxes'][i] - session['ficasocsecurity'][i] - session['ficamedicare'][i] - session['sgli'][i] - session['statetaxes'][i] - session['rothtsp'][i] - session['debt'][i] - session['partialpay'][i] - session['pcsmembers'][i]


                les_pdf.close()

            return render_template('les.html')

    return 'File upload failed'



@app.route('/updatematrix', methods=['POST'])
def updatematrix():

    session['rank_future'] = request.form['rank_future']
    session['rank_future_month'] = request.form['rank_future_month']
    session['zipcode_future'] = request.form['zipcode_future']
    session['zipcode_future_month'] = request.form['zipcode_future_month']
    session['dependents_future'] = request.form['dependents_future']
    session['dependents_future_month'] = request.form['dependents_future_month']
    session['sgli_future'] = request.form['sgli_future']
    session['sgli_future_month'] = request.form['sgli_future_month']
    session['state_future'] = request.form['state_future']
    session['state_future_month'] = request.form['state_future_month']
    session['rothtsp_future'] = request.form['rothtsp_future']
    session['rothtsp_future_month'] = request.form['rothtsp_future_month']


    #update zipcode




    #update SGLI
    for i in range(len(session['sgli'])):
        if i >= session['months'].index(session['sgli_future_month']) and i > 0:
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