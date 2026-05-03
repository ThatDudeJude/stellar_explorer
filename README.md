# Stellar Coordinate Explorer
A Python-based astronomy data analysis project exploring stellar coordinate systems, Gaia DR3 catalog data, and scientific visualization using Astropy.

---

## Project Overview
Astronomical datasets are recorded in multiple coordinate systems (e.g., ICRS, Galactic) and transforming between them is essential for understanding spatial structure and physical properties of stars.

This project uses real Gaia DR3 data to:
- Transform stellar coordinates between reference frames using Astropy
- Explore stellar distributions using statistical distribution
- Construct colour-magnitude and Hertzsprung-Russell diagrams
- Investigate observational selection effects in nearby stellar samples

---

## Main Objective
Build an interactive astronomy data-analysis and visualization tool for exploring the spatial distribution and photometric properties of nearby Gaia DR3 stellar sources.

## Specific Objectives
- Load and process real Gaia DR3 catalog data using Astropy
- Transform stellar coordinates between ICRS and Galactic frames
- Generate meaningful visualizations of source positions using astronomical sky maps 
- Explore stellar population using photometric properties and statistical visualizations
- Build a structured, reproducible astronomy data analysis workflow
- Build an interactive Streamlit dashboard for stellar exploration

---

## Data Source

Data is obtained from the Gaia Archive DR3 sources selected with the following query syntax:
- Apparent G-band magnitude:
  - `phot_g_mean_mag < 10` (mainly moderately bright and faint sources)
- Parallax
  - `parallax > 5` (nearby sources, ~ within $200\ pc$)
- Sample size: `SELECT TOP 10000` ($10,000$ stellar sources)

This approximately limits the sample to sources within $\approx 200$ parsecs of Earth.

---

## Sample Characteristics

The dataset is dominated by nearby main-sequence stars in the solar neighbourhood. Analysis of the colour index and absolute magnitude distributions suggests the sample
primarily contains:
- Late F-type stars
- G-type stars
- Early K-type dwarf stars

The selection criteria also introduces important observational biases:
- Very faint stars are underrepresented due to the magnitude limit
- Distant Galactic plane structure is less visible because the sample probes mostly nearby stars

## Tools and Technologies
- Python
- Astropy
- Numpy
- Matplotlib
- Jupyter Notebook
- Streamlit (planned)

---

## Visualizations and Analysis

Current visualizations include:

- ICRS sky-position scatter plots
- Colour-coded stellar maps
- Hexbin density visualizations
- Full-sky Aitoff projections
- Apparent magnitude distributions
- Absolute magnitude distributions
- Parallax histograms
- BP-RP colour index distributions
- Hertzsprung-Russell diagrams
- Colour-magnitude diagrams using absolute magnitude

---

### Key Findings
- The sky distribution of nearby stars appears approximately isotropic, with no strong concentration along the Galactic plane.
- The sample is dominated by nearby solar-neighbourhood stars and is limited by magnitude selection.
- The colour index distribution peaks around BP-RP $\approx 0.6-1.0$, consistent with moderately cool dwarf and sun-like stars.
- The absolute magnitude distribution peaks around $M_{G}\approx 3-5$, broadly matching late F-, G-, and early K-type main-sequence stars.
- Bayesian Blocks adaptive histograms reveal changes in local data density more effectively than fixed-width histograms.

### Featured Visualizations
The following figures highlight the spatial distribution and photometric properties of the Gaia DR3 sample.
- Full-sky Aitoff projections (ICRS and Galactic)
![Full-sky Aitoff Projection](./outputs/aitoff_projection_icrs_galactic_coord.png)
- BP-RP colour index distributions
![BP-RP colour index distribution](./outputs/bp-rp_distribution.png)
- Absolute magnitude distributions
![Absolute magnitude distributions](./outputs/abs_mag_distribution.png)
- Hertzsprung-Russell diagrams
![Hertzsprung-Russell diagrams](./outputs/hertzsprung-russel_diagrams.png)

---

## Next Steps and Planned Features
- Hypothesis testing (brightness vs distance)
- Interactive dashboard using Streamlit
- Coordinate-system toggle (ICRS &rarr; Galactic)
- Interactive magnitude filtering
- Plotly-based interactive sky maps
- Exportable plots and analysis summaries

---

## Project structure

```text
stellar_explorer
 |
 |------ app/
 |       |---- app.py
 |       |---- utils.py
 |------ data/
 |       |---- bright_stars_filtered_biased.fits 
 |       |---- bright_stars_filtered_random.fits 
 |       |---- gaia_subset_biased.fits
 |       |---- gaia_subset_random.fits
 |       |---- stars_with_galactic_coord_biased.fits
 |       |---- stars_with_galactic_coord_random.fits      
 |------ notebooks/
 |       |---- learning/
 |       |     |---- 01_quantities.ipynb
 |       |     |---- 02_coordinates.ipynb
 |       |     |---- 03_load_and_inspect_biased.ipynb
 |       |     |---- 04_coord_transform_biased.ipynb
 |       |     |---- 05_viz_biased.ipynb
 |       |     |---- 06_load_and_inspect_random.ipynb
 |       |     |---- 07_coord_transform_random.ipynb
 |       |     |---- 08_viz_random.ipynb
 |       |     |---- 09_colour_magnitude_random.ipynb
 |       |     |---- 10_aitoff_sky_map.ipynb
 |       |     |---- 11_histograms_cmds_HR.ipynb
 |       |---- stellar_coordinate_explorer.ipynb
 |------ outputs/
 |       |---- images 
 |------ README.md
 ```