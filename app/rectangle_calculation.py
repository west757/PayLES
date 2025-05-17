from flask import Flask
from flask import request, render_template, make_response, jsonify, session, send_file
from flask_session import Session
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from decimal import Decimal
from datetime import datetime
import pdfplumber
import os
import io
import pandas as pd
import fitz
import cv2
import numpy as np
from PIL import Image
import io

def find_rectangles():
    doc = fitz.open(os.path.join(app.config['STATIC_FOLDER'], "rectangles.pdf"))
                
    pix = doc[0].get_pixmap(dpi=300)
    image = Image.open(io.BytesIO(pix.tobytes("png")))
    doc.close()

    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # --- Detect green rectangles ---
    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (40, 40, 40), (80, 255, 255))
    green_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_boxes = [cv2.boundingRect(cnt) for cnt in green_contours]
    green_boxes_xyxy = [[x, y, x + w, y + h] for (x, y, w, h) in green_boxes]

    #print(f"Detected {len(green_boxes_xyxy)} green rectangles.")

    # --- Function: Find black rectangle around each green ---
    def find_enclosing_black_box(image, green_box, initial_padding=30, max_padding=100, step=10):
        x1, y1, x2, y2 = green_box
        h, w = image.shape[:2]

        for pad in range(initial_padding, max_padding + 1, step):
            roi_x1 = max(x1 - pad, 0)
            roi_y1 = max(y1 - pad, 0)
            roi_x2 = min(x2 + pad, w)
            roi_y2 = min(y2 + pad, h)

            roi = image[roi_y1:roi_y2, roi_x1:roi_x2]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 30, 100)

            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            candidate_boxes = []

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 200:  # low threshold to catch thin lines
                    x, y, w_box, h_box = cv2.boundingRect(cnt)
                    box_abs = [roi_x1 + x, roi_y1 + y, roi_x1 + x + w_box, roi_y1 + y + h_box]
                    candidate_boxes.append(box_abs)

            for box in candidate_boxes:
                bx1, by1, bx2, by2 = box
                if bx1 <= x1 and by1 <= y1 and bx2 >= x2 and by2 >= y2:
                    return box  # found valid black box

        return None  # not found

    # --- Try to find one black rectangle per green one ---
    matched_black_boxes = []
    not_found = 0

    for green in green_boxes_xyxy:
        box = find_enclosing_black_box(cv_image, green)
        if box:
            matched_black_boxes.append(box)
        else:
            matched_black_boxes.append(None)
            not_found += 1

    # --- Report ---
    #print(f"Matched {len([b for b in matched_black_boxes if b is not None])} black rectangles.")
    #print(f"{not_found} rectangles were not matched.")

    # --- Optional: Debug image ---
    debug_image = cv_image.copy()
    for box in matched_black_boxes:
        if box:
            x1, y1, x2, y2 = box
            cv2.rectangle(debug_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.imwrite("debug_greenguided_blackrects.png", debug_image)

    # --- Final Output ---
    output_boxes = [box for box in matched_black_boxes if box is not None]
    #print("\nBounding boxes (top-left origin):")
    #for box in output_boxes:
    #    print([int(coord) for coord in box])


    def sort_boxes_top_to_bottom_left_to_right(boxes, row_tolerance=20):
        # Sort primarily by y1 (top edge), then x1 (left edge)
        boxes_sorted = sorted(boxes, key=lambda b: (b[1] // row_tolerance, b[0]))
        return boxes_sorted


    # Only include matched boxes for visualization
    numbered_boxes = [box for box in matched_black_boxes if box is not None]
    numbered_boxes = sort_boxes_top_to_bottom_left_to_right(numbered_boxes)

    debug_image = cv_image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2
    color = (0, 0, 255)

    for idx, box in enumerate(numbered_boxes):
        x1, y1, x2, y2 = box
        cv2.rectangle(debug_image, (x1, y1), (x2, y2), color, 2)

        # Center the label
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        label = str(idx + 1)
        text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        text_x = cx - text_size[0] // 2
        text_y = cy + text_size[1] // 2
        cv2.putText(debug_image, label, (text_x, text_y), font, font_scale, color, thickness)

    cv2.imwrite("debug_greenguided_blackrects_numbered.png", debug_image)




    columns = ["index", "x1", "y1", "x2", "y2"]
    data = []

    for idx, (x1, y1, x2, y2) in enumerate(numbered_boxes, start=1):
        data.append([idx, int(x1), int(y1), int(x2), int(y2)])

    df = pd.DataFrame(data, columns=columns)

    # --- Save to CSV ---
    df.to_csv("black_rectangles_coordinates.csv", index=False)

    print("\n CSV file saved as 'black_rectangles_coordinates.csv'")


    source_width=2550
    source_height=3300

    results = ["les text"]

    page = les_pdf.pages[0]
    pdf_width = page.width    # 612
    pdf_height = page.height  # 792

    scale_x = pdf_width / source_width   # 612 / 2550
    scale_y = pdf_height / source_height # 792 / 3300

    for i, row in app.config['RECTANGLES'].iterrows():
        x0 = float(row['x1']) * scale_x
        x1 = float(row['x2']) * scale_x
        y0 = float(row['y1']) * scale_y
        y1 = float(row['y2']) * scale_y

        top = min(y0, y1)
        bottom = max(y0, y1)

        text = page.within_bbox((x0, top, x1, bottom)).extract_text()
        clean_text = text.replace("\n", " ")
        results.append(clean_text.strip() if text else "")


    inum = 0
    for x in results:
        print("rectangle ",inum,": ",x,"\n")
        inum += 1


    return None