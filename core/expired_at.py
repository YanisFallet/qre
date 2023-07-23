import requests, sqlite3, os

import api_utils

s, headers = api_utils.authentificate('yanis.fallet@gmail.com', 'yanoufallet38618')
alert = api_utils.get_alerts(s, headers).iloc[0,:]

def contains_digit(string):
    return any(char.isdigit() for char in string)

def manage_expired_one_ad(session : requests.Session, headers : dict, alert_serie):
    alert_serie_content = alert_serie[1]
    if isinstance(alert_serie_content['zone'][0], list) or contains_digit(alert_serie_content['zone'][0]):
        city = alert_serie_content['user_name'].strip().replace(" ", "_")
    else :
        city = "_".join(alert_serie_content['zone']).replace("-",'_').replace(" ", "_")
    search_type = alert_serie_content['type']
    root_url = 'https://api.jinka.fr/apiv2/alert/' + str(alert["id"]) + '/dashboard' 

    with sqlite3.connect(os.path.join(os.path.expanduser('~'), f"sql_server/jinka/database_{city}.db")) as conn:
        c = conn.cursor()
        if_exists = c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='ads_{city}_{search_type}'").fetchall()
        if len(if_exists) == 0:
            id = []
        else :
            id = c.execute(f"SELECT id FROM ads_{city}_{search_type}").fetchall()
            id = [i[0] for i in id]
        page = 0
        while page <= alert_serie_content["nb_pages"]:
            target_url = root_url + f'?filter=all&page={page}&sorting=default'
            data_apparts = session.get(target_url, headers=headers).json()['ads']
            for ad in data_apparts :
                if ad['id'] in id:
                    c.execute(f"UPDATE ads_{city}_{search_type} SET expired_at = '{ad['expired_at']}' WHERE id = '{ad['id']}'")