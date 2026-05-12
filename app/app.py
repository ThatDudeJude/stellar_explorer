import streamlit as st
from astropy.coordinates import SkyCoord
from astropy.table import Table
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils import load_fits, add_galactic_coords, add_abs_mag, add_distance_pc

# Title
st.title("Stellar Coordinate Explorer")

# Sidebar

sidebar = st.sidebar

with sidebar:
    # Selecting source of data (file or astroquery)
    
    with st.expander("Data Source"):        
        
        # Radio buttons
        data_source = st.radio("Select data source", ['File Upload', 'Live Gaia DR3 ADQL'])
        
        # Boolean for checking is source is loaded to avoid attempting computations on empty data in tabs        
        source_is_loaded = False
        
        
        # Checking source type
        if data_source == 'File Upload':
            # File upload
            
            file = st.file_uploader("Upload a CSV/FITS file", accept_multiple_files=False, )    
            if file:
                sources_df = load_fits(file)
                source_is_loaded = True
        elif data_source == 'Live Gaia DR3 ADQL':
            st.write("Fetch with Astroquery")
        else:
            st.write("Something Went Wrong!")
    
    # Selecting coordinate frame for sky map
    
    with st.expander("Coordinate Frame"):
        coord_frame = st.radio("Select Coordinate System", ['ICRS (RA/Dec)', 'Galactic (l/b)'])        
    
    
    # Filtering sources 
    with st.expander("Filtering"):
        
        
        # Confirm data from source is loaded
        if source_is_loaded:
            
            # Apparent Magnitude Filter    
            # Obtain min and max apparent magnitudes
            min_app_mag = float(sources_df['phot_g_mean_mag'].min())
            max_app_mag = float(sources_df['phot_g_mean_mag'].max())
            
            # Select minimum and maximum aparent magnitude
            app_mag_range = st.slider("Select Apparent Magnitude Range", 
                    min_value=min_app_mag,
                    max_value=max_app_mag,
                    value=(min_app_mag, max_app_mag)
                    )
            
            # filter sources within apparent magnitude range values selected
            sources_df = sources_df[(sources_df['phot_g_mean_mag'] >= app_mag_range[0]) & (sources_df['phot_g_mean_mag'] <= app_mag_range[1])]
            
            
            # Distance Filter
            # Obtain min and max parallax
            min_parallax = float(sources_df['parallax'].min())
            max_parallax = float(sources_df['parallax'].max())
            # Convert to distance in parsec
            max_distance = 1000.0 / min_parallax 
            min_distance = 1000.0/ max_parallax
            
            # Select minimum and maximum distance
            distance_range = st.slider("Select Distance Range (in pc)", 
                                       min_value=min_distance,
                                       max_value=max_distance,
                                       value=(min_distance, max_distance))
            
            # filter sources within distance range values selected
            sources_df = sources_df[(sources_df['parallax'] >= (1000.0 / distance_range[1])) & (sources_df['parallax'] <= (1000.0 / distance_range[0]))]
            
        else:
            st.write('Load data from Data Source to apply Filtering')

        
        
    
    # st.write("Coordinate Frame")
    # st.write("Download")
    # st.write("Dataset Info")
    # st.write("Help/Legend")




# Tabs for sky map, cmd, hr diagram, 3d xyz plot

sky_map_tab, cmd_tab, hr_tab, distance_tab, three_d_xyz_tab = st.tabs(["Sky Map", "CMD", "HR Diagram", "Distance", "3D XYZ"])
    
# Sky Map Tab
with sky_map_tab:        
    
    # Header
    st.header("Sky Map")
    
    # Update loaded data and check for coordinate type
    if data_source == 'File Upload' and source_is_loaded:
        
        # Add Galactic Coords, Absolute Magnitude and Distance columns to dataframe
        
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
        
        st.plotly_chart(fig, width='stretch')
            
    else:
        st.write("To view the sky plot, select data file or fetch data to load from Data Source.")

# CMD Tab
with cmd_tab:
    st.header("Colour-Magnitude Diagram")    
        
    # Update loaded data and check for coordinate type
    if data_source == 'File Upload' and source_is_loaded:
        
        # Add Galactic Coords, Absolute Magnitude and Distance columns to dataframe
        
        cmd_sources_df = add_galactic_coords(sources_df)
        cmd_sources_df = add_abs_mag(cmd_sources_df)
        cmd_sources_df = add_distance_pc(cmd_sources_df)
        
        # Create new abs_mag_log column for log-stetch normalization
        cmd_sources_df['abs_mag_log'] = np.log10(cmd_sources_df['abs_mag'])
        
        # Rename columns for hover data 
        
        cmd_sources_df = cmd_sources_df.rename(columns={'source_id': 'source id', 'phot_g_mean_mag': 'G mag', 'abs_mag_log': 'log(G mag)', 'bp_rp': 'BP-RP', 
                                                                'distance_pc': 'distance (pc)', 'abs_mag': 'M (G-band)', 'gal_l': 'gal l', 'gal_b': 'gal b'})
        
        col1, col2 = st.columns(2)
        
        # Add radio buttons for selecting between scatter and histogram 2d contour plot        
        with col1:
            plot_selected = st.radio('Plot Type', ['Scatter', '2D Histogram Contour'])
            
            
        
        # Select radio buttons displayed in col 2 based on plot type
        with col2:
            #  Scatter plot
            if plot_selected == 'Scatter':
                # Add radio buttons for selecting colour mapping based on parallax, distance, absolute magnitude or none
                
                colour_map_var = st.radio("Variable for Colour Points", ['None', 'Parallax (mas)', 'Distance (pc)', 'G (mag)'])
                                
                # Update related arguments based on selection        
                if colour_map_var == 'None':
                    range_colour = [0, 0]
                    var_selected = None
                elif colour_map_var == 'Parallax (mas)':
                    range_colour = [cmd_sources_df['parallax'].min(), cmd_sources_df['parallax'].max()]
                    var_selected = 'parallax'
                elif colour_map_var == 'Distance (pc)':
                    range_colour = [cmd_sources_df['distance (pc)'].min(), cmd_sources_df['distance (pc)'].max()]
                    var_selected = 'distance (pc)'
                elif colour_map_var == 'G (mag)':
                    range_colour = [cmd_sources_df['G mag'].min(), cmd_sources_df['G mag'].max()]
                    var_selected = 'G mag'
            
            
            # 2D Histogram Contour
            elif plot_selected == '2D Histogram Contour':
                # Add radio buttons for selecting binning function
                
                bin_func = st.radio("Choose Binning Function", ['Count (stellar density)', 'Average (average distance per bin)'])
                
                if bin_func == 'Count (stellar density)':
                    hist_func = 'count' 
                    z_col = None
                    cb_title = 'Stars per bin'
                    hover_temp_stat = 'Count'
                elif bin_func == 'Average (average distance per bin)':
                    hist_func = 'avg'
                    z_col = cmd_sources_df['parallax']
                    cb_title = 'Average distance per bin'
                    hover_temp_stat = 'Avg Distance:'
        
        #  Plot CMD
        
        if plot_selected == 'Scatter':            
            # Scatter Plot
            
            fig = px.scatter(
                cmd_sources_df,
                x='BP-RP',
                y='G mag',
                color=var_selected,
                range_color=range_colour,
                hover_data={'source id': True, 'G mag': ':.2f', 'BP-RP': ':.2f', 'parallax': ':.2f', 'distance (pc)': ':.1f', 'log(G mag)': False, 'M (G-band)': ':.2f'},
                labels={'BP-RP': 'BP - RP (mag)', 'G mag': 'G (mag)'},
                title=f'Colour Magnitude Diagram (N={len(sky_map_sources_df)} sources)'
            )
                        
            
        elif plot_selected == '2D Histogram Contour':
            # 2D Histogram Contour
            
            # Pick a binning number for both x and y
            xbins = st.slider("Number of bins for x axis", 2, 100)
            ybins = st.slider("Number of bins for y axis", 2, 100)
            
            fig = go.Figure(
                go.Histogram2dContour(                    
                    x=cmd_sources_df['BP-RP'],
                    y=cmd_sources_df['G mag'],
                    z=z_col,
                    histfunc=hist_func,
                    nbinsx=xbins,
                    nbinsy=ybins,
                    contours=dict(
                        coloring='heatmap',
                        showlabels=False,                        
                    ),
                    colorbar=dict(
                        title=cb_title, 
                        tickformat='.0f'
                    ),
                    hovertemplate='Colour: %{x:.2f}<br>Magnitude: %{y:.2f}<br>' + hover_temp_stat + ' %{z:.0f}<extra></extra>',                    
                ),                
            )
        fig.update_yaxes(autorange="reversed")
        
        
        st.plotly_chart(fig, width='stretch')
            
    else:
        st.write("To view the Colour Magnitude Diagram, select data file or fetch data to load from Data Source.")
    
with hr_tab:
    st.header("Hertzsprung-Russel Diagram")
    
with distance_tab:
    st.header("Distance (Parallax)")
    
with three_d_xyz_tab:
    st.header("3D XYZ Plot")