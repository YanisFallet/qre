import requests
import urllib.parse
import logging

from address_extraction import extract_address


def encodage(lieux : list, city : str):
    api_url = "https://api-adresse.data.gouv.fr/search/?q="
    score = {}
    for lieu in lieux:
        adr = lieu + ", " + city
        r = requests.get(api_url + urllib.parse.quote(lieux))
        if r.status_code == 200:
            js = r.json()
            if js["features"]["properties"]["city"] == city:
                score[["features"]["properties"]["score"]] = js["features"]["geometry"]["coordinates"]
        else:
            raise Exception("Error while encoding the address")
    if len(score) == 0:
        raise Exception("No address found")
    else :
        return score[max(score.keys())]
        
if __name__  == "__main__":
    pass