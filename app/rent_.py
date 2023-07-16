import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pydeck as pdk

class RentApp:
    def __init__(self, city, conn):
        self.city = city
        self.conn = conn
        self.data = pd.read_sql_query(f"SELECT area, pm2, room, link, created_at, id FROM ads_{city}_for_rent", conn)
        self.df = self.data[['area', 'pm2', 'room', 'link']]
        self.historical = self.data[['created_at', 'pm2', 'id']]
        self.geo_coord = pd.read_sql_query(f"SELECT lat, lng, pm2 FROM ads_{city}_for_rent WHERE lat != 'None'", conn)
        self.COLOR_RANGE = [
            [65, 182, 196],
            [127, 205, 187],
            [199, 233, 180],
            [237, 248, 177],
            [255, 255, 204],
            [255, 237, 160],
            [254, 217, 118],
            [254, 178, 76],
            [253, 141, 60],
            [252, 78, 42],
            [227, 26, 28],
            [189, 0, 38],
            [128, 0, 38],
        ]
        self.BREAKS = np.quantile(self.df["pm2"], np.linspace(0, 1, len(self.COLOR_RANGE))).tolist()
                
    def screener_pm2(self):
        load_pm2_rent_for_invest = pd.read_sql_query(f"SELECT pm2, rent,link FROM ads_{self.city}_for_rent ", self.conn)
        return load_pm2_rent_for_invest.sort_values(by="pm2", ascending=True)
    
    def plot_pm2_vs_area(self):
        fig, ax = plt.subplots(figsize=(7, 5))
        fig = px.scatter(self.df, x="area", y="pm2", color="room", hover_data=['link'], trendline="ols", color_continuous_scale=px.colors.sequential.Viridis, trendline_color_override="red", log_y=False)
        fig.update_traces(marker_size=3)
        fig.update_layout(
            xaxis_title="Area",
            yaxis_title="PM2",
            title="PM2 vs Area",
            legend_title="Room",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        return fig
    
    def color_scale(self, val):
        for i, b in enumerate(self.BREAKS):
            if val < b:
                return self.COLOR_RANGE[i]
        return self.COLOR_RANGE[i]

    def calculate_elevation_min_max(self, val : float):
        return (val - self.df["pm2"].min()) / (self.df["pm2"].max() - self.df["pm2"].min()) * 1000
    
    def spread_geo_coords(self, lat : float):
        """this function is used to spread the geo coordinates to avoid overlapping"""
        return lat + np.random.normal(scale=0.0001)
    
    def apply_geo_coord_spreading_only_for_overlapping_assets(self):
        """this function is used to spread the geo coordinates to avoid overlapping"""
        self.geo_coord["lat"] = self.geo_coord["lat"].apply(self.spread_geo_coords)
        self.geo_coord["lng"] = self.geo_coord["lng"].apply(self.spread_geo_coords)
    
    def plot_map(self):
        self.apply_geo_coord_spreading_only_for_overlapping_assets()
        self.geo_coord["elevation"] = self.geo_coord["pm2"].apply(self.calculate_elevation_min_max)
        self.geo_coord["fill_color"] = self.geo_coord["pm2"].apply(self.color_scale)

        layer = pdk.Layer(
            "ColumnLayer",
            data = self.geo_coord,
            get_position=["lng", "lat"],
            get_elevation="elevation",
            get_fill_color="fill_color",
            pickable=True,
            radius = 20,
        )
        initial_view_state = pdk.ViewState(
            latitude=self.geo_coord["lat"].mean(),
            longitude=self.geo_coord["lng"].mean(),
            zoom=11,
            pitch=50,
            bearing=self.bearing
        )
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=initial_view_state,
            tooltip={"text": "PM2: {pm2}"}
        )
        return r
    
    def plot_historical_pm2(self):
        self.historical.set_index('created_at', inplace=True)
        self.historical.index = pd.to_datetime(self.historical.index)
        self.resample = self.historical.resample('M').agg({'pm2': 'mean', 'id': 'count'})
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=self.resample.index, y=self.resample['pm2'], name="PM2", offsetgroup=1), secondary_y=False)
        fig.add_trace(go.Bar(x=self.resample.index, y=self.resample['id'], name="Number of Assets", offsetgroup=2, opacity=0.2), secondary_y=True)
        fig.update_layout(title="Historical PM2")
        return fig
        
    def run(self):
        col1, col2 = st.columns([2,1])
        col2.dataframe(self.screener_pm2(), hide_index=True)
        col1.plotly_chart(self.plot_pm2_vs_area())
        self.bearing = st.select_slider("Move the bearing", options=[0, 45, 90, 135, 180, 225, 270, 315], value=0, key="bearing_rent")
        st.pydeck_chart(self.plot_map())
        st.plotly_chart(self.plot_historical_pm2())
