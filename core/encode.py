import requests
import os
import urllib.parse
import logging

from address_extraction import extract_address

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w', filename='encode.log')

def encodage(lieux : list, postcode : str, city):
    api_url = "https://api-adresse.data.gouv.fr/search/?q="
    score = {}
    for lieu in lieux:
        adr = f"{lieu}, {postcode}, {city}"
        r = requests.get(api_url + urllib.parse.quote(adr))
        if r.status_code == 200:
            js = r.json()
            i = 0
            length = len(js["features"])
            while i < length :
                if js["features"][i]["properties"]["postcode"] == postcode:
                    score[js["features"][i]["properties"]["score"]] = js["features"][i]["geometry"]["coordinates"]
                i += 1
        else:
            logging.warning("The request has failed")
            return None, None
    if len(score) == 0:
        return None, None
    else :
        logging.info("Encoding succeeded => " + str(score[max(score.keys())]))
        return score[max(score.keys())]
    
    
def manual_encoding():
    root = "/Users/yanisfallet/sql_server/jinka/"
    for database in os.listdir(root):
        conn = sqlite3.connect(os.path.join(root, database))
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
        for table in tables.itertuples():
            lat_none = pd.read_sql_query(f"SELECT description, postal_code, city, id FROM {table[0]} WHERE processed = 'False'", conn)
            for row in lat_none.itertuples():
                lng, lat = encodage(extract_address(row[1]), row[2], row[3])
                
                
                
        pass
if __name__ == "__main__":
    import sqlite3
    import pandas as pd
    lat_none = pd.read_sql_query("SELECT description, postal_code FROM ads_Grenoble_for_invest WHERE lat IS NULL", sqlite3.connect("/Users/yanisfallet/sql_server/jinka/database_Grenoble.db"))
    for row in lat_none.itertuples():
        encodage(extract_address(row[1]), row[2], 'Grenoble')

        