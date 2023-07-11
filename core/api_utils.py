import requests
import logging
import json
import pandas as pd
import sqlite3
from unidecode import unidecode
from functools import partial
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(filename="api_utils.log", filemode="w" , level = logging.INFO, format = "%(asctime)s-%(levelname)s-%(message)s")

def authenticate(email, password):
    auth_url = 'https://api.jinka.fr/apiv2/user/auth'
    auth_dict = {'email':email, 'password':password}
    s = requests.Session()
    r_auth = s.post(auth_url, auth_dict)
    if r_auth.status_code == 200:
        logging.info('Authentification succeeded (200)')
        access_token = r_auth.json()['access_token']
    else:
        logging.critical(f'Authentification failed with error {r_auth.status_code}')
        return None, None

    headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}',
    'Origin': 'https://www.jinka.fr',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Sec-GPC': '1',
    'If-None-Match': 'W/f46-qWZd5Nq9sjWAv9cj3oEhFaxFuek',
    'TE': 'Trailers',
    }
    return s, headers

def get_alerts(session : requests.Session, headers):
    r_alerts = session.get('https://api.jinka.fr/apiv2/alert', headers=headers)
    df_alerts = pd.DataFrame(columns=['id', 'name', 'user_name', 'ads_per_day'])
    data_dict = {'id':[], 'name':[], 'user_name':[], 'ads_per_day':[], 'nb_pages':[], 'all':[], 'read':[],
    'unread':[], 'favorite':[], 'contact':[], 'deleted':[]}
    for counter, alert in enumerate(r_alerts.json()):

        data_dict['id'].append(alert['id'])
        data_dict['name'].append(alert['name'])
        data_dict['user_name'].append(alert['user_name'])
        data_dict['ads_per_day'].append(alert['estimated_ads_per_day'])

        root_url = 'https://api.jinka.fr/apiv2/alert/' + str(alert['id']) + '/dashboard' 

        r_pagination = session.get(root_url, headers=headers)
        pagination_data = r_pagination.json()['pagination']
        data_dict['nb_pages'].append(pagination_data['nbPages'])
        data_dict['all'].append(pagination_data['totals']['all'])
        data_dict['read'].append(pagination_data['totals']['read'])
        data_dict['unread'].append(pagination_data['totals']['unread'])
        data_dict['favorite'].append(pagination_data['totals']['favorite'])
        data_dict['contact'].append(pagination_data['totals']['contact'])
        data_dict['deleted'].append(pagination_data['totals']['deleted'])

        logging.info(f'{counter+1} / {len(r_alerts.json())} alerts have been processed.')

    df_alerts = pd.DataFrame(data=data_dict)  
    return df_alerts

def update_one_alert(session : requests.Session, headers, alert_serie : tuple):
    alert_serie_content = alert_serie[1]
    city = unidecode(alert_serie_content['user_name'].replace(' ', '_').lower())
    root_url = 'https://api.jinka.fr/apiv2/alert/' + str(alert_serie_content["id"]) + '/dashboard'
    df_apparts = pd.DataFrame(columns= ['id', 'source', 'source_label', 'search_type', 'owner_type', \
        'rent', 'area', 'room', 'bedroom', 'floor', 'type', 'buy_type', 'city', 'postal_code', 'lat', 'lng',  'furnished', \
        'description', 'created_at', 'expired_at', 'sendDate', \
        'new_real_estate', 'features', 'alert_id'])
    
    with sqlite3.connect(f"/Users/yanisfallet/sql_server/jinka/database_{city}.db") as conn:
        c = conn.cursor()
        if_exists = c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='ads_{city}'").fetchall()
        if len(if_exists) == 0:
            id = []
        else :
            id = c.execute(f"SELECT id FROM ads_{city}").fetchall()
            id = [i[0] for i in id]
        page = 0
        flag = True
        while page <= alert_serie_content["nb_pages"] and flag:
            target_url = root_url + f'?filter=all&page={page}&sorting=default'
            data_apparts = session.get(target_url, headers=headers).json()['ads']
            for ad in data_apparts :
                if ad['id'] in id:
                    flag = False
                    break
                else:
                    df_apparts = pd.concat([df_apparts,pd.DataFrame.from_records(data=[ad])], axis=0, join="inner")
            logging.info(f"Page {page} / {alert_serie_content['nb_pages']} has been processed")
            page += 1            
        logging.info(f'{len(df_apparts)} new ads have been found for alert {alert_serie_content["user_name"]}')
        df_apparts["pm2"] = df_apparts["rent"] / df_apparts["area"]
        df_apparts['features'] = df_apparts['features'].apply(lambda x: str(x))
        df_apparts['new_real_estate'] = df_apparts['new_real_estate'].apply(lambda x: str(x))
        df_apparts.to_sql(f'ads_{city}', conn, if_exists='append', index=False)

def update_all_alerts(email : str, password : str):
    session, headers = authenticate(email, password)
    df_alerts = get_alerts(session, headers)
    print(df_alerts)
    with ThreadPoolExecutor() as executor:
        print("Updating alerts...")
        executor.map(partial(update_one_alert, session, headers), df_alerts.iterrows())

if __name__ == "__main__":
    with open('./logs.json', 'r') as f:
        config = json.load(f)
    # s, headers = authenticate(**config)
    # alert = get_alerts(s, headers).iloc[4,:]
    # print(alert)
    # update_one_alert(s, headers, alert)
    update_all_alerts(**config)