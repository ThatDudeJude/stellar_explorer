import streamlit as st
from astropy.coordinates import SkyCoord
from astropy.visualization import quantity_support
from astropy.table import Table
import plotly.express as px
import numpy as np
from utils import load_fits, add_galactic_coords, add_abs_mag, add_distance_pc

quantity_support()
st.title("Stellar Coordinate Explorer")

# Sidebar

sidebar = st.sidebar

with sidebar:
    with st.expander("Data Source"):
        # st.subheader("Data Source")
        data_source = st.radio("Select data source", ['File Upload', 'Live Gaia DR3 ADQL'])
        source_is_loaded = False
        if data_source == 'File Upload':
            st.write("File Uploading")
            file = st.file_uploader("Upload a CSV/FITS file", accept_multiple_files=False, )    
            if file:
                sources_df = load_fits(file)
                source_is_loaded = True
        elif data_source == 'Live Gaia DR3 ADQL':
            st.write("Fetch with Astroquery")
        else:
            st.write("Something Went Wrong!")
            
    with st.expander("Coordinate Frame"):
        coord_frame = st.radio("Select Coordinate System", ['ICRS (RA/Dec)', 'Galactic (l/b)'])        
    
    
    # st.write("Filters")
    
    # st.write("Coordinate Frame")
    # st.write("Download")
    # st.write("Dataset Info")
    # st.write("Help/Legend")




# Tabs

sky_map_tab, cmd_tab, hr_tab, distance_tab, three_d_xyz_tab = st.tabs(["Sky Map", "CMD", "HR Diagram", "Distance", "3D XYZ"])
    
# Sky Map Tab
with sky_map_tab:        
    
    # Header
    st.header("Sky Map")
    
    # Update loaded data and check for coordinate type
    if data_source == 'File Upload' and source_is_loaded:
        
        # Add Galactic Coords, Absolute Magnitude and Distance columns
        
        sky_map_sources_df = add_galactic_coords(sources_df)
        sky_map_sources_df = add_abs_mag(sky_map_sources_df)
        sky_map_sources_df = add_distance_pc(sky_map_sources_df)
        
        # Create new abs_mag_log column for log-stetch normalization
        sky_map_sources_df['abs_mag_log'] = np.log10(sky_map_sources_df['abs_mag'])
        
        # Rename columns for hover data 
        
        sky_map_sources_df = sky_map_sources_df.rename(columns={'source_id': 'source id', 'phot_g_mean_mag': 'G mag', 'abs_mag_log': 'log(G mag)', 'bp_rp': 'BP-RP', 
                                                                'distance_pc': 'distance (pc)', 'abs_mag': 'M (G-band)', 'gal_l': 'gal l', 'gal_b': 'gal b'})
                
        
        
        # Add radio buttons for selecting colour scaling for normalization 
        
        scale_option = st.radio("Color Scale", ['Linear (G mag)', 'Log (log(G mag))'])
        scale_selected = ['G mag' if scale_option == 'Linear (G mag)' else 'log(G mag)'][0]
        min_val, max_val = [(sky_map_sources_df['G mag'].min(), sky_map_sources_df['G mag'].max()) if scale_option == 'Linear (G mag)' else (sky_map_sources_df['log(G mag)'].min(), sky_map_sources_df['log(G mag)'].max()) ][0]
        
        # Check for coordinate type and load appropriate sky map
        
        # ICRS (RA/Dec)
        if coord_frame == 'ICRS (RA/Dec)':
            
            fig = px.scatter(
                sky_map_sources_df,
                x=sky_map_sources_df['ra'],
                y=sky_map_sources_df['dec'],
                color=scale_selected,
                range_color=[min_val, max_val],                
                hover_data={'source id': True, 'G mag': ':.2f', 'BP-RP': ':.2f', 'parallax': ':.2f', 'distance (pc)': ':.1f', 'log(G mag)': False, 'M (G-band)': ':.2f'},
                labels={'ra': 'Right Ascension (&deg;)', 'dec': 'Declination (&deg;)'},
                title=f'ICRS Sky Map (N={len(sky_map_sources_df)} sources)'            
            )
        
        # Galactic (l/b)
        elif coord_frame == 'Galactic (l/b)':
            
            fig = px.scatter(
                sky_map_sources_df,
                x=sky_map_sources_df['gal l'],
                y=sky_map_sources_df['gal b'],
                color=scale_selected,
                range_color=[min_val, max_val],
                hover_data={'source id': True, 'G mag': ':.2f', 'BP-RP': ':.2f', 'parallax': ':.2f', 'distance (pc)': ':.1f', 'log(G mag)': False, 'M (G-band)': ':.2f'},
                labels={'gal b': 'Galactic Longitude (&deg;)', 'gal l': 'Galactic Latitude (&deg;)'},
                title=f'Galactic Coordinates Sky Map (N={len(sky_map_sources_df)} sources)'
            ) 
        # fig.update_layout(coloraxis_colorbar=dict(range_color=[min_val, max_val]))    
        st.plotly_chart(fig, width='stretch')
            
    

with cmd_tab:
    st.header("Colour-Magnitude Diagram")    
    
with hr_tab:
    st.header("Hertzsprung-Russel Diagram")
    
with distance_tab:
    st.header("Distance (Parallax)")
    
with three_d_xyz_tab:
    st.header("3D XYZ Plot")