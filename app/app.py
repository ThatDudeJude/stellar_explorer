import streamlit as st
from astropy.coordinates import SkyCoord
from astropy.visualization import quantity_support
from astropy.table import Table

st.title("Stellar Coordinate Explorer")

# Sidebar

sidebar = st.sidebar

with sidebar:
    with st.expander("Data Source"):
        # st.subheader("Data Source")
        data_source = st.radio("Select data source", ['File Upload', 'Live Gaia DR3 ADQL'])
    
        if data_source == 'File Upload':
            st.write("File Uploading")
            file = st.file_uploader("Upload a CSV/FITS file", accept_multiple_files=False)    
            if file:
                table = Table.read(file)
        elif data_source == 'Live Gaia DR3 ADQL':
            st.write("Fetch with Astroquery")
        else:
            st.write("Something Went Wrong!")
    # st.write("Filters")
    # st.write("Coordinate Frame")
    # st.write("Download")
    # st.write("Dataset Info")
    # st.write("Help/Legend")




# Tabs

sky_map_tab, cmd_tab, hr_tab, distance_tab, three_d_xyz_tab = st.tabs(["Sky Map", "CMD", "HR Diagram", "Distance", "3D XYZ"])
    

with sky_map_tab:
    st.header("Sky Map")
    if data_source == 'File Upload' and file:
        st.write("Table")
    

with cmd_tab:
    st.header("Colour-Magnitude Diagram")    
    
with hr_tab:
    st.header("Hertzsprung-Russel Diagram")
    
with distance_tab:
    st.header("Distance (Parallax)")
    
with three_d_xyz_tab:
    st.header("3D XYZ Plot")