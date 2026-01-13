"""
main code orchestrating the receipt parsing and categorization process.
"""

from .parse_receipt import image_to_dict
from datetime import datetime
from .categorize_items import categorize_items
from .get_receipt import find_images
from .move_receipts import move_file
from .save_results import dict_to_excel
from pathlib import Path


image_path = find_images(Path.cwd() / "src_img")
for image in image_path:
    receipt_data = image_to_dict(image)
    categorized_data = categorize_items(receipt_data)
    dict_to_excel(
        categorized_data["items"],
        Path.cwd()
        / "output"
        / f'this_receipt_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{datetime.now().microsecond // 1000:03d}.xlsx',
    )
    move_file(image, Path.cwd() / "processed_img")
