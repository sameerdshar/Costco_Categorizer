import pandas as pd


def dict_to_excel(data: dict, output_path: str):
    '''
    Save structured data dictionary to an Excel file.
    Args:
        data (dict): Structured data to be saved.
        output_path (str): Path to the output Excel file.'''
    df = pd.DataFrame(data, columns=data[0].keys())
    df.to_excel(output_path, index=False)
