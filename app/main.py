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
         'O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9',
         'W1', 'W2', 'W3', 'W4', 'W5']


#variable_pos is the index of the start of that word in the text from the pdf
#variable is the representation of the value associated with it
grade_pos = 0
grade = ""
basepay_pos = 0
basepay = 0
bas_pos = 0
bas = 0
bah_pos = 0
bah = 0
federaltaxes_pos = 0
federaltaxes = 0
ficasocsecurity_pos = 0
ficasocsecurity = 0
ficamedicare_pos = 0
ficamedicare = 0
sgli_pos = 0
sgli = 0
rothtsp_pos = 0
rothtsp = 0
midmonthpay_pos = 0
midmonthpay = 0
grosspay_pos = 0
grosspay = 0
netpay_pos = 0
netpay = 0

month = ""
month1 = ""
month2 = ""
month3 = ""
month4 = ""
month5 = ""
month6 = ""

state = ""

@app.route('/')
def home():
    return render_template('index.html')


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
                        break
                    else:
                        month = "no month found"

                #find grade
                for x in ranks:
                    if x in text:
                        grade = x
                        break
                    else:
                        grade = "no grade found"

                #find base pay
                if 'BASE' in text:
                    basepay_pos = text.index('BASE')
                    basepay = Decimal(text[(basepay_pos+2)])
                else:
                    basepay = -1

                #find BAS
                if 'BAS' in text:
                    bas_pos = text.index('BAS')
                    bas = Decimal(text[(bas_pos+1)])
                else:
                    bas = -1

                #find BAH
                if 'BAH' in text:
                    bah_pos = text.index('BAH')
                    bah = Decimal(text[(bah_pos+1)])
                else:
                    bah = -1

                #find federal taxes
                if 'TAXES' in text:
                    federaltaxes_pos = text.index('TAXES')
                    federaltaxes = Decimal(text[(federaltaxes_pos+1)])
                else:
                    federaltaxes = -1

                #find FICA - Social Security
                if 'SECURITY' in text:
                    ficasocsecurity_pos = text.index('SECURITY')
                    ficasocsecurity = Decimal(text[(ficasocsecurity_pos+1)])
                else:
                    ficasocsecurity = -1

                #find FICA - Medicare
                if 'FICA-MEDICARE' in text:
                    ficamedicare_pos = text.index('FICA-MEDICARE')
                    ficamedicare = Decimal(text[(ficamedicare_pos+1)])
                else:
                    ficamedicare = -1

                #find SGLI
                if 'SGLI' in text:
                    sgli_pos = text.index('SGLI')
                    sgli = Decimal(text[(sgli_pos+1)])
                else:
                    sgli = -1

                #find Roth TPS
                if 'ROTH' in text:
                    rothtsp_pos = text.index('ROTH')
                    rothtsp = Decimal(text[(rothtsp_pos+2)])
                else:
                    rothtsp = -1

                #find mid-month-pay
                if 'MID-MONTH-PAY' in text:
                    midmonthpay_pos = text.index('MID-MONTH-PAY')
                    midmonthpay = Decimal(text[(midmonthpay_pos+1)])
                else:
                    midmonthpay = -1

                #find gross pay
                if 'ENT' in text:
                    grosspay_pos = text.index('ENT')
                    grosspay = Decimal(text[(grosspay_pos+1)])
                else:
                    grosspay = -1

                #find net pay (takes mid-month pay into account)
                if '=NET' in text:
                    netpay_pos = text.index('=NET')
                    netpay = Decimal(text[(netpay_pos+2)])
                    netpay = netpay + midmonthpay
                else:
                    netpay = -1



                #find state
                for x in states:
                    if x in text:
                        state = x
                        break
                    else:
                        state = "no state found"


            return render_template('index.html', months=months, states=states, ranks=ranks, 
                                   filename_display=filename, textarray_display=text, grade=grade, basepay=basepay, bas=bas, bah=bah, federaltaxes=federaltaxes,
                                   ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, sgli=sgli, rothtsp=rothtsp, midmonthpay=midmonthpay, grosspay=grosspay, netpay=netpay,
                                   month=month, month1=month1, month2=month2, month3=month3, month4=month4, month5=month5, month6=month6, state=state)
    return 'File upload failed'


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