from calendar import month_name
from flask import Flask
from flask import request, render_template, request, make_response, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal

import pdfplumber
import os

#file extensions allowed
ALLOWED_EXTENSIONS = {'pdf'}
#location where files are uploaded to and stored for them to be accessed by the program
UPLOAD_FOLDER = 'C:/Users/blue/Documents/GitHub/PayLES/upload'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#sets the max content length of the uploaded file to 16MB, prevents massive files from overloading the server
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MONTHS_SHORT = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
STATES_LONG = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii',
               'Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota',
               'Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina',
               'North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas',
               'Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']
STATES_SHORT = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO',
                'MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
RANKS_SHORT = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9',
               'W1', 'W2', 'W3', 'W4', 'W5', 'O1E', 'O2E', 'O3E',
               'O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9']
SGLI_COVERAGES = [0, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000, 500000]
SGLI_PREMIUMS = [0, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31]


#variables
months = ["", "", "", "", "", "", ""]
state = ""
grade = ""
zipcode = 0

#entitlements
basepay = [0, 0, 0, 0, 0, 0, 0]
bas = [0, 0, 0, 0, 0, 0, 0]
bah = [0, 0, 0, 0, 0, 0, 0]
ueainitial = 0
advancedebt = 0
pcsmember = 0

#deductions
federaltaxes = [0, 0, 0, 0, 0, 0, 0]
ficasocsecurity = [0, 0, 0, 0, 0, 0, 0]
ficamedicare = [0, 0, 0, 0, 0, 0, 0]
sgli = [0, 0, 0, 0, 0, 0, 0]
statetaxes = [0, 0, 0, 0, 0, 0, 0]
rothtsp = [0, 0, 0, 0, 0, 0, 0]
midmonthpay = 0
debt = 0
partialpay = 0
pcsmembers = 0

#allotments


#calculations
grosspay = [0, 0, 0, 0, 0, 0, 0]
netpay = [0, 0, 0, 0, 0, 0, 0]


rank_selected = ""
rank_month_selected = ""
sgli_selected = 0
sgli_month_selected = ""
state_selected = 0
state_month_selected = ""
rothtsp_selected = 0
rothtsp_month_selected = ""




@app.route('/')
def home():
    return render_template('index.html', 
                           MONTHS_LONG=MONTHS_LONG, MONTHS_SHORT=MONTHS_SHORT, STATES_LONG=STATES_LONG, STATES_SHORT=STATES_SHORT, RANKS_SHORT=RANKS_SHORT,
                           SGLI_COVERAGES=SGLI_COVERAGES, SGLI_PREMIUMS=SGLI_PREMIUMS,
                           months=months, state=state, grade=grade, zipcode=zipcode,
                           basepay=basepay, bas=bas, bah=bah, ueainitial=ueainitial, advancedebt=advancedebt, pcsmember=pcsmember,
                           federaltaxes=federaltaxes, ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, sgli=sgli, statetaxes=statetaxes, rothtsp=rothtsp,
                           midmonthpay=midmonthpay, debt=debt, partialpay=partialpay, pcsmembers=pcsmembers,
                           grosspay=grosspay, netpay=netpay,
                           rank_selected=rank_selected, rank_month_selected=rank_month_selected, 
                           sgli_selected=sgli_selected,sgli_month_selected=sgli_month_selected,
                           state_selected=state_selected, state_month_selected=state_month_selected,
                           rothtsp_selected=rothtsp_selected, rothtsp_month_selected=rothtsp_month_selected)


@app.route('/uploadfile', methods=['POST'])
def uploadfile():

    global MONTHS_LONG
    global MONTHS_SHORT
    global STATES_LONG
    global STATES_SHORT
    global RANKS_SHORT
    global SGLI_COVERAGES
    global SGLI_PREMIUMS
    global months
    global state
    global grade
    global zipcode
    global basepay
    global bas
    global bah
    global ueainitial
    global advancedebt
    global pcsmember
    global federaltaxes
    global ficasocsecurity
    global ficamedicare
    global sgli
    global statetaxes
    global rothtsp
    global midmonthpay
    global debt
    global partialpay
    global pcsmembers
    global grosspay
    global netpay
    global rank_selected
    global rank_month_selected
    global sgli_selected
    global sgli_month_selected
    global state_selected
    global state_month_selected
    global rothtsp_selected
    global rothtsp_month_selected


    if 'file' not in request.files:
        return 'No file part in the request', 400

    if 'file' in request.files:
        file = request.files['file']

        #checks to see if  there is a file, if not then returns an error
        if file.filename == '':
            return 'No selected file', 400

        #checks to see if the file type is allowed, if not then returns an error
        #file types allowed defined in ALLOWED_EXTENSIONS variable
        if file and not allowed_file(file.filename):
            return 'File type not allowed', 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #start pdfplumber
            with pdfplumber.open(file) as les:
                #gets all the content of the first page of the LES
                page = les.pages[0]
                #creates a string of all text from the LES
                textstring = page.extract_text()
                #creates an array of all text separated by a space
                #avoids the problem of using specific indexes because indexes may change depending on text size
                text = textstring.split()

                #print(text)

                #find month
                for x in MONTHS_SHORT:
                    if x in text:
                        for i in range(len(months)):
                            months[i] = MONTHS_SHORT[(MONTHS_SHORT.index(x)+i) % 12]
                        sgli_month_selected = months[1]
                        break
                    else:
                        for i in range(len(months)):
                            months[i] = "no month"

                #find grade
                for x in RANKS_SHORT:
                    if x in text and text[text.index(x)+9] == "ENTITLEMENTS":
                        grade = x
                        break
                    else:
                        grade = "no grade found"

                #find base pay
                if 'BASE' in text:
                    for i in range(len(basepay)):
                        basepay[i] = Decimal(text[(text.index('BASE')+2)])
                else:
                    for i in range(len(basepay)):
                        basepay[i] = 0

                #find BAS
                if 'BAS' in text:
                    for i in range(len(bas)):
                        bas[i] = Decimal(text[(text.index('BAS')+1)])
                else:
                    for i in range(len(bas)):
                        bas[i] = 0

                #find BAH
                if 'BAH' in text:
                    for i in range(len(bah)):
                        bah[i] = Decimal(text[(text.index('BAH')+1)])
                else:
                    for i in range(len(bah)):
                        bah[i] = 0

                #find federal taxes
                if 'FEDERAL' in text and text[text.index('FEDERAL')+1] == "TAXES":
                    for i in range(len(federaltaxes)):
                        federaltaxes[i] = Decimal(text[(text.index('FEDERAL')+2)])
                else:
                    for i in range(len(federaltaxes)):
                        federaltaxes[i] = 0

                #find FICA - Social Security
                if 'SECURITY' in text:
                    for i in range(len(ficasocsecurity)):
                        ficasocsecurity[i] = Decimal(text[(text.index('SECURITY')+1)])
                else:
                    for i in range(len(ficasocsecurity)):
                        ficasocsecurity[i] = 0

                #find FICA - Medicare
                if 'FICA-MEDICARE' in text:
                    for i in range(len(ficamedicare)):
                        ficamedicare[i] = Decimal(text[(text.index('FICA-MEDICARE')+1)])
                else:
                    for i in range(len(ficamedicare)):
                        ficamedicare[i] = 0

                #find SGLI
                if 'SGLI' in text:
                    for i in range(len(sgli)):
                        sgli[i] = Decimal(text[(text.index('SGLI')+1)])
                else:
                    for i in range(len(sgli)):
                        sgli[i] = 0

                #find state taxes
                if 'STATE' in text and text[text.index('STATE')+1] == "TAXES":
                    for i in range(len(statetaxes)):
                        statetaxes[i] = Decimal(text[(text.index('STATE')+2)])
                else:
                    for i in range(len(statetaxes)):
                        statetaxes[i] = 0

                #find Roth TSP
                if 'ROTH' in text:
                    for i in range(len(rothtsp)):
                        rothtsp[i] = Decimal(text[(text.index('ROTH')+2)])
                else:
                    for i in range(len(rothtsp)):
                        rothtsp[i] = 0

                #find mid-month-pay
                if 'MID-MONTH-PAY' in text:
                    midmonthpay = Decimal(text[(text.index('MID-MONTH-PAY')+1)])
                else:
                    midmonthpay = 0

                #find gross pay
                if 'ENT' in text:
                    for i in range(len(grosspay)):
                        grosspay[i] = Decimal(text[(text.index('ENT')+1)])
                else:
                    for i in range(len(grosspay)):
                        grosspay[i] = 0

                #find net pay (takes mid-month pay into account)
                if '=NET' in text:
                    netpayinitial = Decimal(text[(text.index('=NET')+2)])
                    if midmonthpay != 0:
                        netpayinitial = netpayinitial + midmonthpay
                    for i in range(len(netpay)):
                        netpay[i] = netpayinitial
                else:
                    for i in range(len(netpay)):
                        netpay[i] = 0

                #find state
                for x in STATES_SHORT:
                    if (x in text) and (text[text.index(x)-1] == "TAXES"):
                        state = x
                        break
                    else:
                        state = "no state found"

                #find zip code
                if 'PACIDN' in text:
                    zipcode = Decimal(text[(text.index('PACIDN')+3)])
                else:
                    zipcode = 0


            return render_template('les.html', 
                                    MONTHS_LONG=MONTHS_LONG, MONTHS_SHORT=MONTHS_SHORT, STATES_LONG=STATES_LONG, STATES_SHORT=STATES_SHORT, RANKS_SHORT=RANKS_SHORT,
                                    SGLI_COVERAGES=SGLI_COVERAGES, SGLI_PREMIUMS=SGLI_PREMIUMS,
                                    months=months, state=state, grade=grade, zipcode=zipcode,
                                    basepay=basepay, bas=bas, bah=bah, ueainitial=ueainitial, advancedebt=advancedebt, pcsmember=pcsmember,
                                    federaltaxes=federaltaxes, ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, sgli=sgli, statetaxes=statetaxes, rothtsp=rothtsp,
                                    midmonthpay=midmonthpay, debt=debt, partialpay=partialpay, pcsmembers=pcsmembers,
                                    grosspay=grosspay, netpay=netpay,
                                    rank_selected=rank_selected, rank_month_selected=rank_month_selected, 
                                    sgli_selected=sgli_selected,sgli_month_selected=sgli_month_selected,
                                    state_selected=state_selected, state_month_selected=state_month_selected,
                                    rothtsp_selected=rothtsp_selected, rothtsp_month_selected=rothtsp_month_selected)

    return 'File upload failed'



@app.route('/updatematrix', methods=['POST'])
def updatematrix():

    global MONTHS_LONG
    global MONTHS_SHORT
    global STATES_LONG
    global STATES_SHORT
    global RANKS_SHORT
    global SGLI_COVERAGES
    global SGLI_PREMIUMS
    global months
    global state
    global grade
    global zipcode
    global basepay
    global bas
    global bah
    global ueainitial
    global advancedebt
    global pcsmember
    global federaltaxes
    global ficasocsecurity
    global ficamedicare
    global sgli
    global statetaxes
    global rothtsp
    global midmonthpay
    global debt
    global partialpay
    global pcsmembers
    global grosspay
    global netpay
    global rank_selected
    global rank_month_selected
    global sgli_selected
    global sgli_month_selected
    global state_selected
    global state_month_selected
    global rothtsp_selected
    global rothtsp_month_selected

    sgli_selected = request.form['sgli_selected']
    sgli_month_selected = request.form['sgli_month_selected']


    #update SGLI
    for i in range(len(sgli)):
        if i >= months.index(sgli_month_selected) and i > 0:
            sgli[i] = Decimal(sgli_selected)
        else:
            sgli[i] = sgli[0]

    #update gross pay:
    for i in range(len(grosspay)):
        grosspay[i] = basepay[i] + bas[i] + bah[i]

    #update net pay:
    for i in range(len(netpay)):
        netpay[i] = grosspay[i] - federaltaxes[i] - ficasocsecurity[i] - ficamedicare[i] - sgli[i] - statetaxes[i] - rothtsp[i]


    return render_template('les.html', 
                           MONTHS_LONG=MONTHS_LONG, MONTHS_SHORT=MONTHS_SHORT, STATES_LONG=STATES_LONG, STATES_SHORT=STATES_SHORT, RANKS_SHORT=RANKS_SHORT,
                           SGLI_COVERAGES=SGLI_COVERAGES, SGLI_PREMIUMS=SGLI_PREMIUMS,
                           months=months, state=state, grade=grade, zipcode=zipcode,
                           basepay=basepay, bas=bas, bah=bah, ueainitial=ueainitial, advancedebt=advancedebt, pcsmember=pcsmember,
                           federaltaxes=federaltaxes, ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, sgli=sgli, statetaxes=statetaxes, rothtsp=rothtsp,
                           midmonthpay=midmonthpay, debt=debt, partialpay=partialpay, pcsmembers=pcsmembers,
                           grosspay=grosspay, netpay=netpay,
                           rank_selected=rank_selected, rank_month_selected=rank_month_selected, 
                           sgli_selected=sgli_selected,sgli_month_selected=sgli_month_selected,
                           state_selected=state_selected, state_month_selected=state_month_selected,
                           rothtsp_selected=rothtsp_selected, rothtsp_month_selected=rothtsp_month_selected)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return 'File is too large', 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)