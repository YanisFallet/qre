import requests
import urllib.parse
import logging

import sys, os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from core.address_extraction import extract_address
from core.utilities import connect_to_database



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
    
@connect_to_database
def manual_encoding(cursor, table_name):
    lat_none = cursor.execute(f"SELECT description, postal_code, city, id FROM {table_name} WHERE processed = 0").fetchall()
    for row in lat_none:
        lng, lat = encodage(extract_address(row[0]), row[1], row[2])
        cursor.execute(f"UPDATE {table_name} SET lat = '{lat}', lng = '{lng}', processed = 1 WHERE id = '{row[3]}'")
                
                
if __name__ == "__main__":
    manual_encoding()

        