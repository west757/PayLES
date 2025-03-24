from flask import Flask
from flask import request, render_template, request, make_response, jsonify
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
#from pdf2image import convert_from_path
import pdfplumber
import os



app = Flask(__name__)
app.config.from_object(Config)



#variables
months = ["", "", "", "", "", "", ""]
state = ""
rank = ""
zipcode = 0
dependents = [0, 0, 0, 0, 0, 0, 0]
BAH_WITH_DEPENDENTS = []
BAH_WITHOUT_DEPENDENTS = []

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


#inputs
rank_selected = ""
rank_month_selected = ""
zipcode_selected = ""
zipcode_month_selected = ""
dependents_selected = 0
dependents_month_selected = ""
sgli_selected = 0
sgli_month_selected = ""
state_selected = ""
state_month_selected = ""
rothtsp_selected = 0
rothtsp_month_selected = ""



@app.route('/')
def index():
    return render_template('index.html', 
                           months=months, state=state, rank=rank, zipcode=zipcode, dependents=dependents,
                           basepay=basepay, bas=bas, bah=bah, ueainitial=ueainitial, advancedebt=advancedebt, pcsmember=pcsmember,
                           federaltaxes=federaltaxes, ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, sgli=sgli, statetaxes=statetaxes, rothtsp=rothtsp,
                           midmonthpay=midmonthpay, debt=debt, partialpay=partialpay, pcsmembers=pcsmembers,
                           taxablepay=taxablepay, nontaxablepay=nontaxablepay, totaltaxes=totaltaxes, grosspay=grosspay, netpay=netpay,
                           rank_selected=rank_selected, rank_month_selected=rank_month_selected, 
                           zipcode_selected=zipcode_selected, zipcode_month_selected=zipcode_month_selected,
                           dependents_selected=dependents_selected, dependents_month_selected=dependents_month_selected,
                           sgli_selected=sgli_selected,sgli_month_selected=sgli_month_selected,
                           state_selected=state_selected, state_month_selected=state_month_selected,
                           rothtsp_selected=rothtsp_selected, rothtsp_month_selected=rothtsp_month_selected)


@app.route('/uploadfile', methods=['POST'])
def uploadfile():

    global months
    global state
    global rank
    global zipcode
    global dependents
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
    global taxablepay
    global nontaxablepay
    global totaltaxes
    global grosspay
    global netpay
    global rank_selected
    global rank_month_selected
    global zipcode_selected
    global zipcode_month_selected
    global dependents_selected
    global dependents_month_selected
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
                        for i in range(len(months)):
                            months[i] = app.config['MONTHS_SHORT'][(app.config['MONTHS_SHORT'].index(x)+i) % 12]
                        rank_month_selected = months[1]
                        zipcode_month_selected = months[1]
                        dependents_month_selecetd = months[1]
                        sgli_month_selected = months[1]
                        state_month_selected = months[1]
                        rothtsp_month_selected = months[1]
                        break
                    else:
                        for i in range(len(months)):
                            months[i] = "no month"

                #find rank
                for x in app.config['RANKS_SHORT']:
                    if x in les_text and les_text[les_text.index(x)+9] == "ENTITLEMENTS":
                        rank = x
                        rank_selected = x
                        break
                    else:
                        rank = "no rank found"

                #find zip code
                if 'PACIDN' in les_text:
                    zipcode = Decimal(les_text[(les_text.index('PACIDN')+3)])
                    zipcode_selected = zipcode
                else:
                    zipcode = 0

                #find dependents
                if 'Depns' in les_text:
                    for i in range(len(dependents)):
                        dependents[i] = Decimal(les_text[(les_text.index('PACIDN')+7)])
                    dependents_selected = dependents[0]
                else:
                    for i in range(len(dependents)):
                        dependents[i] = 0

                #find state
                for x in app.config['STATES_SHORT']:
                    if x in les_text and les_text[(les_text.index(x)-1)] == "TAXES":
                        state = x
                        state_selected = x
                        break
                    else:
                        state = "no state found"

                #find base pay
                if 'BASE' in les_text:
                    for i in range(len(basepay)):
                        basepay[i] = Decimal(les_text[(les_text.index('BASE')+2)])
                else:
                    for i in range(len(basepay)):
                        basepay[i] = 0

                #find BAS
                if 'BAS' in les_text:
                    for i in range(len(bas)):
                        bas[i] = Decimal(les_text[(les_text.index('BAS')+1)])
                else:
                    for i in range(len(bas)):
                        bas[i] = 0

                #find BAH
                if 'BAH' in les_text:
                    for i in range(len(bah)):
                        bah[i] = Decimal(les_text[(les_text.index('BAH')+1)])
                else:
                    for i in range(len(bah)):
                        bah[i] = 0

                #find uea initial
                if 'UEA' in les_text and les_text[les_text.index('UEA')+1] == "INITIAL":
                    ueainitial[0] = Decimal(les_text[(les_text.index('UEA')+2)])
                else:
                    ueainitial[0] = 0

                #find advance debt
                if 'ADVANCE' in les_text and les_text[les_text.index('ADVANCE')+1] == "DEBT":
                    advancedebt[0] = Decimal(les_text[(les_text.index('ADVANCE')+2)])
                else:
                    advancedebt[0] = 0

                #find pcs member
                if 'PCS' in les_text and les_text[les_text.index('PCS')+1] == "MEMBER":
                    pcsmember[0] = Decimal(les_text[(les_text.index('PCS')+2)])
                else:
                    pcsmember[0] = 0

                #find federal taxes
                if 'FEDERAL' in les_text and les_text[les_text.index('FEDERAL')+1] == "TAXES":
                    for i in range(len(federaltaxes)):
                        federaltaxes[i] = Decimal(les_text[(les_text.index('FEDERAL')+2)])
                else:
                    for i in range(len(federaltaxes)):
                        federaltaxes[i] = 0

                #find FICA - Social Security
                if 'SECURITY' in les_text:
                    for i in range(len(ficasocsecurity)):
                        ficasocsecurity[i] = Decimal(les_text[(les_text.index('SECURITY')+1)])
                else:
                    for i in range(len(ficasocsecurity)):
                        ficasocsecurity[i] = 0

                #find FICA - Medicare
                if 'FICA-MEDICARE' in les_text:
                    for i in range(len(ficamedicare)):
                        ficamedicare[i] = Decimal(les_text[(les_text.index('FICA-MEDICARE')+1)])
                else:
                    for i in range(len(ficamedicare)):
                        ficamedicare[i] = 0

                #find SGLI
                if 'SGLI' in les_text:
                    for i in range(len(sgli)):
                        sgli[i] = Decimal(les_text[(les_text.index('SGLI')+1)])
                    sgli_selected = sgli[1]
                else:
                    for i in range(len(sgli)):
                        sgli[i] = 0

                #find state taxes
                if 'STATE' in les_text and les_text[les_text.index('STATE')+1] == "TAXES":
                    for i in range(len(statetaxes)):
                        statetaxes[i] = Decimal(les_text[(les_text.index('STATE')+2)])
                else:
                    for i in range(len(statetaxes)):
                        statetaxes[i] = 0

                #find Roth TSP
                if 'ROTH' in les_text:
                    for i in range(len(rothtsp)):
                        rothtsp[i] = Decimal(les_text[(les_text.index('ROTH')+2)])
                    rothtsp_selected = rothtsp[0]
                else:
                    for i in range(len(rothtsp)):
                        rothtsp[i] = 0

                #find mid-month-pay
                if 'MID-MONTH-PAY' in les_text:
                    midmonthpay = Decimal(les_text[(les_text.index('MID-MONTH-PAY')+1)])
                else:
                    midmonthpay = 0

                #find partial pay
                if 'PARTIAL' in les_text and les_text[les_text.index('PARTIAL')+1] == "PAY":
                    partialpay[0] = Decimal(les_text[(les_text.index('PARTIAL')+2)])
                else:
                    partialpay[0] = 0

                #find pcs members
                if 'PCS' in les_text and les_text[les_text.index('PCS')+1] == "MEMBERS":
                    pcsmembers[0] = Decimal(les_text[(les_text.index('PCS')+2)])
                else:
                    pcsmembers[0] = 0

                #find debt
                if 'DEBT' in les_text and les_text[les_text.index('DEBT')-1] != "ADVANCE":
                    debt[0] = Decimal(les_text[(les_text.index('DEBT')+1)])
                else:
                    debt[0] = 0

                #update total taxes
                for i in range(len(totaltaxes)):
                    totaltaxes[i] = federaltaxes[i] + statetaxes[i]

                #update gross pay:
                for i in range(len(grosspay)):
                    grosspay[i] = basepay[i] + bas[i] + bah[i] + ueainitial[i] + advancedebt[i] + pcsmember[i]

                #update net pay:
                for i in range(len(netpay)):
                    netpay[i] = grosspay[i] - federaltaxes[i] - ficasocsecurity[i] - ficamedicare[i] - sgli[i] - statetaxes[i] - rothtsp[i] - debt[i] - partialpay[i] - pcsmembers[i]


                les_pdf.close()

            return render_template('les.html', 
                                    months=months, state=state, rank=rank, zipcode=zipcode, dependents=dependents,
                                    basepay=basepay, bas=bas, bah=bah, ueainitial=ueainitial, advancedebt=advancedebt, pcsmember=pcsmember,
                                    federaltaxes=federaltaxes, ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, sgli=sgli, statetaxes=statetaxes, rothtsp=rothtsp,
                                    midmonthpay=midmonthpay, debt=debt, partialpay=partialpay, pcsmembers=pcsmembers,
                                    taxablepay=taxablepay, nontaxablepay=nontaxablepay, totaltaxes=totaltaxes, grosspay=grosspay, netpay=netpay,
                                    rank_selected=rank_selected, rank_month_selected=rank_month_selected, 
                                    zipcode_selected=zipcode_selected, zipcode_month_selected=zipcode_month_selected,
                                    dependents_selected=dependents_selected, dependents_month_selected=dependents_month_selected,
                                    sgli_selected=sgli_selected,sgli_month_selected=sgli_month_selected,
                                    state_selected=state_selected, state_month_selected=state_month_selected,
                                    rothtsp_selected=rothtsp_selected, rothtsp_month_selected=rothtsp_month_selected)

    return 'File upload failed'



@app.route('/updatematrix', methods=['POST'])
def updatematrix():

    global months
    global state
    global rank
    global zipcode
    global dependents
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
    global taxablepay
    global nontaxablepay
    global totaltaxes
    global grosspay
    global netpay
    global rank_selected
    global rank_month_selected
    global zipcode_selected
    global zipcode_month_selected
    global dependents_selected
    global dependents_month_selected
    global sgli_selected
    global sgli_month_selected
    global state_selected
    global state_month_selected
    global rothtsp_selected
    global rothtsp_month_selected

    rank_selected = request.form['rank_selected']
    rank_month_selected = request.form['rank_month_selected']
    zipcode_selected = request.form['zipcode_selected']
    zipcode_month_selected = request.form['zipcode_month_selected']
    dependents_selected = request.form['dependents_selected']
    dependents_month_selected = request.form['dependents_month_selected']
    sgli_selected = Decimal(request.form['sgli_selected'])
    sgli_month_selected = request.form['sgli_month_selected']
    state_selected = request.form['state_selected']
    state_month_selected = request.form['state_month_selected']
    rothtsp_selected = request.form['rothtsp_selected']
    rothtsp_month_selected = request.form['rothtsp_month_selected']

    #update rank



    #update zipcode
    #if zipcode_selected:



        #with pdfplumber.open(os.path.join(app.config['STATIC_FOLDER'], BAH_FILE_PDF)) as bah_pdf:
        #    bah_page = bah_pdf.pages[0]
        #    bah_textstring = bah_page.extract_text()
        #    bah_text = bah_textstring.split()

            #print(les_text)

        #    bah_pdf.close()





    #update SGLI
    for i in range(len(sgli)):
        if i >= months.index(sgli_month_selected) and i > 0:
            sgli[i] = Decimal(sgli_selected)
        else:
            sgli[i] = sgli[0]

    #update total taxes
    for i in range(len(totaltaxes)):
        totaltaxes[i] = federaltaxes[i] + statetaxes[i]

    #update gross pay:
    for i in range(len(grosspay)):
        grosspay[i] = basepay[i] + bas[i] + bah[i] + ueainitial[i] + advancedebt[i] + pcsmember[i]

    #update net pay:
    for i in range(len(netpay)):
        netpay[i] = grosspay[i] - federaltaxes[i] - ficasocsecurity[i] - ficamedicare[i] - sgli[i] - statetaxes[i] - rothtsp[i] - debt[i] - partialpay[i] - pcsmembers[i]

    return render_template('les.html', 
                           months=months, state=state, rank=rank, zipcode=zipcode, dependents=dependents,
                           basepay=basepay, bas=bas, bah=bah, ueainitial=ueainitial, advancedebt=advancedebt, pcsmember=pcsmember,
                           federaltaxes=federaltaxes, ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, sgli=sgli, statetaxes=statetaxes, rothtsp=rothtsp,
                           midmonthpay=midmonthpay, debt=debt, partialpay=partialpay, pcsmembers=pcsmembers,
                           taxablepay=taxablepay, nontaxablepay=nontaxablepay, totaltaxes=totaltaxes, grosspay=grosspay, netpay=netpay,
                           rank_selected=rank_selected, rank_month_selected=rank_month_selected, 
                           zipcode_selected=zipcode_selected, zipcode_month_selected=zipcode_month_selected,
                           dependents_selected=dependents_selected, dependents_month_selected=dependents_month_selected,
                           sgli_selected=sgli_selected,sgli_month_selected=sgli_month_selected,
                           state_selected=state_selected, state_month_selected=state_month_selected,
                           rothtsp_selected=rothtsp_selected, rothtsp_month_selected=rothtsp_month_selected)



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