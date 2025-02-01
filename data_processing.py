import os
import pandas as pd
import dmoxml  # handles XML fetching and conversion to DataFrame and CSV

DATA_DIR = "data"

def scrape_data():
    """
    Fetches XML from DMO, processes the XML data,
    saves it as a CSV and returns a DataFrame.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    df = dmoxml.process_dmo_xml()
    df = dmoxml.load_df_from_csv()
    return df


def load_data():
    """
    Loads the XML from directory, processes the XML data,
    saves it as a CSV and returns a DataFrame.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    df = dmoxml.process_dmo_xml()
    df = dmoxml.load_df_from_csv()
    return df


def filter_conventional_gilts(df):
    """
    Filters out non-Conventional Gilts.

    Parameters:
        df (pd.DataFrame): The full DataFrame.

    Returns:
        pd.DataFrame: Filtered DataFrame containing only conventional gilts.
    """
    # .strip() is required since DMO leaves a ' ' (space) after Conventional in raw data!
    return df[df['INSTRUMENT_TYPE'].str.strip() == 'Conventional']