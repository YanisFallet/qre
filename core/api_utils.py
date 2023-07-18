import requests
import logging
import pandas as pd
import sqlite3
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

logging.basicConfig(filename='api_utils.log',filemode="w" , level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        raise Exception(f'Authentification failed with error {r_auth.status_code}')

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
    'unread':[], 'favorite':[], 'contact':[], 'deleted':[], 'type':[], 'zone' : [], 'token':[]}
    for counter, alert in enumerate(r_alerts.json()):

        data_dict['id'].append(alert['id'])
        data_dict['name'].append(alert['name'])
        data_dict['user_name'].append(alert['user_name'])
        data_dict['ads_per_day'].append(alert['estimated_ads_per_day'])
        data_dict['type'].append(alert['search_type'])
        data_dict['zone'].append([zone['name'] for zone in alert['where_zone']])
        data_dict['token'].append(alert['token'])
        
        if len(alert["where_zone"]) == 0:
            data_dict['zone'].pop()
            data_dict['zone'].append([alert['geopoints'][0]["latLng"], alert['geopoints'][0]["radius"]])

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

def build_link(token, id):
    return f"https://www.jinka.fr/alert_result?token={token}&ad={id}&from=dashboard_card&from_alert_filter=all"

def contains_digit(string):
    return any(char.isdigit() for char in string)

def update_one_alert(session : requests.Session, headers, alert_serie : tuple):
    alert_serie_content = alert_serie[1]
    if isinstance(alert_serie_content['zone'][0], list) or contains_digit(alert_serie_content['zone'][0]):
        city = alert_serie_content['user_name'].strip().replace(" ", "_")
    else :
        city = "_".join(alert_serie_content['zone']).replace("-",'_').replace(" ", "_")
    search_type = alert_serie_content['type']
    root_url = 'https://api.jinka.fr/apiv2/alert/' + str(alert_serie_content["id"]) + '/dashboard'
    df_apparts = pd.DataFrame(columns= ['id', 'source', 'source_label', 'search_type', 'owner_type', \
        'rent', 'area', 'room', 'bedroom', 'floor', 'type', 'buy_type', 'city', 'postal_code', 'lat', 'lng',  'furnished', \
        'description', 'created_at', 'expired_at', 'sendDate', \
        'new_real_estate', 'features', 'alert_id', 'link'])
    
    with sqlite3.connect(f"/Users/yanisfallet/sql_server/jinka/database_{city}.db") as conn:
        c = conn.cursor()
        if_exists = c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='ads_{city}_{search_type}'").fetchall()
        if len(if_exists) == 0:
            id = []
        else :
            id = c.execute(f"SELECT id FROM ads_{city}_{search_type}").fetchall()
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
                elif ad["new_real_estate"] == None:
                    df_temp = pd.DataFrame.from_records(data=[ad])
                    df_temp['link'] = build_link(alert_serie_content['token'], ad['id'])
                    df_apparts = pd.concat([df_apparts,df_temp], axis=0, join="inner")
            page += 1            
        logging.info(f'{len(df_apparts)} new ads have been found for alert {alert_serie_content["user_name"]}')
        df_apparts["pm2"] = df_apparts["rent"] / df_apparts["area"]
        df_apparts['features'] = df_apparts['features'].apply(lambda x: str(x))
        df_apparts['new_real_estate'] = df_apparts['new_real_estate'].apply(lambda x: str(x))
        df_apparts.to_sql(f'ads_{city}_{search_type}', conn, if_exists='append', index=False)

def update_all_alerts(email : str, password : str):
    session, headers = authenticate(email, password)
    df_alerts = get_alerts(session, headers)
    with ThreadPoolExecutor() as executor:
        executor.map(partial(update_one_alert, session, headers), df_alerts.iterrows())
        
        
def update_all_alerts_iterativ(email : str, password : str):
    session, headers = authenticate(email, password)
    df_alerts = get_alerts(session, headers)
    for alert in tqdm(df_alerts.iterrows()):
        update_one_alert(session, headers, alert)


if __name__ == "__main__":
    update_all_alerts_iterativ("yanis.fallet@gmail.com", "yanoufallet38618")