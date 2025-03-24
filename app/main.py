from flask import Flask
from flask import request, render_template, request, make_response, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
#from pdf2image import convert_from_path

import pdfplumber
import os

#file extensions allowed
ALLOWED_EXTENSIONS = {'pdf'}
#location where files are uploaded to and stored for them to be accessed by the program
UPLOAD_FOLDER = 'C:/Users/blue/Documents/GitHub/PayLES/upload'
STATIC_FOLDER = 'C:/Users/blue/Documents/GitHub/PayLES/app/static'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
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
MHA_LONG = ['KETCHIKAN, AK', 'SITKA, AK', 'JUNEAU, AK', 'KODIAK ISLAND, AK', 'ANCHORAGE, AK', 'FAIRBANKS, AK', 'ANNISTON/FORT MCCLELLAN, AL', 'FORT NOVOSEL, AL', 'HUNTSVILLE, AL', 
            'MOBILE, AL', 'MONTGOMERY, AL', 'AUBURN, AL', 'BIRMINGHAM, AL', 'LITTLE ROCK, AR', 'FORT CHAFFEE/FORT SMITH, AR', 'FAYETTEVILLE, AR', 'PHOENIX, AZ', 'FORT HUACHUCA, AZ', 
            'DAVIS-MONTHAN AFB, AZ', 'YUMA, AZ', 'OAKLAND, CA', 'SAN FRANCISCO, CA', 'CHINA LAKE, CA', 'FRESNO, CA', 'LEMOORE NAS, CA', 'CAMP PENDLETON, CA', 'VENTURA, CA', 
            'VANDENBERG SFB, CA', 'MARIN/SONOMA, CA', 'BARSTOW/FORT IRWIN, CA', 'SAN BERNARDINO, CA', 'TWENTY NINE PALMS MCB, CA', 'BEALE AFB, CA', 'SACRAMENTO, CA', 'STOCKTON, CA', 
            'VALLEJO/TRAVIS AFB, CA', 'LOS ANGELES, CA', 'SAN DIEGO, CA', 'MONTEREY, CA', 'RIVERSIDE, CA', 'HUMBOLDT COUNTY, CA', 'SANTA CLARA COUNTY, CA', 'SAN LUIS OBISPO, CA', 
            'BRIDGEPORT, CA', 'EL CENTRO, CA', 'EDWARDS AFB/PALMDALE, CA', 'DENVER, CO', 'COLORADO SPRINGS, CO', 'FORT COLLINS, CO', 'BOULDER, CO', 'NEW LONDON, CT', 'HARTFORD, CT', 
            'NEW HAVEN/FAIRFIELD, CT', 'WASHINGTON, DC METRO AREA', 'DOVER AFB/REHOBOTH, DE', 'EGLIN AFB, FL', 'GAINESVILLE, FL', 'JACKSONVILLE, FL', 'PATRICK SFB, FL', 
            'MIAMI/FORT LAUDERDALE, FL', 'ORLANDO, FL', 'PANAMA CITY, FL', 'PENSACOLA, FL', 'TALLAHASSEE, FL', 'TAMPA, FL', 'WEST PALM BEACH, FL', 'OCALA, FL', 'FLORIDA KEYS, FL', 
            'VOLUSIA COUNTY, FL', 'FORT PIERCE, FL', 'FORT MYERS BEACH, FL', 'ATLANTA, GA', 'ALBANY, GA', 'FORT EISENHOWER, GA', 'KINGS BAY/BRUNSWICK, GA', 'FORT MOORE, GA', 
            'ROBINS AFB, GA', 'SAVANNAH, GA', 'DAHLONEGA, GA', 'FORT STEWART, GA', 'MOODY AFB, GA', 'MAUI COUNTY, HI', 'HONOLULU COUNTY, HI', 'HAWAII COUNTY, HI', 
            'KAUAI COUNTY, HI', 'DES MOINES, IA', 'BOISE, ID', 'MOUNTAIN HOME AFB, ID', 'CHAMPAIGN/URBANA, IL', 'ROCK ISLAND, IL', 'PEORIA, IL', 'GREAT LAKES NAVTRACEN, IL', 
            'SCOTT AFB, IL', 'CHICAGO, IL', 'SPRINGFIELD/DECATUR, IL', 'INDIANAPOLIS, IN', 'FORT WAYNE, IN', 'TERRE HAUTE, IN', 'BLOOMINGTON, IN', 'FORT RILEY, KS', 
            'WICHITA/MCCONNELL AFB, KS', 'FORT LEAVENWORTH, KS', 'TOPEKA, KS', 'FORT CAMPBELL, KY', 'LEXINGTON, KY', 'LOUISVILLE, KY', 'FORT KNOX, KY', 'FRANKFORT, KY', 
            'PADUCAH, KY', 'ALEXANDRIA, LA', 'BATON ROUGE, LA', 'FORT JOHNSON, LA', 'NEW ORLEANS, LA', 'SHREVEPORT/BARKSDALE AFB, LA', 'LAFAYETTE, LA', 'ST MARY AND TERREBONNE, LA', 
            'LAKE CHARLES, LA', 'MONROE, LA', 'NANTUCKET, MA', 'BOSTON, MA', 'WORCESTER, MA', 'FITCHBURG, MA', 'CAPE COD-PLYMOUTH, MA', 'ESSEX CO, MA', 'HAMPDEN COUNTY, MA', 
            'MARTHAS VINEYARD, MA', 'HANSCOM AFB, MA', 'ABERDEEN PROVING GROUNDS, MD', 'ANNAPOLIS, MD', 'BALTIMORE, MD', 'FORT DETRICK, MD', 'FORT G. G. MEADE, MD', 
            'INDIAN HEAD NAVORDSTA, MD', 'PATUXENT RIVER, MD', 'EASTERN SHORE, MD', 'OXFORD, MD', 'BRUNSWICK, ME', 'PORTLAND, ME', 'COASTAL MAINE, ME', 'BANGOR, ME', 'DETROIT, MI', 
            'MARQUETTE, MI', 'SAULT STE MARIE, MI', 'TRAVERSE CITY, MI', 'GRAND HAVEN, MI', 'BATTLE CREEK/KALAMAZOO, MI', 'LANSING, MI', 'GRAND RAPIDS, MI', 'ANN ARBOR, MI', 
            'SAGINAW, MI', 'DULUTH, MN', 'MINNEAPOLIS/ST PAUL, MN', 'KANSAS CITY, MO', 'ST. LOUIS, MO', 'WHITEMAN AFB, MO', 'FORT LEONARD WOOD, MO', 'SPRINGFIELD, MO', 
            'COLUMBIA/JEFFERSON CITY, MO', 'GULFPORT, MS', 'COLUMBUS AFB, MS', 'JACKSON, MS', 'MERIDIAN, MS', 'HATTIESBURG, MS', 'MALMSTROM SFB/GREAT FALLS, MT', 'HELENA, MT', 
            'OUTER BANKS, NC', 'MOREHEAD/CHERRY PT MCAS, NC', 'CAMP LEJEUNE, NC', 'CHARLOTTE, NC', 'DURHAM/CHAPEL HILL, NC', 'ELIZABETH CITY, NC', 'FORT LIBERTY/POPE, NC', 
            'SEYMOUR JOHNSON AFB, NC', 'GREENSBORO, NC', 'RALEIGH, NC', 'WILMINGTON, NC', 'ASHEVILLE, NC', 'BISMARCK, ND', 'FARGO, ND', 'GRAND FORKS, ND', 'MINOT AFB, ND', 
            'OMAHA/OFFUTT AFB, NE', 'LINCOLN, NE', 'PORTSMOUTH, NH/KITTERY, ME', 'MANCHESTER/CONCORD, NH', 'ATLANTIC CITY, NJ', 'CAPE MAY, NJ', 'FORT MONMOUTH/EARLE NWS, NJ', 
            'PERTH AMBOY, NJ', 'NORTHERN NEW JERSEY, NJ', 'TRENTON, NJ', 'JB MCGUIRE-DIX-LAKEHURST, NJ', 'HOLLOMAN AFB/ALAMOGORDO, NM', 'ALBUQUERQUE/KIRTLAND AFB, NM', 
            'CANNON AFB/CLOVIS, NM', 'WHITE SANDS MR/LAS CRUCES, NM', 'SANTA FE/LOS ALAMOS, NM', 'FALLON NAS, NV', 'NELLIS AFB/LAS VEGAS, NV', 'RENO/CARSON CITY, NV', 
            'BALLSTON SPA/ALBANY, NY', 'BUFFALO, NY', 'WEST POINT, NY', 'LONG ISLAND, NY', 'NEW YORK CITY, NY', 'ROCHESTER, NY', 'ROME/GRIFFISS AFB, NY', 'SYRACUSE, NY', 
            'FORT DRUM/WATERTOWN, NY', 'WESTCHESTER COUNTY, NY', 'STATEN ISLAND, NY', 'AKRON, OH', 'CINCINNATI, OH', 'CLEVELAND, OH', 'COLUMBUS, OH', 'WRIGHT-PATTERSON AFB, OH', 
            'TOLEDO, OH', 'YOUNGSTOWN, OH', 'ALTUS AFB, OK', 'VANCE AFB/ENID, OK', 'FORT SILL/LAWTON, OK', 'OKLAHOMA CITY, OK', 'TULSA, OK', 'ASTORIA, OR', 'COOS BAY, OR', 
            'PORTLAND, OR', 'SALEM, OR', 'CORVALLIS, OR', 'EUGENE, OR', 'CARLISLE BARRACKS, PA', 'PHILADELPHIA, PA/CAMDEN, NJ', 'WILLOW GROVE, PA', 'PITTSBURGH, PA', 
            'STATE COLLEGE, PA', 'ERIE, PA', 'WILKES-BARRE/SCRANTON, PA', 'ALLENTOWN/BETHLEHEM, PA', 'NEWPORT, RI', 'PROVIDENCE, RI', 'BEAUFORT/PARRIS ISLAND, SC', 'CHARLESTON, SC', 
            'COLUMBIA/FORT JACKSON, SC', 'GREENVILLE, SC', 'MYRTLE BEACH, SC', 'SUMTER/SHAW AFB, SC', 'RAPID CITY/ELLSWORTH AFB, SD', 'SIOUX FALLS, SD', 'CHATTANOOGA, TN', 
            'KNOXVILLE, TN', 'MEMPHIS, TN', 'NASHVILLE, TN', 'JOHNSON CITY/KINGSPORT, TN', 'ABILENE/DYESS AFB, TX', 'AUSTIN, TX', 'BEAUMONT, TX', 'COLLEGE STATION, TX', 
            'CORPUS CHRISTI, TX', 'DALLAS, TX', 'LAUGHLIN AFB/DEL RIO, TX', 'EL PASO, TX', 'BROWNSVILLE, TX', 'HOUSTON, TX', 'LUBBOCK, TX', 'GOODFELLOW AFB, TX', 'SAN ANTONIO, TX', 
            'FORT CAVAZOS, TX', 'WICHITA FLS/SHEPPARD AFB, TX', 'FORT WORTH, TX', 'WACO, TX', 'OGDEN/HILL AFB, UT', 'SALT LAKE CITY, UT', 'PROVO, UT', 'CHARLOTTESVILLE, VA', 
            'QUANTICO/WOODBRIDGE, VA', 'HAMPTON/NEWPORT NEWS, VA', 'NORFOLK/PORTSMOUTH, VA', 'RICHMOND/FORT GREGG-ADAMS, VA', 'WARRENTON, VA', 'LEXINGTON, VA', 'ROANOKE, VA', 
            'DAHLGREN/FORT WALKER, VA', 'BURLINGTON, VT', 'BREMERTON, WA', 'EVERETT, WA', 'PORT ANGELES, WA', 'SEATTLE, WA', 'SPOKANE, WA', 'TACOMA, WA', 'WHIDBEY ISLAND, WA', 
            'YAKIMA, WA', 'MADISON, WI', 'MILWAUKEE, WI', 'SPARTA/FORT MCCOY, WI', 'STEVENS POINT, WI', 'MORGANTOWN, WV', 'HUNTINGTON, WV', 'CHARLESTON, WV', 'EASTERN PANHANDLE, WV', 
            'CHEYENNE, WY', 'COUNTY COST GROUP 510', 'COUNTY COST GROUP 520', 'COUNTY COST GROUP 530', 'COUNTY COST GROUP 540', 'COUNTY COST GROUP 550', 'COUNTY COST GROUP 560', 
            'COUNTY COST GROUP 570', 'COUNTY COST GROUP 580', 'COUNTY COST GROUP 590', 'COUNTY COST GROUP 600', 'COUNTY COST GROUP 610', 'COUNTY COST GROUP 620', 
            'COUNTY COST GROUP 630', 'COUNTY COST GROUP 640', 'COUNTY COST GROUP 650', 'COUNTY COST GROUP 660', 'COUNTY COST GROUP 670', 'COUNTY COST GROUP 680', 
            'COUNTY COST GROUP 690', 'COUNTY COST GROUP 700', 'COUNTY COST GROUP 710', 'COUNTY COST GROUP 720', 'COUNTY COST GROUP 730', 'COUNTY COST GROUP 740', 
            'COUNTY COST GROUP 750', 'COUNTY COST GROUP 760', 'COUNTY COST GROUP 770', 'COUNTY COST GROUP 780', 'COUNTY COST GROUP 790', 'COUNTY COST GROUP 800', 
            'COUNTY COST GROUP 810', 'COUNTY COST GROUP 820', 'COUNTY COST GROUP 830', 'COUNTY COST GROUP 840', 'COUNTY COST GROUP 850', 'COUNTY COST GROUP 860', 
            'COUNTY COST GROUP 870', 'COUNTY COST GROUP 880', 'COUNTY COST GROUP 890']
MHA_SHORT = ['AK400', 'AK401', 'AK402', 'AK403', 'AK404', 'AK405', 'AL001', 'AL002', 'AL003', 'AL004', 'AL005', 'AL006', 'AL007', 'AR010', 'AR012', 'AR411', 'AZ013', 'AZ014', 
            'AZ015', 'AZ016', 'CA018', 'CA019', 'CA021', 'CA022', 'CA023', 'CA024', 'CA025', 'CA026', 'CA027', 'CA028', 'CA031', 'CA032', 'CA033', 'CA034', 'CA035', 'CA036', 
            'CA037', 'CA038', 'CA039', 'CA041', 'CA042', 'CA044', 'CA392', 'CA393', 'CA420', 'CA457', 'CO045', 'CO046', 'CO047', 'CO422', 'CT049', 'CT050', 'CT051', 'DC053', 
            'DE054', 'FL056', 'FL057', 'FL058', 'FL059', 'FL061', 'FL062', 'FL063', 'FL064', 'FL065', 'FL066', 'FL067', 'FL068', 'FL069', 'FL070', 'FL423', 'FL424', 'GA071', 
            'GA072', 'GA073', 'GA074', 'GA075', 'GA076', 'GA077', 'GA079', 'GA080', 'GA081', 'HI407', 'HI408', 'HI409', 'HI414', 'IA082', 'ID084', 'ID086', 'IL088', 'IL089', 
            'IL090', 'IL092', 'IL093', 'IL325', 'IL335', 'IN094', 'IN097', 'IN338', 'IN399', 'KS100', 'KS101', 'KS102', 'KS105', 'KY106', 'KY107', 'KY109', 'KY110', 'KY339', 
            'KY430', 'LA113', 'LA114', 'LA115', 'LA116', 'LA117', 'LA118', 'LA326', 'LA370', 'LA371', 'MA119', 'MA120', 'MA122', 'MA123', 'MA124', 'MA125', 'MA126', 'MA151', 
            'MA377', 'MD127', 'MD128', 'MD129', 'MD130', 'MD133', 'MD134', 'MD135', 'MD432', 'MD458', 'ME136', 'ME139', 'ME141', 'ME390', 'MI142', 'MI143', 'MI145', 'MI146', 
            'MI148', 'MI152', 'MI153', 'MI154', 'MI155', 'MI156', 'MN158', 'MN159', 'MO160', 'MO161', 'MO162', 'MO163', 'MO164', 'MO165', 'MS168', 'MS169', 'MS170', 'MS171', 
            'MS172', 'MT175', 'MT347', 'NC176', 'NC177', 'NC178', 'NC179', 'NC180', 'NC181', 'NC182', 'NC183', 'NC184', 'NC185', 'NC186', 'NC187', 'ND188', 'ND189', 'ND190', 
            'ND191', 'NE192', 'NE193', 'NH194', 'NH195', 'NJ196', 'NJ198', 'NJ200', 'NJ201', 'NJ202', 'NJ203', 'NJ204', 'NM205', 'NM206', 'NM207', 'NM209', 'NM210', 'NV211', 
            'NV212', 'NV213', 'NY215', 'NY216', 'NY217', 'NY218', 'NY219', 'NY221', 'NY222', 'NY223', 'NY225', 'NY349', 'NY413', 'OH227', 'OH228', 'OH229', 'OH230', 'OH231', 
            'OH232', 'OH233', 'OK235', 'OK236', 'OK237', 'OK239', 'OK240', 'OR241', 'OR242', 'OR243', 'OR244', 'OR245', 'OR246', 'PA247', 'PA248', 'PA249', 'PA250', 'PA252', 
            'PA253', 'PA254', 'PA255', 'RI256', 'RI257', 'SC258', 'SC259', 'SC260', 'SC261', 'SC262', 'SC263', 'SD264', 'SD265', 'TN266', 'TN267', 'TN268', 'TN269', 'TN353', 
            'TX270', 'TX272', 'TX273', 'TX274', 'TX275', 'TX277', 'TX278', 'TX279', 'TX281', 'TX282', 'TX283', 'TX284', 'TX285', 'TX286', 'TX288', 'TX356', 'TX415', 'UT291', 
            'UT292', 'UT357', 'VA295', 'VA296', 'VA297', 'VA298', 'VA301', 'VA302', 'VA303', 'VA362', 'VA368', 'VT305', 'WA306', 'WA307', 'WA308', 'WA309', 'WA310', 'WA311', 
            'WA312', 'WA313', 'WI316', 'WI317', 'WI318', 'WI359', 'WV320', 'WV322', 'WV323', 'WV454', 'WY324', 'ZZ510', 'ZZ520', 'ZZ530', 'ZZ540', 'ZZ550', 'ZZ560', 'ZZ570', 
            'ZZ580', 'ZZ590', 'ZZ600', 'ZZ610', 'ZZ620', 'ZZ630', 'ZZ640', 'ZZ650', 'ZZ660', 'ZZ670', 'ZZ680', 'ZZ690', 'ZZ700', 'ZZ710', 'ZZ720', 'ZZ730', 'ZZ740', 'ZZ750', 
            'ZZ760', 'ZZ770', 'ZZ780', 'ZZ790', 'ZZ800', 'ZZ810', 'ZZ820', 'ZZ830', 'ZZ840', 'ZZ850', 'ZZ860', 'ZZ870', 'ZZ880', 'ZZ890']
BAH_FILE_PDF = "BAH_2025.pdf"


#variables
months = ["", "", "", "", "", "", ""]
state = ""
rank = ""
zipcode = 0
dependents = [0, 0, 0, 0, 0, 0, 0]

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

    with pdfplumber.open(os.path.join(app.config['STATIC_FOLDER'], BAH_FILE_PDF)) as bah_pdf:
        bah_page = bah_pdf.pages[0]
        bah_textstring = page.extract_text()
        bah_text = bah_textstring.split()

        #print(les_text)

        bah_pdf.close()

    return render_template('index.html', 
                           MONTHS_LONG=MONTHS_LONG, MONTHS_SHORT=MONTHS_SHORT, STATES_LONG=STATES_LONG, STATES_SHORT=STATES_SHORT, RANKS_SHORT=RANKS_SHORT,
                           SGLI_COVERAGES=SGLI_COVERAGES, SGLI_PREMIUMS=SGLI_PREMIUMS,
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

    global MONTHS_LONG
    global MONTHS_SHORT
    global STATES_LONG
    global STATES_SHORT
    global RANKS_SHORT
    global SGLI_COVERAGES
    global SGLI_PREMIUMS
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
                for x in MONTHS_SHORT:
                    if x in les_text:
                        for i in range(len(months)):
                            months[i] = MONTHS_SHORT[(MONTHS_SHORT.index(x)+i) % 12]
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
                for x in RANKS_SHORT:
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
                for x in STATES_SHORT:
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
                                    MONTHS_LONG=MONTHS_LONG, MONTHS_SHORT=MONTHS_SHORT, STATES_LONG=STATES_LONG, STATES_SHORT=STATES_SHORT, RANKS_SHORT=RANKS_SHORT,
                                    SGLI_COVERAGES=SGLI_COVERAGES, SGLI_PREMIUMS=SGLI_PREMIUMS,
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

    global MONTHS_LONG
    global MONTHS_SHORT
    global STATES_LONG
    global STATES_SHORT
    global RANKS_SHORT
    global SGLI_COVERAGES
    global SGLI_PREMIUMS
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
                           MONTHS_LONG=MONTHS_LONG, MONTHS_SHORT=MONTHS_SHORT, STATES_LONG=STATES_LONG, STATES_SHORT=STATES_SHORT, RANKS_SHORT=RANKS_SHORT,
                           SGLI_COVERAGES=SGLI_COVERAGES, SGLI_PREMIUMS=SGLI_PREMIUMS,
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
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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