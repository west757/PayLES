from datetime import datetime, timedelta
from pathlib import Path
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
    VERSION = "Version 0.1.0 2025-10-05"


    #folders
    STATIC_FOLDER = Path(__file__).parent / "static"
    CSV_FOLDER = STATIC_FOLDER / "csv"
    GRAPHICS_FOLDER = STATIC_FOLDER / "graphics"
    JSON_FOLDER = STATIC_FOLDER / "json"
    PDF_FOLDER = STATIC_FOLDER / "pdf"
    

    #constants 
    DEFAULT_MONTHS_NUM = 6
    MAX_ROWS = 99
    LES_IMAGE_SCALE = 0.42
    LES_COORD_SCALE = 0.24

    FICA_SOCIALSECURITY_TAX_RATE = 0.062
    FICA_MEDICARE_TAX_RATE = 0.0145
    BAS_AMOUNT = [465.77, 320.78]

    TRAD_TSP_RATE_MAX = 84
    ROTH_TSP_RATE_MAX = 60
    TSP_ELECTIVE_LIMIT = 23500.00
    TSP_ANNUAL_LIMIT = 70000.00

    MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    MONTHS_SHORT = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    BRANCHES = {
        "USA": "United States Army",
        "USAF": "United States Air Force",
        "USSF": "United States Space Force",
        "USN": "United States Navy",
        "USMC": "United States Marine Corps",
        #"USCG": "United States Coast Guard",
    }

    COMPONENTS = {
        "AD": "Active Duty",
        "AGR": "Active Guard Reserve",
        "NG": "National Guard",
        "RES": "Traditional Reservist",
        "IRR": "Individual Ready Reserve",
    }

    TAX_FILING_TYPES_DEDUCTIONS = {
        "Single": 15000,
        "Married": 30000,
        "Head of Household": 22500
    }
    
    COMBAT_ZONES = ["No", "Yes"]

    # budget type order:
    # v = variables
    # e = entitlements
    # d = deductions
    # a = allotments
    # c = custom
    # x = calculations
    # y = year-to-date
    # z = accounts
    # m = metadata
    BUDGET_TYPE_ORDER = ['v', 'e', 'd', 'a', 'c', 'x', 'y', 'z', 'm']
    BUDGET_METADATA = [
        'type',
        'sign',
        'field',
        'tax',
        'editable',
        'modal',
    ]

    # tsp type order:
    # r = rates
    # t = tsp rows
    # p = tsp accounts
    TSP_TYPE_ORDER = ['r', 't', 'p']
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
    TSP_CONTRIBUTION_HEADERS = [
        "Trad TSP Contribution",
        "Trad TSP Exempt Contribution",
        "Roth TSP Contribution",
        "Agency Auto Contribution",
        "Agency Matching Contribution"
    ]
    TSP_YTD_HEADERS = [
        "YTD Trad TSP",
        "YTD Trad TSP Exempt",
        "YTD Roth TSP",
        "YTD Agency Auto",
        "YTD Agency Matching"
    ]
    TSP_YTD_ELECTIVE_HEADERS = [
        "YTD Trad TSP",
        "YTD Roth TSP"
    ]


    #load static files
    dtype_pay_active = {'grade': str}
    for i in [0, 2, 3, 4] + list(range(6, 41, 2)):
        dtype_pay_active[str(i)] = float
    PAY_ACTIVE = pd.read_csv(CSV_FOLDER / "pay_active_2025.csv",
        dtype=dtype_pay_active
    )
    PAY_DRILL = pd.read_csv(CSV_FOLDER / "pay_drill_2025.csv")
    GRADES = list(reversed(PAY_ACTIVE['grade'].tolist()))

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
            'sign': int,
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
            'sign': int,
            'field': str,
            'tax': bool,
            'editable': bool,
            'modal': str,
            'tooltip': str,
        }
    )

    FAQ_JSON = JSON_FOLDER / "faq.json"
    LES_REMARKS_JSON = JSON_FOLDER / "les_remarks.json"
    MODALS_JSON = JSON_FOLDER / "modals.json"
    RESOURCES_JSON = JSON_FOLDER / "resources.json"

    LES_EXAMPLE = PDF_FOLDER / "les_example.pdf"
