
import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="Location Pin Map", layout="centered")
st.title("Location Pin Map")
st.write("Enter a latitude and longitude to drop a pin on the map.")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0,
                          value=39.3299, step=0.0001, format="%.4f",
                          help="North is positive, south is negative (-90 to 90)")
with col2:
    lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0,
                          value=-76.6205, step=0.0001, format="%.4f",
                          help="East is positive, west is negative (-180 to 180)")

zoom = st.slider("Zoom level", min_value=2, max_value=18, value=12)

# Build the map centered on the chosen point, with a pin icon on it
m = folium.Map(location=[lat, lon], zoom_start=zoom, tiles="OpenStreetMap")
folium.Marker(
    location=[lat, lon],
    tooltip="Selected location",
    popup=f"Lat: {lat:.4f}<br>Lon: {lon:.4f}",
    icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
).add_to(m)

# key ties to the coordinates so the map re-centers whenever they change
st_folium(m, width=700, height=450, key=f"map_{lat}_{lon}_{zoom}",
          returned_objects=[])

st.caption(f"Showing pin at **{lat:.4f}, {lon:.4f}**")