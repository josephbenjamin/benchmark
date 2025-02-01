import os
import time
import random
import requests
import pandas as pd
import xml.etree.ElementTree as ET

data_dir = "data"
os.makedirs(data_dir, exist_ok=True)


def fetch_dmo_xml():
    url = "https://www.dmo.gov.uk/data/XmlDataReport?reportCode=D1A"
    xml_file_path = os.path.join(data_dir, "dmo_data.xml")

    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
        ]),
        "Referer": "https://www.dmo.gov.uk/",
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
        "Connection": "keep-alive"
    }

    session = requests.Session()
    session.headers.update(headers)

    time.sleep(random.uniform(1, 3))  # Simulate human browsing

    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            with open(xml_file_path, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"XML data saved to {xml_file_path}")
        else:
            print(f"Failed to fetch data: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def process_dmo_xml(xml_file_path=None):

    if xml_file_path == None:
        xml_file_path = os.path.join(data_dir, "dmo_data.xml")
    csv_file_path = os.path.join(data_dir, "dmo_data.csv")

    if not os.path.exists(xml_file_path):
        print(f"XML file not found at {xml_file_path}. Please fetch or manually download the file.")
        return None

    try:
        with open(xml_file_path, "r", encoding="utf-8") as file:
            xml_data = file.read()

        root = ET.fromstring(xml_data)
        records = [{attr: elem.attrib[attr] for attr in elem.attrib} for elem in root.findall("View_GILTS_IN_ISSUE")]

        df = pd.DataFrame(records)

        date_columns = ["CLOSE_OF_BUSINESS_DATE", "REDEMPTION_DATE", "FIRST_ISSUE_DATE", "CURRENT_EX_DIV_DATE"]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        df.to_csv(csv_file_path, index=False)
        print(f"CSV data saved to {csv_file_path}")
        return df
    except Exception as e:
        print(f"Error processing XML file: {e}")
        return None


if __name__ == "__main__":
    # fetch_dmo_xml()
    df = process_dmo_xml("data/XmlDataReport.xml")
    if df is not None:
        print(df.head())
