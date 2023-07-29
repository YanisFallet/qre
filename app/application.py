import os, sys, sqlite3
import pandas as pd
import streamlit as st

import model_
import macro_
import combined_

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from core.api_utils import authentificate, update_all_alerts
from core.utilities import clean_databases_outliers

st.set_page_config(layout="wide")

def authentication_error_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            st.sidebar.error('Authentication error. Please check your credentials.')
    return wrapper

def get_city_databases():
    root = "/Users/yanisfallet/sql_server/jinka"
    return [database.replace("database_", "").replace(".db", "") for database in os.listdir(root)]

def get_tables(city, conn):
    return pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)

@authentication_error_decorator
def authentificate_wrapper():
    return authentificate(email, password)

with st.sidebar:
    st.title(':blue[DASHBOARD]')
    st.write('Please enter your credentials below.')
    email = st.text_input('Email', key='email', value='yanis.fallet@gmail.com')
    password = st.text_input('Password', key='password', type='password', value="yanoufallet38618")

    update = st.button('Fetch new ads', key='update')
        
    databases = get_city_databases()

    if update:
        if authentificate_wrapper():
            st.info('Fetching new ads...')
            update_all_alerts(email=email, password=password)
            # clean_databases_outliers()
            with open('api_utils.log', 'r') as f:
                data = [line.strip("\n").split("-")[4] for line in f.readlines()[-len(databases)-1:]]
            for elem in data:
                st.info(elem)


unique_city, cities_comparison = st.tabs(["City", "Cities comparison"])

with unique_city:
    city = st.selectbox('Pick a city', databases, key='database')
    conn = sqlite3.connect(f"/Users/yanisfallet/sql_server/jinka/database_{city}.db")
    data_available = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    if data_available.shape[0] == 2:
        rent, invest, combined_invest_rent, macro = st.tabs(["Rent", "Invest", "Combined invest & rent", "Macro"])
        with rent:
            rent = model_.ModelApp(city, conn, "rent")
            rent.run()
        with invest:
            inv = model_.ModelApp(city, conn, "invest")
            inv.run()
        with combined_invest_rent:
            pass
        # with macro:
        #     macro = macro_.MacroApp(city)
        #     macro.run()
            
    elif data_available.iloc[0]["name"].endswith("rent"):
        rent, macro= st.tabs(["Rent", "Macro"])
        with rent :
            rent = model_.ModelApp(city, conn, "rent")
            rent.run()
        # with macro:
        #     macro = macro_.MacroApp(city)
        #     macro.run()
    else :
        invest, macro = st.tabs(["Invest", "Macro"])
        with invest:
            inv = model_.ModelApp(city, conn, "invest")
            inv.run()
        # with macro:
        #     macro = macro_.MacroApp(city)
        #     macro.run()
            

with cities_comparison:
    pass
            

    







