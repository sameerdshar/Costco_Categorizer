from .product_dictionary import ESSENTIAL_LIST


def categorize_items(receipt_data):
    """
    Categorize items in the receipt data as essential or non-essential.
    Args:
        receipt_data (dict): Structured data extracted from the receipt.
    Returns:
        dict: Receipt data with categorized items.
    """
    for item in receipt_data["items"]:
        for product in ESSENTIAL_LIST:
            if product in item["name"]:
                item["name"] = product  # Standardize the name
                break
        if item["name"] in ESSENTIAL_LIST or item["effective_price"] < 20.00:
            item["category"] = "essential"
        else:
            item["category"] = ""
    return receipt_data
