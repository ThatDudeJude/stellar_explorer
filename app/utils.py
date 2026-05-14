# Reusable functions for the Stellar Coordinate Explorer dashboard

from astropy.table import Table
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.stats import pearsonr, spearmanr
import numpy as np


def load_fits(file_path_or_buffer_data):
    """
    Loads a FITS or CSV file into a pandas DataFrame.
    
    Parameters
    ----------
    file_path_or_buffer_data: str or file-like object
        Path to a FITS/CSV file or an uploaded file object.
        
    Returns
    -------
    pandas.DataFrame
        DataFrame containing the catalog data.
    """
    # Try reading a FITS first, fallback to CSV
    try:
        table = Table.read(file_path_or_buffer_data, format='fits')
    except (OSError, TypeError, ValueError):
        # if FITS fails, assume CSV
        table = Table.read(file_path_or_buffer_data, format='csv')
    df = table.to_pandas()
    return df

def add_galactic_coords(df, ra_col='ra', dec_col='dec'):
    """
    Add Galactic coordinates (l, b) columns to the DataFrame.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Must contain columns 'ra_col' and 'dec_col' in degrees.
    ra_col : str, optional
        Name of the Right Ascension column.
    dec_col: str, optional
        Name of the Declination column.
    
    Returns        
    -------
    pandas.DataFrame
        Original DataFrame with new columns 'gal_l' and 'gal_b' (degrees).
    """
    coords = SkyCoord(ra=df[ra_col].values * u.deg, dec=df[dec_col].values * u.deg, frame='icrs')
    galactic = coords.galactic
    df['gal_l'] = galactic.l.deg
    df['gal_b'] = galactic.b.deg
    return df

def add_abs_mag(df, mag_col='phot_g_mean_mag', parallax_col='parallax'):
    """
    Add absolute G magnitude column using the distance modulus
    
    M = m + 5 * log10(parallax) - 10, where parallax is in mas.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Must contain `mag_col` and `parallax_col` (mas).
    mag_col : str
        Apparent magnitude column name.
    parallax_col: str
        Parallax column name (milliarcseconds).
        
    Returns
    -------
    pandas.DataFrame
        DataFrame with new column `abs_mag`.
    """
    df['abs_mag'] = df[mag_col] + 5 * np.log10(df[parallax_col]) - 10
    return df
    
    
def add_distance_pc(df, parallax_col='parallax'):
    """
    Add distance in parsecs (yielded by 1 / parallax)
    
    d = 1000 / parallax (in mas)
    
    Parameters
    ----------
    df: pandas.DataFrame
        Must contain `parallax_col` (mas).
        
    parallax_col: str
        Parallax column name.
        
    
    Returns
    -------
    pandas.DataFrame
        DataFrame with new column `distance_pc`.
    """
    df['distance_pc'] = 1000.0 / df[parallax_col]
    return df


def add_xyz_galactic(df, l_col='gal_l', b_col='gal_b', distance_col='distance_pc'):
    """
    Convert Galactic coordinates (l, b, distance) to Cartesian X, Y, Z.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Must contain l_col (deg), b_col (deg), distance_col (pc).
        
    l_col: str
        Galactic longitude column name.
    b_col: str
        Galactic latitude column name.
    distance_col: str
        Distance in parsecs.

    Returns
    -------
    pandas.DataFrame    
        DataFrame with new columns 'X', 'Y', 'Z' (pc).
    """
    l_rad = np.radians(df[l_col])
    b_rad = np.radians(df[b_col])
    d = df[distance_col]
    
    df['X'] = d * np.cos(b_rad) * np.cos(l_rad)
    df['Y'] = d * np.cos(b_rad) * np.sin(l_rad)
    df['Z'] = d * np.sin(b_rad)
    return df

def interpret_magnitude_distance_correlation(df, mag_col='G mag', parallax_col='parallax (mas)', distance_col = None):
    """
    Compute correlation between magnitude and distance (or parallax) dynamically.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Must contain `mag_col` and `parallax_col`. If `distance_col` is given, use that; otherwise compute distance = 1000 / parallax.
    mag_col: str
        Apparent magnitude column name.
    parallax_col: str
        Parallax column name (mas).
    distance_col: str, optional
        Pre-computed distance column (pc). If None, compute from parallax.
        
    Returns
    -------
    str
        Interpretation sentence.
    dict
        Dictionary with keys: 'pearson_r', 'pearson_p', 'spearman_r', spearman_p'
        for the chosen distance/parallax variable
    """
    # Prepare data
    
    data = df[[mag_col, parallax_col]].dropna()
    if len(data) == 0:
        return "Insufficient data for correlation analysis.", {}
    
    magnitude = data[mag_col]
    parallax = data[parallax_col]
    
    # Use pre-computed distance or compute from parallax
    if distance_col is not None and distance_col in df.columns:
        distance = df.loc[data.index, distance_col].values
        var_name = 'distance (pc)'
    else:
        # Avoid division by zero or negative parallax
        parallax_safe = np.where(parallax <=0, np.nan, parallax)
        distance = 1000.0/parallax_safe
        var_name = 'distance (pc)'
        
        # Remove any NaN from invalid parallax
        mask = ~np.isnan(distance)
        magnitude = magnitude[mask]
        distance = distance[mask]
        
        if len(magnitude) == 0:
            return "No valid distances (parallax must be >0).", {}

    # Compute correlation
    pearson_r, pearson_p = pearsonr(magnitude, distance)
    spearman_r, spearman_p = spearmanr(magnitude, distance)
    
    results = {
        'variable': var_name,
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
        'spearman_p': spearman_p
    }
    
    # Helper functions
    def strength(r_abs):
        if r_abs < 0.2:
            return "very weak"
        elif r_abs < 0.4:
            return "weak"
        elif r_abs < 0.6:
            return "moderate"
        elif r_abs < 0.8:
            return "strong"
        else:
            return "very strong"
    
    def is_significant(p):
        return p < 0.05
    
    def direction(r):
        if r > 0:
            return "positive (brighter stars tend to be closer)"
        elif r < 0:
            return "negative (brighter stars tend to be farther)"
        else:
            return "no directional trend"
    
    pearson_sig = is_significant(pearson_p)
    spearman_sig = is_significant(spearman_p)
    pearson_strength = strength(abs(pearson_r))
    spearman_strength = strength(abs(spearman_r))
    
    sentence = f"Correlation between apparent magnitude and {var_name}: "
    sentence += f"Pearson r = {pearson_r:.2f} (p = {pearson_p:.2e}) indicates a {pearson_strength} {direction(pearson_r)}. "
    sentence += f"Spearman r = {spearman_r:.2f} (p = {spearman_p:.2e}) indicates a {spearman_strength} monotonic relationship. "
    
    if abs(pearson_r - spearman_r) < 0.1:
        sentence += "The two coefficients agree, suggesting a roughly linear monotonic trend. "
    elif abs(spearman_r) > abs(pearson_r) + 0.1:
        sentence += "The stronger Spearman correlation suggests a monotonic relationship that may not be perfectly linear. "
    elif abs(pearson_r) > abs(spearman_r) + 0.1:
        sentence += "The stronger Pearson correlation suggests a linear relationship with some monotonic deviations. "
        
    if not (pearson_sig or spearman_sig):
        sentence += "Neither correlaion is statistically significant: the null hypothesis (no relationship) cannot be rejected."
        
    elif pearson_sig and not spearman_sig:
        sentence += "Only the Pearson correlation is significant, indicating a linear trend despite a non-monotonic scatter."
    elif not pearson_sig and spearman_sig:
        sentence += "Only the Spearman correlation is significant, pointing to a monotonic trend but non-linear relationship."
    else:
        sentence += "Both correlations are statistically significant, confirming a reliable relationship."
    
    return sentence, results