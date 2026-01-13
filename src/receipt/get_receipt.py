def find_images(directory):
    """
    Find all .jpg and .jpeg images in the given directory.
    Args:
        directory (Path): Path to the directory to search for images.
    Returns:
        list: List of Paths to the found image files.
    """
    return list(directory.glob("*.jpg")) + list(directory.glob("*.jpeg"))
