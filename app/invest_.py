import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import pydeck as pdk

def screener_pm2(city, conn):
    load_pm2_rent_for_invest = pd.read_sql_query(f"SELECT pm2, link FROM ads_{city}_for_invest ", conn)
    return load_pm2_rent_for_invest.sort_values(by="pm2", ascending=True)
    
def app_invest(city, conn):
    col1, col2 = st.columns([2,1])
    alpha = col2.dataframe(screener_pm2(city, conn), hide_index=True)
    df = pd.read_sql_query(f"SELECT area, pm2, room, link FROM ads_{city}_for_invest", conn)
    geo_coord = pd.read_sql_query(f"SELECT lat, lng, pm2 FROM ads_{city}_for_invest WHERE lat != 'None'", conn)
    
    geo_coord.columns = ['lat', 'lon', 'pm2']
    fig = px.scatter(
                df,
                x="area",
                y="pm2",
                color="room",
                hover_name="link",
                color_continuous_scale=px.colors.sequential.Viridis,
                trendline="ols")
    col1.plotly_chart(fig, use_container_width=True)
    
    
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=geo_coord["lat"].mean(),
            longitude=geo_coord["lon"].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
            'ColumnLayer',
            data=geo_coord,
            get_position=['lon', 'lat'],
            radius=20,
            elevation_scale=0.2,
            pickable=True,
            extruded=True,
            get_elevation = "pm2",
            get_fill_color=[255, 165, 0, 80],
            )
        ]
    ))
    

