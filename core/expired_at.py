import requests, sqlite3, os
from functools import partial
from concurrent.futures import ThreadPoolExecutor

import api_utils


def contains_digit(string):
    return any(char.isdigit() for char in string)

def manage_expired_one_ad(session : requests.Session, headers : dict, alert_serie):
    alert_serie_content = alert_serie[1]
    if isinstance(alert_serie_content['zone'][0], list) or contains_digit(alert_serie_content['zone'][0]):
        city = alert_serie_content['user_name'].strip().replace(" ", "_")
    else :
        city = "_".join(alert_serie_content['zone']).replace("-",'_').replace(" ", "_")
    search_type = alert_serie_content['type']
    root_url = 'https://api.jinka.fr/apiv2/alert/' + str(alert_serie_content["id"]) + '/dashboard' 

    with sqlite3.connect(os.path.join(os.path.expanduser('~'), f"sql_server/jinka/database_{city}.db")) as conn:
        c = conn.cursor()
        if_exists = c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='ads_{city}_{search_type}'").fetchall()
        if len(if_exists) == 0:
            id = []
        else :
            id = c.execute(f"SELECT id FROM ads_{city}_{search_type}").fetchall()
            id = [i[0] for i in id]
        page = alert_serie_content["nb_pages"]
        while page > 0:
            target_url = root_url + f'?filter=all&page={page}&sorting=default'
            data_apparts = session.get(target_url, headers=headers).json()['ads']
            for ad in data_apparts :
                if not ad['expired_at'] is None and ad['id'] in id:
                    c.execute(f"UPDATE ads_{city}_{search_type} SET expired_at = '{ad['expired_at']}' WHERE id = '{ad['id']}'")
                    print(f"UPDATE ads_{city}_{search_type} SET expired_at = '{ad['expired_at']}' WHERE id = '{ad['id']}'")
            page -= 1
            
def manage_expired_all_ads(email : str, password : str):
    s, headers = api_utils.authentificate(email, password)
    alert = api_utils.get_alerts(s, headers)
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(partial(manage_expired_one_ad, s, headers), alert.iterrows())
        
if __name__ == "__main__":
    manage_expired_all_ads('yanis.fallet@gmail.com', 'yanoufallet38618')