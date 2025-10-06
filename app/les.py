from PIL import Image, ImageDraw
import base64
import io
import pdfplumber
import numpy as np

from app import flask_app


# =========================
# validate and process LES
# =========================

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
    les_text = extract_les_text(les_page)
    get_rect_bounds()
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

    # creates les_image as base64 encoded PNG, result is flattened raster image
    img_io = io.BytesIO()
    scaled_image.save(img_io, format='PNG')
    img_io.seek(0)
    les_image = base64.b64encode(img_io.read()).decode("utf-8")

    return les_image


def extract_les_text(les_page):
    LES_RECT_OVERLAY = flask_app.config['LES_RECT_OVERLAY']
    LES_COORD_SCALE = flask_app.config['LES_COORD_SCALE']
    les_text = ["text per rectangle"]

    # extracts text from each rectangle defined in LES_RECT_OVERLAY
    for _, row in LES_RECT_OVERLAY.iterrows():
        x1 = float(row['x1']) * LES_COORD_SCALE
        x2 = float(row['x2']) * LES_COORD_SCALE
        y1 = float(row['y1']) * LES_COORD_SCALE
        y2 = float(row['y2']) * LES_COORD_SCALE
        upper = min(y1, y2)
        lower = max(y1, y2)

        les_rect_text = les_page.within_bbox((x1, upper, x2, lower)).extract_text()
        les_text.append(les_rect_text.replace("\n", " ").split())

    return les_text


def calc_les_rect_overlay():
    LES_RECT_OVERLAY = flask_app.config['LES_RECT_OVERLAY']
    LES_IMAGE_SCALE = flask_app.config['LES_IMAGE_SCALE']

    # initialize and scale rectangle overlay data
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



import csv
from PIL import ImageFont

def get_rect_bounds():
    pdf_path = flask_app.config['LES_RECTS_GREEN']
    rects = []

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        im = page.to_image(resolution=300).original.convert("RGB")
        arr = np.array(im)

        # Target green: #4CAF50 (76, 175, 80)
        lower_green = np.array([70, 170, 70])
        upper_green = np.array([85, 185, 90])

        green_mask = np.all((arr >= lower_green) & (arr <= upper_green), axis=-1)

        from scipy.ndimage import label, find_objects
        labeled, num_features = label(green_mask)
        slices = find_objects(labeled)

        # Prepare for drawing numbers
        draw = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()

        for idx, sl in enumerate(slices, start=1):
            y1, x1 = sl[0].start, sl[1].start
            y2, x2 = sl[0].stop, sl[1].stop
            rects.append([idx, x1, y1, x2, y2])

            # Draw the number at the center of the rectangle
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            draw.text((cx, cy), str(idx), fill="black", font=font, anchor="mm")

    # Write to CSV with number column
    csv_path = "green_rect_bounds.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["number", "x1", "y1", "x2", "y2"])
        for rect in rects:
            writer.writerow(rect)

    # Save annotated image for visual reference
    im.save("green_rect_bounds_annotated.png")

    return None