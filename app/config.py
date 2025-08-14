from datetime import timedelta
from decimal import Decimal
from pathlib import Path
import os
import pandas as pd
import secrets

from app.utils import (
    str_to_bool,
)

class Config:
    #configuration settings
    SECRET_KEY = secrets.token_hex(16)
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   #16MB
    ALLOWED_EXTENSIONS = {'pdf'}
    VERSION = "Version 0.1.0 2025-08-11"


    #folders
    STATIC_FOLDER = Path(__file__).parent / "static"
    CSV_FOLDER = STATIC_FOLDER / "csv"
    GRAPHICS_FOLDER = STATIC_FOLDER / "graphics"
    JSON_FOLDER = STATIC_FOLDER / "json"
    PDF_FOLDER = STATIC_FOLDER / "pdf"
    

    #load static files
    BAH_WITH_DEPENDENTS = pd.read_csv(CSV_FOLDER / "bah_with_dependents_2025.csv")
    BAH_WITHOUT_DEPENDENTS = pd.read_csv(CSV_FOLDER / "bah_without_dependents_2025.csv")
    FEDERAL_TAX_RATES = pd.read_csv(CSV_FOLDER / "federal_tax_rates_2024.csv")
    LES_RECTANGLES = pd.read_csv(CSV_FOLDER / "les_rectangles.csv")
    MHA_ZIP_CODES = pd.read_csv(CSV_FOLDER / "mha_zip_codes.csv")
    PAY_ACTIVE = pd.read_csv(CSV_FOLDER / "pay_active_2025.csv")
    PAY_DRILL = pd.read_csv(CSV_FOLDER / "pay_drill_2025.csv")
    STATE_TAX_RATES = pd.read_csv(CSV_FOLDER / "state_tax_rates_2025.csv")
    SGLI_RATES = pd.read_csv(CSV_FOLDER / "sgli_rates_2025.csv")

    PAYDF_TEMPLATE = pd.read_csv(
        CSV_FOLDER / "paydf_template.csv",
        dtype={'sign': int},
        converters={
            col: str_to_bool for col in ['required', 'onetime', 'tax', 'option', 'custom']
        },
    )

    FAQ_JSON = JSON_FOLDER / "faq.json"
    LES_REMARKS_JSON = JSON_FOLDER / "les_remarks.json"
    PAYDF_MODALS_JSON = JSON_FOLDER / "paydf_modals.json"
    RESOURCES_JSON = JSON_FOLDER / "resources.json"

    EXAMPLE_LES = PDF_FOLDER / "les_example.pdf"
    

    #constants   
    DEFAULT_MONTHS_DISPLAY = 4
    LES_IMAGE_SCALE = 0.42
    LES_COORD_SCALE = 0.24
    BAS_AMOUNT = list(map(Decimal, [320.78, 465.77, 931.54]))
    FICA_SOCIALSECURITY_TAX_RATE = Decimal(0.062)
    FICA_MEDICARE_TAX_RATE = Decimal(0.0145)
    TRADITIONAL_TSP_RATE_MAX = 84
    ROTH_TSP_RATE_MAX = 60

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
    VARIABLES_MODALS = {
        "Year": "basepay",
        "Grade": "basepay",
        "Months in Service": "basepay",
        "Zip Code": "bah",
        "Military Housing Area": "bah",
        "Home of Record": "bah",
        "Federal Filing Status": "federaltaxes",
        "State Filing Status": "statetaxes",
        "Dependents": "bah",
        "SGLI Coverage": "sgli",
        "Combat Zone": "combatzone",
        "Trad TSP Base Rate": "tsp",
        "Trad TSP Specialty Rate": "tsp",
        "Trad TSP Incentive Rate": "tsp",
        "Trad TSP Bonus Rate": "tsp",
        "Roth TSP Base Rate": "tsp",
        "Roth TSP Specialty Rate": "tsp",
        "Roth TSP Incentive Rate": "tsp",
        "Roth TSP Bonus Rate": "tsp"
    }
    CALCULATIONS_MODALS = {
        "Taxable Income": "taxedincome",
        "Non-Taxable Income": "taxedincome",
        "Total Taxes": "taxedincome",
        "Gross Pay": "grossnetpay",
        "Net Pay": "grossnetpay",
        "Difference": "grossnetpay",
    }