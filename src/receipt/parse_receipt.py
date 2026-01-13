"""
Python code to consume a receipt image and extract structured data such as product name, total amount, and itemized purchases using OCR and regex.
"""

import cv2
import pytesseract
from PIL import Image
import os
import yaml
import re


TOTAL_PATTERN = re.compile(r"\bTOTAL\b\s+(\d+\.\d{2})", re.IGNORECASE)


def image_to_text(image_path):
    """
    Convert receipt image to text using OCR.
    Args:
        image_path (str): Path to the receipt image.
    Returns:
        str: Extracted text from the image.
    """

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    text = pytesseract.image_to_string(gray)
    return text


def image_to_dict(image_path):
    """
    Convert receipt image to structured data dictionary.
    Args:
        image_path (str): Path to the receipt image.
    Returns:
        dict: Structured data extracted from the receipt.
    """
    text = image_to_text(image_path)
    text = [
        item.strip()
        for item in text.split("\n")
        if (not item.isnumeric() and len(item) >= 3)
    ]

    keys = [item for item in text if re.match(r"^(?!\d+\.\d{2,3}).+", item)][
        :-1
    ]
    values = [
        item
        for item in text
        if re.match(r"^\d+\.\d{2,3}(?:\s*[A-Z0-9-])?$", item)
    ]
    print(keys)
    print(values)

    data = {
        "items": []
    }
    last_item = None
    # keys = keys[:-2]
    # values = values[:-2]
    j = 0

    for i in range(len(keys)):
        if "TAX" in keys[i] and "LIQUOR" in keys[i - 1]:
            continue

        if keys[i] == "TAX" or keys[i] == "SUBTOTAL":
            continue

        if keys[i][0] != "/":
            last_item = {
                "name": keys[i].strip(),
                "price": float(values[j].split()[0]),
                "discount": 0.0,
                "effective_price": float(values[j].split()[0]),
            }
            data["items"].append(last_item)
            j += 1
            continue

        else:
            value = values[j][:-1]
            last_item["discount"] += float(value)
            last_item["effective_price"] -= float(value)
            j += 1
            continue

    return data