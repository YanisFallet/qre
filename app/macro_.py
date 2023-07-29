import streamlit as st
import pandas as pd
import requests
import sqlite3 as sql

"/Users/yanisfallet/sql_server/data_historique_immobilier/communes.db"


class MacroApp:
    
    def __init__(self, city : str):
        commune = pd.read_sql_query(f"SELECT DISTINCT code_commune_INSEE FROM communes WHERE nom_commune_postal = '{city.upper()}'", sql.connect("/Users/yanisfallet/sql_server/data_historique_immobilier/communes.db"))
        self.req = pd.read_html(f"https://www.insee.fr/fr/statistiques/2011101?geo=COM-{commune['code_commune_INSEE'].iloc[0]}#chiffre-cle-1", decimal=',', thousands=' ')
        
    def display_data(self):
        for tableau in self.req:
            st.dataframe(tableau)
    
    def run(self):
        self.display_data()
            
if __name__ == "__main__":
    app = MacroApp("Grenoble")
    