import os, sys, re
import pandas as pd
import streamlit as st
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from core.api_utils import authenticate, update_all_alerts

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

@authentication_error_decorator
def authentificate_wrapper():
    return authenticate(email, password)

databases = get_city_databases()

st.sidebar.title(':blue[DASHBOARD]')
st.sidebar.write('Please enter your credentials below.')
email = st.sidebar.text_input('Email', key='email', value='yanis.fallet@gmail.com')
password = st.sidebar.text_input('Password', key='password', type='password', value="")

update = st.sidebar.button('Fetch new ads', key='update')
    
if update:
    if authentificate_wrapper():
        st.sidebar.info('Fetching new ads...')
        update_all_alerts(email=email, password=password)
        with open('api_utils.log', 'r') as f:
            data = [line.strip("\n").split("-")[4] for line in f.readlines()[-len(databases)+1:]]
        for elem in data:
            st.sidebar.info(elem)
            
st.selectbox('Select a city', options=databases, key='city')
    







