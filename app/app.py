import streamlit as st
from astropy.io import fits
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
            
            file = st.file_uploader("Upload FITS/CSV file", accept_multiple_files=False, )    
            if file:
                sources_df = load_fits(file)
                sources_df.fillna(np.nan)
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
            
            # Add Galactic Coords, Absolute Magnitude and Distance columns to dataframe
            
            sources_df = add_galactic_coords(sources_df)
            sources_df = add_abs_mag(sources_df)
            sources_df = add_distance_pc(sources_df)
            
            # Create new abs_mag_log_column for log-stretch normalization
            sources_df['abs_mag_log'] = np.log10(sources_df['abs_mag'])
            
            # Rename columns for hover data
            sources_df = sources_df.rename(columns={'source_id': 'source id', 'phot_g_mean_mag': 'G mag', 'abs_mag_log': 'log(G mag)', 'bp_rp': 'BP-RP', 
                                                                'distance_pc': 'distance (pc)', 'abs_mag': 'M (G-band)', 'gal_l': 'gal l', 'gal_b': 'gal b'})
            
        else:
            st.write('Load data from Data Source to apply Filtering')

        
        
    
    # st.write("Coordinate Frame")
    # st.write("Download")
    # st.write("Dataset Info")
    # st.write("Help/Legend")




# Tabs for sky map, cmd, hr diagram, 3d xyz plot

data_tab, sky_map_tab, cmd_tab, hr_tab, distance_tab, three_d_xyz_tab = st.tabs(["Data and Summary Statistics", "Sky Map", "CMD", "HR Diagram", "Distance", "3D XYZ"])
    
# Data Tab
with data_tab:
    # Header
    st.header("Data and Summary Statistics")   
    
    
    
    # # Display query information from metadata
    # if data_source == 'File Upload' and source_is_loaded:
    #     st.subheader('ADQL query for the data')
    #     # Open the downloaded FITS file
    #     print(file.upload_url)
    

    if source_is_loaded:
        # Display the data
        st.subheader('Data')
        st.dataframe(sources_df)
        
        st.markdown("## Statistics")        
        
        st.metric('Number of sources:', len(sources_df))
        
        st.markdown('---')
        # Parallax
        st.markdown('#### Parallax (mas)')
        min_parallax_col, max_parallax_col = st.columns(2)
        
        with min_parallax_col:
            st.metric('Minimum', round(sources_df['parallax'].min(), 4))
        
        with max_parallax_col:
            st.metric('Maximum', round(sources_df['parallax'].max(), 4))
        
        st.markdown('---')
        
        # Mean and Median G-band magnitudes
        
        # Apparent magnitude
        st.markdown('#### Apparent Magnitude (G-band)')
        
        # Mean, median, std dev
        mean_app_mag_col, median_app_mag_col, std_dev_app_mag_col = st.columns(3)
        with mean_app_mag_col:
            st.metric("Mean", round(np.mean(sources_df['G mag']), 2))
        with median_app_mag_col:
            st.metric("Median", round(np.median(sources_df['G mag']), 2))
        with std_dev_app_mag_col:
            st.metric("Standard Deviation", round(np.std(sources_df['G mag']), 2))
        
        # Min, max
        min_app_mag_col, max_app_mag_col, blank_col = st.columns(3)
        with min_app_mag_col:
            st.metric("Minimum", round(sources_df['G mag'].min(), 2))
        
        with max_app_mag_col:
            st.metric("Maximum", round(sources_df['G mag'].max(), 2))
        
        st.markdown('---')
        
        # Absolute magnitude
        st.markdown('#### Absolute Magnitude (G-band)')
        mean_abs_mag_col, median_abs_mag_col, std_dev_abs_mag_col = st.columns(3)
        with mean_abs_mag_col:
            st.metric("Mean", round(np.mean(sources_df['M (G-band)']), 2))
        with median_abs_mag_col:
            st.metric("Median", round(np.median(sources_df['M (G-band)']), 2))
        with std_dev_abs_mag_col:
            st.metric("Standard Deviation", round(np.std(sources_df['M (G-band)']), 2))

        # Min, max
        min_abs_mag_col, max_abs_mag_col, blank_col = st.columns(3)
        with min_abs_mag_col:
            st.metric("Minimum", round(sources_df['M (G-band)'].min(), 2))
        
        with max_abs_mag_col:
            st.metric("Maximum", round(sources_df['M (G-band)'].max(), 2))
        
        
        st.markdown('---')
    
    else:
        st.write("To view data and statistics, select data file or fetch data to load from Data Source.")

# Sky Map Tab
with sky_map_tab:        
    
    # Header
    st.header("Sky Map")
    
    # Confirm data is loaded
    if data_source == 'File Upload' and source_is_loaded:
        
        # Copy sources data for tab
        sky_map_sources_df = sources_df.copy()        
        
        
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
            
            st.plotly_chart(fig, width='stretch')
            
            # Add coordinates range
            
            st.markdown(f"__ra range__: {sky_map_sources_df['ra'].min()} &deg;   to   {sky_map_sources_df['ra'].max()} &deg;")
            st.markdown(f"__dec range__: {sky_map_sources_df['dec'].min()} &deg;   to   {sky_map_sources_df['dec'].max()} &deg;")
        
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
            
            # Add coordinaetes range
            st.markdown(f"__l range__: {sky_map_sources_df['gal l'].min()} &deg;   to   {sky_map_sources_df['gal l'].max()} &deg;")
            st.markdown(f"__b range__: {sky_map_sources_df['gal b'].min()} &deg;   to   {sky_map_sources_df['gal b'].max()} &deg;")
        
            
    else:
        st.write("To view the sky plot, select data file or fetch data to load from Data Source.")

# CMD Tab
with cmd_tab:
    st.header("Colour-Magnitude Diagram")    
        
    # Confirm data is loaded
    if data_source == 'File Upload' and source_is_loaded:
                
        # Copy sources data for tab
        cmd_sources_df = sources_df.copy()                                                                
        
        col1, col2 = st.columns(2)
        
        # Add radio buttons for selecting between scatter and histogram 2d contour plot        
        with col1:
            plot_selected = st.radio('Plot Type', ['Scatter', '2D Histogram Contour'], key=0)
            
            
        
        # Select radio buttons displayed in col 2 based on plot type
        with col2:
            #  Scatter plot
            if plot_selected == 'Scatter':
                # Add radio buttons for selecting colour mapping based on parallax, distance, absolute magnitude or none
                
                colour_map_var = st.radio("Variable for Colour Points", ['None', 'Parallax (mas)', 'Distance (pc)', 'G (mag)'], key=1)
                                
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
                
                bin_func = st.radio("Choose Binning Function", ['Count (stellar density)', 'Average (average distance per bin)'], key=2)
                
                # Update histogram function, z column, colour bar title and statistics on hover
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
                title=f'Colour Magnitude Diagram (N={len(cmd_sources_df)} sources)'
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


# HR Diagram Tab
    
with hr_tab:
    st.header("Hertzsprung-Russel Diagram")
    
    # Confirm data is loaded
    if data_source == 'File Upload' and source_is_loaded:
        
        # Copy sources data for tab
        hrd_sources_df = sources_df.copy()
        
        col1, col2 = st.columns(2)
        
        # Add radio buttons for selecting between scatter and 2D histogram contour plot
        with col1:
            plot_selected = st.radio('Plot Type', ['Scatter', '2D Histogram Contour'], key=3)
            

        # Select radio buttons displayed in col2 based on pot type
        with col2:
            # Scatter plot
            if plot_selected == 'Scatter':
                # Add radio buttons for selecting colour mapping based on parallax, distance, absolute magnitude or none
                
                colour_map_var = st.radio("Variable for Colour Points", ['None', 'Parallax (mas)', 'Distance (pc)', 'G (mag)'], key=4)
                
                # Update related arguments based on selection
                if colour_map_var == 'None':
                    range_colour = [0, 0]
                    var_selected = None
                elif colour_map_var == 'Parallax (mas)':
                    range_colour = [hrd_sources_df['parallax'].min(), hrd_sources_df['parallax'].max()]
                    var_selected = 'parallax'
                elif colour_map_var == 'Distance (pc)':
                    range_colour = [hrd_sources_df['distance (pc)'].min(), hrd_sources_df['distance (pc)'].max()]
                    var_selected = 'distance (pc)'
                elif colour_map_var == 'G (mag)':
                    range_colour = [hrd_sources_df['G mag'].min(), hrd_sources_df['G mag'].min()]
                    var_selected = 'G mag'

            #  2D Histogram Contour
            elif plot_selected == '2D Histogram Contour':
                # Add radio buttons for selecting binning function
                
                bin_func = st.radio("Choose Binning Function", ['Count (stellar density)', 'Average (average distance per bin)'], key=5)

                # Update histogram function, z column, colour bar title and statistics on hover
                if bin_func == 'Count (stellar density)':
                    hist_func = 'count'
                    z_col = None
                    cb_title = 'Stars per bin'
                    hover_temp_stat = 'Count'
                elif bin_func == 'Average (average distance per bin)':
                    hist_func = 'avg'
                    z_col = hrd_sources_df['parallax']
                    cb_title = 'Average distance per bin'
                    hover_temp_stat = 'Avg Distance:'
                    
        # Plot CMD
        
        if plot_selected == 'Scatter':
            # Scatter plot
            
            fig = px.scatter(
                hrd_sources_df, 
                x='BP-RP', 
                y='M (G-band)',
                color=var_selected,
                range_color=range_colour,
                hover_data={'source id': True, 'G mag': ':.2f', 'BP-RP': ':.2f', 'parallax': ':.2f', 'distance (pc)': ':.1f', 'log(G mag)': False, 'M (G-band)': ':.2f'},
                labels={'BP-RP': 'BP - RP (mag)', 'M (G-band)': 'Absolute G-band Magnitude (mag)'},
                title=f'Hertzsprung-Russell Diagram (N={len(hrd_sources_df)} sources)'      
            )
        
        elif plot_selected == '2D Histogram Contour':
            # 2D Histogram Contour
            
            # Pick a binning number for both x and y
            xbins = st.slider("Number of x-axis bins", 2, 100)
            ybins = st.slider("Number of y-axis bins", 2, 100)
            
            fig = go.Figure(
                go.Histogram2dContour(
                    x=hrd_sources_df['BP-RP'],
                    y=hrd_sources_df['M (G-band)'],
                    z=z_col,
                    histfunc=hist_func,
                    nbinsx=xbins,
                    nbinsy=ybins,
                    contours=dict(
                        coloring='heatmap',
                        showlabels=False
                    ),
                    colorbar=dict(
                        title=cb_title, 
                        tickformat='.0f'
                    ),
                    hovertemplate='Colour: %{x:.2f}<br>Magnitude: %{y:.2f}<br>' + hover_temp_stat + ' %{z:.0f}<extra></extra>',
                ),
            )
            
            # Add title, x-axis label and y-axis label

            fig.update_layout(title=f'Hertzsprung-Russell Diagram with 2D Histogram Contours (N={len(hrd_sources_df)} sources)',
                              xaxis_title='BP - RP (mag)', yaxis_title='Absolute G-band Magnitude (mag)')
            
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, width="stretch")
        
    else:
        st.write("To view the Hertzsprung-Russell Diagram, select data file or fetch data to load from Data Source.")
        
with distance_tab:
    st.header("Distance (Parallax)")
    
    # Confirm data is loaded
    if data_source == 'File Upload' and source_is_loaded:
        
        # Copy sources data for tab
        distance_sources_df = sources_df.copy()
        
        hist_selection_col, norm_selection_col = st.columns(2)
        
        # Select distance or parallax histogram
        with hist_selection_col:
            hist_displayed = st.radio("Histogram plotted", ['Distance',  'Parallax'])
        
        # Select normalization
        with norm_selection_col:
            norm_selected = st.radio("Normalization", ['None', 'Percent'])
            norm = ['' if norm_selected == 'None' else norm_selected.lower()][0]
            if norm == 'percent':
                yaxis_title = 'Percentage of sources (%)'            
            else:
                yaxis_title='Number of sources'
        # Selecting number of bins
        num_bins = st.slider("Number of bins", 15, 50)
        
        # Histogram
        if hist_displayed == 'Distance':            
            # Distance histogram
            
            fig = px.histogram(
                distance_sources_df,
                x='distance (pc)',
                nbins=num_bins,
                histnorm=norm,
                marginal='box',            
                opacity=0.7,
                barmode='overlay',                
                
            )
        
            fig.update_layout(bargap=0.02, xaxis_title='Distance (pc)', yaxis_title=yaxis_title,
                            title=f"Distance distribution of the sample (N={len(distance_sources_df)})")
            st.plotly_chart(fig, width="stretch")
        
        elif hist_displayed == 'Parallax':
            # Parallax histogram
            
            fig = px.histogram(
                distance_sources_df,
                x='parallax',
                nbins=num_bins,
                histnorm=norm,
                marginal='box',            
                opacity=0.7,
                barmode='overlay',
                
            )
        
            fig.update_layout(bargap=0.02, xaxis_title='Parallax (mas)', yaxis_title=yaxis_title,
                            title=f"Parallax distribution of the sample (N={len(distance_sources_df)})")
            st.plotly_chart(fig, width="stretch")
    
with three_d_xyz_tab:
    st.header("3D XYZ Plot")