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

#variable_pos is the index of the start of that word in the text from the pdf
#variable is the representation of the value associated with it
month_pos = 0
month = ""
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

month1 = ""
month2 = ""
month3 = ""
month4 = ""

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

                #find month
                if 'JAN' in text:
                    month_pos = text.index('JAN')
                    month = text[(month_pos)]
                elif 'FEB' in text:
                    month_pos = text.index('FEB')
                    month = text[(month_pos)]
                elif 'MAR' in text:
                    month_pos = text.index('MAR')
                    month = text[(month_pos)]
                elif 'APR' in text:
                    month_pos = text.index('APR')
                    month = text[(month_pos)]
                elif 'MAY' in text:
                    month_pos = text.index('MAY')
                    month = text[(month_pos)]
                elif 'JUN' in text:
                    month_pos = text.index('JUN')
                    month = text[(month_pos)]
                elif 'JUL' in text:
                    month_pos = text.index('JUL')
                    month = text[(month_pos)]
                elif 'AUG' in text:
                    month_pos = text.index('AUG')
                    month = text[(month_pos)]
                elif 'SEP' in text:
                    month_pos = text.index('SEP')
                    month = text[(month_pos)]
                elif 'OCT' in text:
                    month_pos = text.index('OCT')
                    month = text[(month_pos)]
                elif 'NOV' in text:
                    month_pos = text.index('NOV')
                    month = text[(month_pos)]
                elif 'DEC' in text:
                    month_pos = text.index('DEC')
                    month = text[(month_pos)]
                else:
                    month = "no month found"

                #find grade
                if 'E1' in text:
                    grade_pos = text.index('E1')
                    grade = text[(grade_pos)]
                elif 'E2' in text:
                    grade_pos = text.index('E2')
                    grade = text[(grade_pos)]
                elif 'E3' in text:
                    grade_pos = text.index('E3')
                    grade = text[(grade_pos)]
                elif 'E4' in text:
                    grade_pos = text.index('E4')
                    grade = text[(grade_pos)]
                elif 'E5' in text:
                    grade_pos = text.index('E5')
                    grade = text[(grade_pos)]
                elif 'E6' in text:
                    grade_pos = text.index('E6')
                    grade = text[(grade_pos)]
                elif 'E7' in text:
                    grade_pos = text.index('E7')
                    grade = text[(grade_pos)]
                elif 'E8' in text:
                    grade_pos = text.index('E8')
                    grade = text[(grade_pos)]
                elif 'E9' in text:
                    grade_pos = text.index('E9')
                    grade = text[(grade_pos)]
                elif 'O1' in text:
                    grade_pos = text.index('O1')
                    grade = text[(grade_pos)]
                elif 'O2' in text:
                    grade_pos = text.index('O2')
                    grade = text[(grade_pos)]
                elif 'O3' in text:
                    grade_pos = text.index('O3')
                    grade = text[(grade_pos)]
                elif 'O4' in text:
                    grade_pos = text.index('O4')
                    grade = text[(grade_pos)]
                elif 'O5' in text:
                    grade_pos = text.index('O5')
                    grade = text[(grade_pos)]
                elif 'O6' in text:
                    grade_pos = text.index('O6')
                    grade = text[(grade_pos)]
                elif 'O7' in text:
                    grade_pos = text.index('O7')
                    grade = text[(grade_pos)]
                elif 'O8' in text:
                    grade_pos = text.index('O8')
                    grade = text[(grade_pos)]
                elif 'O9' in text:
                    grade_pos = text.index('O9')
                    grade = text[(grade_pos)]
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

            #calculate months
            if month == "JAN":
                month1 = "January"
                month2 = "February"
                month3 = "March"
                month4 = "April"
            elif month == "FEB":
                month1 = "February"
                month2 = "March"
                month3 = "April"
                month4 = "May"
            elif month == "MAR":
                month1 = "March"
                month2 = "April"
                month3 = "May"
                month4 = "June"
            elif month == "APR":
                month1 = "April"
                month2 = "May"
                month3 = "June"
                month4 = "July"
            elif month == "MAY":
                month1 = "May"
                month2 = "June"
                month3 = "July"
                month4 = "August"
            elif month == "JUN":
                month1 = "June"
                month2 = "July"
                month3 = "August"
                month4 = "September"
            elif month == "JUL":
                month1 = "July"
                month2 = "August"
                month3 = "September"
                month4 = "October"
            elif month == "AUG":
                month1 = "August"
                month2 = "September"
                month3 = "October"
                month4 = "November"
            elif month == "SEP":
                month1 = "September"
                month2 = "October"
                month3 = "November"
                month4 = "December"
            elif month == "OCT":
                month1 = "October"
                month2 = "November"
                month3 = "December"
                month4 = "January"
            elif month == "NOV":
                month1 = "November"
                month2 = "December"
                month3 = "January"
                month4 = "February"
            elif month == "DEC":
                month1 = "December"
                month2 = "January"
                month3 = "February"
                month4 = "March"
            else:
                month = "no month found"




            return render_template('index.html', filename_display=filename, textarray_display=text, month=month, grade=grade, basepay=basepay, bas=bas, bah=bah, federaltaxes=federaltaxes,
                                   ficasocsecurity=ficasocsecurity, ficamedicare=ficamedicare, sgli=sgli, rothtsp=rothtsp, midmonthpay=midmonthpay, grosspay=grosspay, netpay=netpay,
                                   month1=month1, month2=month2, month3=month3, month4=month4)
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