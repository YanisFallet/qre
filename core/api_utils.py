import requests
import logging


logging.basicConfig(filename = "api_utils.log", filemode="w" , level = logging.INFO, format = "%(asctime)s-%(levelname)s-%(message)s")

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

if __name__ == "__main__":
    s, headers = authenticate('yanis.fallet@gmail.com', "yanoufallet38618")