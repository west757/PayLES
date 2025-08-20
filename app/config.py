from datetime import timedelta
from decimal import Decimal
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
    VERSION = "Version 0.1.0 2025-08-18"


    #folders
    STATIC_FOLDER = Path(__file__).parent / "static"
    CSV_FOLDER = STATIC_FOLDER / "csv"
    GRAPHICS_FOLDER = STATIC_FOLDER / "graphics"
    JSON_FOLDER = STATIC_FOLDER / "json"
    PDF_FOLDER = STATIC_FOLDER / "pdf"
    

    #constants   
    DEFAULT_MONTHS_NUM = 4
    MAX_CUSTOM_ROWS = 4
    LES_IMAGE_SCALE = 0.42
    LES_COORD_SCALE = 0.24
    DEPENDENTS_MAX = 9
    FICA_SOCIALSECURITY_TAX_RATE = Decimal(0.062)
    FICA_MEDICARE_TAX_RATE = Decimal(0.0145)
    TRAD_TSP_RATE_MAX = 84
    ROTH_TSP_RATE_MAX = 60
    TSP_CONTRIBUTION_LIMIT = 23500
    BAS_AMOUNT = [Decimal(465.77), Decimal(320.78)]

    TAX_FILING_TYPES_DEDUCTIONS = {
        "Single": 15000,
        "Married": 30000,
        "Head of Household": 22500
    }
    MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    MONTHS_SHORT = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    HOME_OF_RECORDS = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 
                       'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 
                       'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 
                       'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC', 'PR', 'GU', 'VI', 'AS', 'MP']
    GRADES = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 
              'W1', 'W2', 'W3', 'W4', 'W5', 'O1E', 'O2E', 'O3E',
              'O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'O8', 'O9']
    
    ROW_METADATA = [
    'varname',
    'type',
    'dtype',
    'tax',
    'editable',
    'field',
    'modal',
    ]
    

    #load static files
    dtype_bah = {'mha': str}
    for grade in GRADES:
        dtype_bah[grade] = int

    BAH_WITH_DEPENDENTS = pd.read_csv(CSV_FOLDER / "bah_with_dependents_2025.csv",
        dtype=dtype_bah
    )
    BAH_WITHOUT_DEPENDENTS = pd.read_csv(CSV_FOLDER / "bah_without_dependents_2025.csv",
        dtype=dtype_bah
    )
    BUDGET_TEMPLATE = pd.read_csv(CSV_FOLDER / "budget_template.csv",
        dtype={
            'header': str,
            'varname': str,
            'shortname': str,
            'longname': str,
            'sign': int,
            'required': bool,
            'onetime': bool,
            'tax': bool,
            'option': bool,
            'custom': bool,
            'modal': str,
        }
    )
    FEDERAL_TAX_RATES = pd.read_csv(CSV_FOLDER / "federal_tax_rates_2024.csv",
        dtype={
            'status': str, 
            'bracket': int,
        },
        converters={
            'rate': lambda x: Decimal(x),
        }
    )
    LES_RECTANGLES = pd.read_csv(CSV_FOLDER / "les_rectangles.csv",
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
    MHA_ZIP_CODES = pd.read_csv(CSV_FOLDER / "mha_zip_codes.csv",
        dtype={
            'mha': str, 
            'mha_name': str, 
            'zip_code': str,
        }
    )
    PAY_ACTIVE = pd.read_csv(CSV_FOLDER / "pay_active_2025.csv")
    PAY_DRILL = pd.read_csv(CSV_FOLDER / "pay_drill_2025.csv")
    SGLI_RATES = pd.read_csv(CSV_FOLDER / "sgli_rates_2025.csv",
        dtype={
            'coverage': str,
            'tsgli_premium': int,
        },
        converters={
            'premium': lambda x: Decimal(x),
            'total': lambda x: Decimal(x),
        }
    )
    STATE_TAX_RATES = pd.read_csv(CSV_FOLDER / "state_tax_rates_2025.csv",
        dtype={
            'state': str,
            'single_bracket': int,
            'married_bracket': int,
        },
        converters={
            'single_rate': lambda x: Decimal(x),
            'married_rate': lambda x: Decimal(x),
        }
    )
    VARIABLE_TEMPLATE = pd.read_csv(CSV_FOLDER / "variable_template.csv",
        dtype={
            'header': str,
            'varname': str,
            'type': str,
            'option': bool,
            'modal': str,
        }
    )

    FAQ_JSON = JSON_FOLDER / "faq.json"
    LES_REMARKS_JSON = JSON_FOLDER / "les_remarks.json"
    MODALS_JSON = JSON_FOLDER / "modals.json"
    RESOURCES_JSON = JSON_FOLDER / "resources.json"

    EXAMPLE_LES = PDF_FOLDER / "les_example.pdf"
