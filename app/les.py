from PIL import Image, ImageDraw
import base64
import io
import pdfplumber
import re

from app import flask_app
from app.utils import (
    get_error_context,
)


def validate_les(file):
    with pdfplumber.open(file) as les_pdf:
        # check bounding box of the LES title to verify the pdf is an LES
        title_crop = les_pdf.pages[0].crop((18, 18, 593, 29))
        title_text = title_crop.extract_text_simple()

        if title_text == "DEFENSE FINANCE AND ACCOUNTING SERVICE MILITARY LEAVE AND EARNINGS STATEMENT":
            return True, None, les_pdf
        else:
            return False, "File is not a valid LES", None


def process_les(les_pdf):
    les_page = les_pdf.pages[0].crop((0, 0, 612, 630))
    les_image = create_les_image(les_page)
    les_text_raw = extract_les_text(les_page)
    les_text = format_les_text(les_text_raw)

    #for header, text in les_text.items():
    #    print(f"{header}: {text}")
    
    return les_image, les_text


def create_les_image(les_page):
    LES_IMAGE_SCALE = flask_app.config['LES_IMAGE_SCALE']

    raw_image = les_page.to_image(resolution=300).original
    new_width = int(raw_image.width * LES_IMAGE_SCALE)
    new_height = int(raw_image.height * LES_IMAGE_SCALE)
    scaled_image = raw_image.resize((new_width, new_height), Image.LANCZOS)

    whiteout_rects = [
        (200, 165, 700, 220),  # name
        (710, 165, 980, 220),  # SSN
    ]

    # apply whiteout rectangles
    draw = ImageDraw.Draw(scaled_image)
    for rect in whiteout_rects:
        x1 = int(rect[0] * LES_IMAGE_SCALE)
        y1 = int(rect[1] * LES_IMAGE_SCALE)
        x2 = int(rect[2] * LES_IMAGE_SCALE)
        y2 = int(rect[3] * LES_IMAGE_SCALE)
        draw.rectangle([x1, y1, x2, y2], fill="white")

    # creates les_image as base64 encoded flattened raster PNG
    img_io = io.BytesIO()
    scaled_image.save(img_io, format='PNG')
    img_io.seek(0)
    les_image = base64.b64encode(img_io.read()).decode("utf-8")

    return les_image


def extract_les_text(les_page):
    LES_RECT_TEXT = flask_app.config['LES_RECT_TEXT']
    LES_COORD_SCALE = flask_app.config['LES_COORD_SCALE']
    les_text = {}

    for _, row in LES_RECT_TEXT.iterrows():
        header = row['header']
        x1 = float(row['x1']) * LES_COORD_SCALE
        y1 = float(row['y1']) * LES_COORD_SCALE
        x2 = float(row['x2']) * LES_COORD_SCALE
        y2 = float(row['y2']) * LES_COORD_SCALE
        upper = min(y1, y2)
        lower = max(y1, y2)

        text = les_page.within_bbox((x1, upper, x2, lower)).extract_text()
        if text:
            text = text.replace("\n", " ").strip()
        else:
            text = ""
        les_text[header] = text

    return les_text


def format_les_text(les_text_raw):
    LES_RECT_TEXT = flask_app.config['LES_RECT_TEXT']
    dtype_map = {row['header']: row['dtype'] for _, row in LES_RECT_TEXT.iterrows()}
    les_text = {}

    for header, value in les_text_raw.items():
        dtype = dtype_map.get(header, "string")
        try:
            if dtype == "int":
                # remove commas and spaces, handle empty or invalid values
                val = value.replace(",", "").strip()
                les_text[header] = int(val) if val.isdigit() or (val and val.lstrip('-').isdigit()) else 0
            elif dtype == "float":
                # remove commas and spaces, handle empty or invalid values
                val = value.replace(",", "").strip()
                try:
                    les_text[header] = float(val)
                except (ValueError, TypeError):
                    les_text[header] = 0.0
            elif dtype == "string":
                # if empty or only whitespace, set as NOT FOUND
                les_text[header] = value.strip() if value and value.strip() else "NOT FOUND"
            else:
                # unknown dtype, just keep as string
                les_text[header] = value
        except Exception as e:
            # fallback for any unexpected error
            if dtype == "int":
                les_text[header] = 0
            elif dtype == "float":
                les_text[header] = 0.0
            else:
                les_text[header] = "NOT FOUND"

    # parse period into les_month and les_year
    period = les_text.get("period", "")
    match = re.search(r"\d+-\d+\s+([A-Z]{3})\s+(\d{2})", period)
    if match:
        les_month = match.group(1)
        les_year = match.group(2)
        les_text["les_month"] = les_month
        les_text["les_year"] = les_year
    else:
        les_text["les_month"] = ""
        les_text["les_year"] = ""
    les_text.pop("period", None)

    # combine remarks1 and remarks2 into remarks
    remarks1 = les_text.get("remarks1", "")
    remarks2 = les_text.get("remarks2", "") 
    les_text["remarks"] = (remarks1 + " " + remarks2).strip()
    les_text.pop("remarks1", None)
    les_text.pop("remarks2", None)

    return les_text


def get_les_rect_overlay():
    LES_RECT_OVERLAY = flask_app.config['LES_RECT_OVERLAY']
    LES_IMAGE_SCALE = flask_app.config['LES_IMAGE_SCALE']

    rect_overlay = []
    for rect in LES_RECT_OVERLAY.to_dict(orient="records"):
        rect_overlay.append({
            "x1": rect["x1"] * LES_IMAGE_SCALE,
            "y1": rect["y1"] * LES_IMAGE_SCALE,
            "x2": rect["x2"] * LES_IMAGE_SCALE,
            "y2": rect["y2"] * LES_IMAGE_SCALE,
            "modal": rect["modal"],
            "tooltip": rect["tooltip"]
        })
    return rect_overlay


def validate_les_age(les_text):
    CURRENT_MONTH = flask_app.config['CURRENT_MONTH']
    CURRENT_YEAR = flask_app.config['CURRENT_YEAR']
    MONTHS = flask_app.config['MONTHS']
    LES_AGE_LIMIT = flask_app.config['LES_AGE_LIMIT']
    
    try:
        month = les_text.get('les_month', None)
        if month not in MONTHS.keys():
            raise ValueError(f"Invalid LES month: {month}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining month from LES text"))
    
    try:
        year = int('20' + les_text.get('les_year', None))
        if not year or year < 2021 or year > flask_app.config['CURRENT_YEAR'] + 1:
            raise ValueError(f"Invalid LES year: {year}")
    except Exception as e:
        raise Exception(get_error_context(e, "Error determining year from LES text"))

    months_number_map = {k: i+1 for i, k in enumerate(MONTHS.keys())}
    delta_months = (CURRENT_YEAR - year) * 12 + (months_number_map.get(CURRENT_MONTH) - months_number_map.get(month))
    #if delta_months > LES_AGE_LIMIT:
    #    return False, f"The LES you submitted is more than {LES_AGE_LIMIT} months old. Please upload a recent LES.", year, month

    return True, "", year, month