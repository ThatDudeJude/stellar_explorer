# Reusable functions for the Stellar Coordinate Explorer dashboard

from astropy.table import Table
from astropy.coordinates import SkyCoord
import astropy.units as u
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

