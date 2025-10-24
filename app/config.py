from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import secrets

class Config:
    #configuration settings
    SECRET_KEY = secrets.token_hex(16)
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRD_ENABLED = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   #16MB
    ALLOWED_EXTENSIONS = {'pdf'}
    CURRENT_YEAR = datetime.now().year
    CURRENT_MONTH = datetime.now().strftime('%b').upper()
    CURRENT_MONTH_LONG = datetime.now().strftime('%B')  
    VERSION = "Version 0.1.0 2025-10-12"


    #folders
    STATIC_FOLDER = Path(__file__).parent / "static"
    CSV_FOLDER = STATIC_FOLDER / "csv"
    GRAPHICS_FOLDER = STATIC_FOLDER / "graphics"
    JSON_FOLDER = STATIC_FOLDER / "json"
    PDF_FOLDER = STATIC_FOLDER / "pdf"
    

    #constants 
    MONTHS = {
        'JAN': 'January',
        'FEB': 'February',
        'MAR': 'March',
        'APR': 'April',
        'MAY': 'May',
        'JUN': 'June',
        'JUL': 'July',
        'AUG': 'August',
        'SEP': 'September',
        'OCT': 'October',
        'NOV': 'November',
        'DEC': 'December',
    }
    DEFAULT_MONTHS_NUM = 6
    MAX_ROWS = 99
    LES_IMAGE_SCALE = 0.42
    LES_COORD_SCALE = 0.24
    LES_AGE_LIMIT = 2

    FICA_SOCIALSECURITY_TAX_RATE = 0.062
    FICA_MEDICARE_TAX_RATE = 0.0145
    BAS_AMOUNT = [465.77, 320.78]
    DEPENDENTS_MAX = 5
    DRILLS_MAX = 4

    TRAD_TSP_RATE_MAX = 84
    ROTH_TSP_RATE_MAX = 60
    TSP_ELECTIVE_LIMIT = 23500.00
    TSP_ANNUAL_LIMIT = 70000.00
    TSP_AGENCY_AUTO_RATE = 0.01
    TSP_AGENCY_MATCH_RATE = {
        1: 0.01,
        2: 0.02,
        3: 0.03,
        4: 0.035,
        5: 0.04,
    }

    BRANCHES = {
        "USA": "U.S. Army",
        "USAF": "U.S. Air Force",
        "USSF": "U.S. Space Force",
        "USN": "U.S. Navy",
        "USMC": "U.S. Marine Corps",
        #"USCG": "U.S. Coast Guard",
    }

    COMPONENTS = {
        "AD": "Active Duty",
        "AGR": "Active Guard Reserve",
        "NG": "National Guard",
        "RES": "Traditional Reservist",
        #"IRR": "Individual Ready Reserve",
    }

    TAX_FILING_TYPES_DEDUCTIONS = {
        "Single": 15000,
        "Married": 30000,
        "Head of Household": 22500
    }
    
    COMBAT_ZONES = ["No", "Yes"]

    TYPE_SIGN = {
        'var': 0,   # variables
        'ent': 1,   # entitlements
        'ded': -1,  # deductions
        'alt': -1,  # allotments
        'inc': 1,   # custom income
        'exp': -1,  # custom expenses
        'calc': 0,  # calculations
        'ytd': 0,   # year-to-date
        'acc': 0,   # accounts
        'meta': 0,  # metadata
    }
    PAY_METADATA = [
        'type',
        'field',
        'tax',
        'editable',
        'modal',
    ]

    TSP_TYPE_ORDER = ['tot',    # pay total
                      'rate',   # rates
                      'cont',   # tsp contribution
                      'calc',   # tsp calculation
                      'ytd',    # tsp year-to-date
                      'acc']    # tsp account
    TSP_METADATA = [
        'type',
        'field',
        'editable',
        'modal',
    ]

    TRIGGER_CALCULATIONS = {
        'Base Pay': 'calc_base_pay',
        'BAS': 'calc_bas',
        'BAH': 'calc_bah',
        'CONUS COLA': 'calc_conus_cola',
        'OCONUS COLA': 'calc_oconus_cola',
        'OHA': 'calc_oha',
        'MIHA-M': 'calc_miha_m',
        'Federal Taxes': 'calc_federal_taxes',
        'FICA - Social Security': 'calc_fica_social_security',
        'FICA - Medicare': 'calc_fica_medicare',
        'SGLI Rate': 'calc_sgli',
        'State Taxes': 'calc_state_taxes',
    }

    TSP_RATE_HEADERS = [
        "Trad TSP Base Rate",
        "Trad TSP Specialty Rate",
        "Trad TSP Incentive Rate",
        "Trad TSP Bonus Rate",
        "Roth TSP Base Rate",
        "Roth TSP Specialty Rate",
        "Roth TSP Incentive Rate",
        "Roth TSP Bonus Rate",
    ]


    #load static files
    GRADES_RANKS = pd.read_csv(CSV_FOLDER / "grades_ranks.csv",
        dtype={
            'grade': str,
            'USA': str,
            'USAF': str,
            'USSF': str,
            'USN': str,
            'USMC': str,
        }
    )
    GRADES = GRADES_RANKS['grade'].tolist()

    dtype_bah = {'mha': str}
    for grade in GRADES:
        dtype_bah[grade] = int
    BAH_WITH_DEPENDENTS = pd.read_csv(CSV_FOLDER / "bah_with_dependents_2025.csv",
        dtype=dtype_bah
    )
    BAH_WITHOUT_DEPENDENTS = pd.read_csv(CSV_FOLDER / "bah_without_dependents_2025.csv",
        dtype=dtype_bah
    )

    PAY_TEMPLATE = pd.read_csv(CSV_FOLDER / "pay_template.csv",
        dtype={
            'header': str,
            'type': str,
            'field': str,
            'tax': bool,
            'editable': bool,
            'modal': str,
            'trigger': str,
            'onetime': bool,
            'lesname': str,
            'tooltip': str,
        }
    )

    dtype_pay_active = {'grade': str}
    for i in [0, 2, 3, 4] + list(range(6, 41, 2)):
        dtype_pay_active[str(i)] = float
    PAY_ACTIVE = pd.read_csv(CSV_FOLDER / "pay_active_2025.csv",
        dtype=dtype_pay_active
    )
    PAY_DRILL = pd.read_csv(CSV_FOLDER / "pay_drill_2025.csv")

    FEDERAL_TAX_RATES = pd.read_csv(CSV_FOLDER / "federal_tax_rates_2024.csv",
        dtype={
            'status': str, 
            'bracket': int,
            'rate': float,
        },
    )

    HOME_OF_RECORDS = pd.read_csv(CSV_FOLDER / "home_of_records.csv",
        dtype={
            'longname': str,
            'abbr': str,
            'income_taxed': str,
            'retirement_taxed': str,
            'tooltip': str,
        },
    )

    LES_RECT_OVERLAY = pd.read_csv(CSV_FOLDER / "les_rect_overlay.csv",
        dtype={
            'index': int,
            'x1': int,
            'y1': int,
            'x2': int,
            'y2': int,
            'title': str,
            'modal': str,
            'tooltip': str,
        }
    )

    LES_RECT_TEXT = pd.read_csv(CSV_FOLDER / "les_rect_text.csv",
        dtype={
            'header': str,
            'x1': int,
            'y1': int,
            'x2': int,
            'y2': int,
            'dtype': str,
        }
    )

    MHA_ZIP_CODES = pd.read_csv(CSV_FOLDER / "mha_zip_codes.csv",
        dtype={
            'mha': str, 
            'mha_name': str, 
        }
    )

    OCONUS_LOCATIONS = pd.read_csv(CSV_FOLDER / "oconus_locations.csv",
        dtype={
            'country': str, 
            'locality': str, 
            'code': str,
            'cola_index': str,
        }
    )
    OCONUS_LOCATIONS['cola_index'] = (
        OCONUS_LOCATIONS['cola_index']
        .replace(['None', None, 'nan', np.nan], 0)
        .astype(float)
        .fillna(0)
        .astype(int)
    )

    SGLI_RATES = pd.read_csv(CSV_FOLDER / "sgli_rates_2025.csv",
        dtype={
            'coverage': str,
            'premium': float,
            'tsgli_premium': int,
            'total': float,
        },
    )
    SGLI_COVERAGES = SGLI_RATES['coverage'].tolist()

    STATE_TAX_RATES = pd.read_csv(CSV_FOLDER / "state_tax_rates_2025.csv",
        dtype={
            'state': str,
            'single_bracket': int,
            'single_rate': float,
            'married_bracket': int,
            'married_rate': float,
        }
    )

    TSP_TEMPLATE = pd.read_csv(CSV_FOLDER / "tsp_template.csv",
        dtype={
            'header': str,
            'type': str,
            'field': str,
            'editable': bool,
            'modal': str,
            'tooltip': str,
        }
    )

    PARAMS_TEMPLATE = pd.read_csv(CSV_FOLDER / "params_template.csv",
        dtype={
            'header': str,
            'type': str,
            'field': str,
            'tax': bool,
            'editable': bool,
            'modal': str,
            'tooltip': str,
        }
    )

    FAQ_JSON = JSON_FOLDER / "faq.json"
    REMARKS_JSON = JSON_FOLDER / "remarks.json"
    MODALS_JSON = JSON_FOLDER / "modals.json"
    RESOURCES_JSON = JSON_FOLDER / "resources.json"

    LES_EXAMPLE = PDF_FOLDER / "les_example.pdf"
