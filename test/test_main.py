import pytest
from receipt.main import *
from receipt.product_dictionary import ESSENTIAL_LIST
from receipt import parse_receipt, save_results
import pytest
from unittest.mock import patch, MagicMock
import cv2
import pytesseract
from pathlib import Path
from datetime import datetime
import tempfile
import pandas as pd


def test_categorize_items_by_name():
    receipt_data = {
        "items": [
            {"name": "WH MK", "effective_price": 25.00},
            {"name": "DUMMY PRODUCT", "effective_price": 40.00},
        ]
    }

    result = categorize_items(receipt_data)

    assert result["items"][0]["name"] in ESSENTIAL_LIST
    assert result["items"][0]["category"] == "essential"
    assert result["items"][1]["category"] == ""


def test_move_file_moves_file(tmp_path):
    # Arrange
    src_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    src_dir.mkdir()

    src_file = src_dir / "test.jpg"
    src_file.write_text("dummy content")

    # Act
    result_path = move_file(src_file, dest_dir)

    # Assert
    assert not src_file.exists()
    assert result_path.exists()
    assert result_path.read_text() == "dummy content"
    assert result_path.parent == dest_dir


def test_image_to_dict_basic(monkeypatch):
    fake_ocr_text = """
    MILK
    4.99
    /1
    1.00-
    EGGS
    6.49
    SUBTOTAL
    11.48
    TAX
    0.92
    TOTAL
    12.40
    """

    def mock_image_to_text(_):
        return fake_ocr_text

    monkeypatch.setattr(parse_receipt, "image_to_text", mock_image_to_text)

    result = image_to_dict("fake_path.jpg")

    assert len(result["items"]) == 2

    milk = result["items"][0]
    eggs = result["items"][1]

    assert milk["name"] == "MILK"
    assert milk["price"] == 4.99
    assert milk["discount"] == 1.00
    assert milk["effective_price"] == 3.99

    assert eggs["name"] == "EGGS"
    assert eggs["price"] == 6.49
    assert eggs["discount"] == 0.0
    assert eggs["effective_price"] == 6.49


def test_image_to_dict_no_discounts(monkeypatch):
    fake_ocr_text = """
    APPLES
    3.99
    BANANAS
    1.49
    SUBTOTAL
    5.48
    TAX
    0.44
    TOTAL
    5.92
    """

    monkeypatch.setattr(parse_receipt, "image_to_text", lambda _: fake_ocr_text)

    result = parse_receipt.image_to_dict("fake.jpg")

    assert len(result["items"]) == 2
    assert result["items"][0]["discount"] == 0.0
    assert result["items"][1]["discount"] == 0.0


def test_discount_applies_to_previous_item(monkeypatch):
    fake_ocr_text = """
    CHEESE
    9.99
    /123
    2.50-
    SUBTOTAL
    7.49
    TAX
    0.60
    TOTAL
    8.09
    """

    monkeypatch.setattr(parse_receipt, "image_to_text", lambda _: fake_ocr_text)

    result = image_to_dict("fake.jpg")

    item = result["items"][0]

    assert item["price"] == 9.99
    assert item["discount"] == 2.50
    assert item["effective_price"] == 7.49


def test_liquor_tax_skipped(monkeypatch):
    fake_ocr_text = """
    WINE
    19.99
    LIQUOR TAX
    TAX
    2.00
    SUBTOTAL
    19.99
    TAX
    1.60
    TOTAL
    21.59
    """

    monkeypatch.setattr(parse_receipt, "image_to_text", lambda _: fake_ocr_text)

    result = image_to_dict("fake.jpg")

    assert len(result["items"]) == 2
    assert result["items"][0]["name"] == "WINE"


def test_image_to_text_called_once(monkeypatch):
    calls = {"count": 0}

    def mock_image_to_text(_):
        calls["count"] += 1
        return "TOTAL\n1.00\n0.10\n"

    monkeypatch.setattr(parse_receipt, "image_to_text", mock_image_to_text)

    image_to_dict("fake.jpg")

    assert calls["count"] == 1


def test_image_to_text(monkeypatch):
    # Mock image returned by cv2.imread
    fake_image = MagicMock(name="FakeImage")

    # Patch cv2.imread to return fake_image
    monkeypatch.setattr(cv2, "imread", lambda path: fake_image)

    # Patch cv2.cvtColor to just return the input (bypass actual color conversion)
    monkeypatch.setattr(cv2, "cvtColor", lambda img, flag: img)

    # Patch cv2.bilateralFilter to just return the input (bypass actual filter)
    monkeypatch.setattr(
        cv2, "bilateralFilter", lambda img, d, sigmaColor, sigmaSpace: img
    )

    # Patch pytesseract.image_to_string to return a fixed string
    monkeypatch.setattr(
        pytesseract, "image_to_string", lambda img: "Mocked OCR text"
    )

    result = parse_receipt.image_to_text("dummy_path.jpg")
    assert result == "Mocked OCR text"


def test_dict_to_excel_creates_file():
    # Example input data
    data = [
        {"name": "milk", "price": 3.5},
        {"name": "bread", "price": 2.0},
    ]

    # Use a temporary file path
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
        output_path = tmp.name

        # Call the function
        dict_to_excel(data, output_path)

        # Check the file exists
        assert Path(output_path).exists()

        # Read the Excel back and check contents
        df = pd.read_excel(output_path)
        assert df.shape == (2, 2)  # 2 rows, 2 columns
        assert list(df.columns) == ["name", "price"]
        assert df.iloc[0]["name"] == "milk"
        assert df.iloc[1]["price"] == 2.0
