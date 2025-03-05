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

monthslong = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
stateslong = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii',
              'Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota',
              'Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina',
              'North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas',
              'Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']
states = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO',
          'MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
ranks = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9',
         'W1', 'W2', 'W3', 'W4', 'W5', 
         'O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9']
sglicoverages = [0, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000, 500000]
sglipremiums = [0, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31]

#variables
month = ""
month1 = ""
month2 = ""
month3 = ""
month4 = ""
month5 = ""
month6 = ""
monthsafter = [month1, month2, month3, month4, month5, month6]
state = ""
grade = ""
zipcode = 0

#entitlements
basepay = 0
bas = 0
bah = 0
ueainitial = 0
advancedebt = 0
pcsmember = 0

#deductions
federaltaxes = 0
ficasocsecurity = 0
ficamedicare = 0
sgli = 0
statetaxes = 0
rothtsp = 0
midmonthpay = 0
debt = 0
partialpay = 0
pcsmembers = 0

#allotments


#calculations
grosspay = 0
netpay = 0
sglicoverage = 0
sgli0 = 0
sgli1 = 0
sgli2 = 0
sgli3 = 0
sgli4 = 0
sgli5 = 0
sgli6 = 0


@app.route('/')
def home():
    return render_template('index.html', months=months, states=states, ranks=ranks,
                                   grade=grade, basepay=basepay, bas=bas, bah=bah, federaltaxes=federaltaxes, statetaxes=statetaxes,
                                   ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, 
                                   sgli0=sgli0, sgli1=sgli1, sgli2=sgli2, sgli3=sgli3, sgli4=sgli4, sgli5=sgli5, sgli6=sgli6,
                                   sglicoverage=sglicoverage, sglipremiums=sglipremiums, sglicoverages=sglicoverages,
                                   rothtsp=rothtsp, midmonthpay=midmonthpay, grosspay=grosspay, netpay=netpay,
                                   month=month, month1=month1, month2=month2, month3=month3, month4=month4, month5=month5, month6=month6, monthsafter=monthsafter,
                                   state=state, zipcode=zipcode)


@app.route('/index', methods=['POST'])
def upload_file():
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
                #text = page.extract_text(x_tolerance=3, x_tolerance_ratio=None, y_tolerance=3, layout=False, x_density=7.25, y_density=13, line_dir_render=None, char_dir_render=None)
                #creates a string of all text from the LES
                textstring = page.extract_text()
                #creates an array of all text separated by a space
                #avoids the problem of using specific indexes because indexes may change depending on text size
                text = textstring.split()

                #print(text)

                #find month
                for x in months:
                    if x in text:
                        month = x
                        month1 = months[(months.index(x)+1) % 12]
                        month2 = months[(months.index(x)+2) % 12]
                        month3 = months[(months.index(x)+3) % 12]
                        month4 = months[(months.index(x)+4) % 12]
                        month5 = months[(months.index(x)+5) % 12]
                        month6 = months[(months.index(x)+6) % 12]
                        monthsafter = [month1, month2, month3, month4, month5, month6]
                        break
                    else:
                        month = "no month found"

                #find grade
                for x in ranks:
                    if x in text and text[text.index(x)+9] == "ENTITLEMENTS":
                        grade = x
                        break
                    else:
                        grade = "no grade found"

                #find base pay
                if 'BASE' in text:
                    basepay = Decimal(text[(text.index('BASE')+2)])
                else:
                    basepay = 0

                #find BAS
                if 'BAS' in text:
                    bas = Decimal(text[(text.index('BAS')+1)])
                else:
                    bas = 0

                #find BAH
                if 'BAH' in text:
                    bah = Decimal(text[(text.index('BAH')+1)])
                else:
                    bah = 0

                #find federal taxes
                if 'FEDERAL' in text and text[text.index('FEDERAL')+1] == "TAXES":
                    federaltaxes = Decimal(text[(text.index('FEDERAL')+2)])
                else:
                    federaltaxes = 0

                #find FICA - Social Security
                if 'SECURITY' in text:
                    ficasocsecurity = Decimal(text[(text.index('SECURITY')+1)])
                else:
                    ficasocsecurity = 0

                #find FICA - Medicare
                if 'FICA-MEDICARE' in text:
                    ficamedicare = Decimal(text[(text.index('FICA-MEDICARE')+1)])
                else:
                    ficamedicare = 0

                #find SGLI
                if 'SGLI' in text:
                    sgli0 = Decimal(text[(text.index('SGLI')+1)])
                    for x in sglipremiums:
                        if x == sgli0:
                            sglicoverage = sglicoverages[sglipremiums.index(int(sgli0))]
                            sgli1 = sgli0
                            sgli2 = sgli0
                            sgli3 = sgli0
                            sgli4 = sgli0
                            sgli5 = sgli0
                            sgli6 = sgli0
                            break
                        else:
                            sglicoverage = 0
                else:
                    sgli0 = 0

                #find state taxes
                if 'STATE' in text and text[text.index('STATE')+1] == "TAXES":
                    statetaxes = Decimal(text[(text.index('STATE')+2)])
                else:
                    statetaxes = 0

                #find Roth TSP
                if 'ROTH' in text:
                    rothtsp = Decimal(text[(text.index('ROTH')+2)])
                else:
                    rothtsp = 0

                #find mid-month-pay
                if 'MID-MONTH-PAY' in text:
                    midmonthpay = Decimal(text[(text.index('MID-MONTH-PAY')+1)])
                else:
                    midmonthpay = 0

                #find gross pay
                if 'ENT' in text:
                    grosspay = Decimal(text[(text.index('ENT')+1)])
                else:
                    grosspay = 0

                #find net pay (takes mid-month pay into account)
                if '=NET' in text:
                    netpay = Decimal(text[(text.index('=NET')+2)])
                    if midmonthpay != 0:
                        netpay = netpay + midmonthpay
                else:
                    netpay = 0

                #find state
                for x in states:
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


            return render_template('index.html', months=months, states=states, ranks=ranks,
                                   filename_display=filename, textarray_display=text, grade=grade, basepay=basepay, bas=bas, bah=bah, federaltaxes=federaltaxes, statetaxes=statetaxes,
                                   ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, 
                                   sgli0=sgli0, sgli1=sgli1, sgli2=sgli2, sgli3=sgli3, sgli4=sgli4, sgli5=sgli5, sgli6=sgli6,
                                   sglicoverage=sglicoverage, sglipremiums=sglipremiums, sglicoverages=sglicoverages,
                                   rothtsp=rothtsp, midmonthpay=midmonthpay, grosspay=grosspay, netpay=netpay,
                                   month=month, month1=month1, month2=month2, month3=month3, month4=month4, month5=month5, month6=month6, monthsafter=monthsafter,
                                   state=state, zipcode=zipcode)
    return 'File upload failed'




@app.route('/submit123', methods=['POST'])
def submit123():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    if not name or not email:
        return "<p>Error: Name and Email are required!</p>", 400
    
    response = f"""
    <div class="alert alert-success">
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
    </div>
    """
    return response



#@app.route('/update-fields')
#def update_fields():
#    type_ = request.args.get('type')
#    if type_ == 'advanced':
#        fields = '''
#        <div class="form-group">
#            <label for="extra">Additional Information:</label>
#            <input type="text" id="extra" name="extra" class="form-control">
#        </div>
#        '''
#    else:
#        fields = ''
#    return fields




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