from datetime import timedelta
from decimal import Decimal
from pathlib import Path
import os
import pandas as pd
import secrets

def str_to_bool(val):
    return str(val).strip().upper() == "TRUE"

class Config:
    #configuration settings
    SECRET_KEY = secrets.token_hex(16)
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SAMESITE = 'Lax'
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   #max size of uploaded file 16MB
    STATIC_FOLDER = Path(__file__).parent / "static"
    VERSION = "Version 0.1.0 2025-08-01"

    #static files
    LOGO_FILE = "logo.png"
    EXAMPLE_LES_FILE = "les_example.pdf"
    LES_RECTANGLES_FILE = "les_rectangles.csv"
    MHA_ZIP_CODE_FILE = "mha_zip_codes.csv"
    PAY_ACTIVE_FILE = "pay_active_2025.csv"
    PAY_DRILL_FILE = "pay_drill_2025.csv"
    BAH_WITH_DEPENDENTS_FILE = "bah_with_dependents_2025.csv"
    BAH_WITHOUT_DEPENDENTS_FILE = "bah_without_dependents_2025.csv"
    FEDERAL_TAX_RATE_FILE = "federal_tax_rate_2024.csv"
    STATE_TAX_RATE_FILE = "state_tax_rate_2025.csv"
    SGLI_RATE_FILE = "sgli_rate.csv"
    PAYDF_TEMPLATE_FILE = "paydf_template.csv"
    PAYDF_MODALS_JSON_FILE = "paydf_modals.json"
    LES_REMARKS_JSON_FILE = "les_remarks.json"
    FAQ_JSON_FILE = "faq.json"
    RESOURCES_JSON_FILE = "resources.json"

    #load static files
    LOGO = os.path.join('static', LOGO_FILE)
    EXAMPLE_LES = os.path.join(STATIC_FOLDER, EXAMPLE_LES_FILE)
    LES_RECTANGLES = pd.read_csv(os.path.join(STATIC_FOLDER, LES_RECTANGLES_FILE))
    MHA_ZIP_CODES = pd.read_csv(os.path.join(STATIC_FOLDER, MHA_ZIP_CODE_FILE))
    PAY_ACTIVE = pd.read_csv(os.path.join(STATIC_FOLDER, PAY_ACTIVE_FILE))
    PAY_DRILL = pd.read_csv(os.path.join(STATIC_FOLDER, PAY_DRILL_FILE))
    BAH_WITH_DEPENDENTS = pd.read_csv(os.path.join(STATIC_FOLDER, BAH_WITH_DEPENDENTS_FILE))
    BAH_WITHOUT_DEPENDENTS = pd.read_csv(os.path.join(STATIC_FOLDER, BAH_WITHOUT_DEPENDENTS_FILE))
    FEDERAL_TAX_RATE = pd.read_csv(os.path.join(STATIC_FOLDER, FEDERAL_TAX_RATE_FILE))
    STATE_TAX_RATE = pd.read_csv(os.path.join(STATIC_FOLDER, STATE_TAX_RATE_FILE))
    SGLI_RATE = pd.read_csv(os.path.join(STATIC_FOLDER, SGLI_RATE_FILE))

    bool_columns = ['required', 'onetime', 'standard', 'tax', 'option']
    PAYDF_TEMPLATE = pd.read_csv(os.path.join(STATIC_FOLDER, PAYDF_TEMPLATE_FILE), converters={col: str_to_bool for col in bool_columns})

    #constants
    LES_COORD_SCALE = 0.24
    LES_IMAGE_SCALE = 0.42
    DEFAULT_MONTHS_DISPLAY = 6
    MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    MONTHS_SHORT = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    STATES_LONG = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii',
                   'Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota',
                   'Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina',
                   'North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas',
                   'Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming', 'District of Columbia']
    STATES_SHORT = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO',
                    'MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY', 'DC']
    GRADES = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 
              'W1', 'W2', 'W3', 'W4', 'W5', 'O1E', 'O2E', 'O3E',
              'O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9']
    BAS_AMOUNT = list(map(Decimal, [320.78, 465.77, 931.54]))   #officers, enlisted, enlisted BAS 2
    FICA_SOCIALSECURITY_TAX_RATE = Decimal(0.062)
    FICA_MEDICARE_TAX_RATE = Decimal(0.0145)
    TAX_FILING_TYPES = ["Single", "Married", "Head of Household"]
    STANDARD_DEDUCTIONS = [15000, 30000, 22500]
    TRADITIONAL_TSP_RATE_MAX = 84
    ROTH_TSP_RATE_MAX = 60
    