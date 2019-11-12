#! /usr/bin/python3
# -*- coding: utf-8 -*-


__author__ = 'Alan Loh, Julien Girard'
__copyright__ = 'Copyright 2019, nenupytv'
__credits__ = ['Alan Loh', 'Julien Girard']
__maintainer__ = 'Alan'
__email__ = 'alan.loh@obspm.fr'
__status__ = 'Production'
__all__ = [
    'lst',
    'lha',
    'eq_zenith',
    'to_radec',
    'rotz',
    'wavelength'
    ]


import numpy as np
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import EarthLocation, Angle, SkyCoord
from astropy.constants import c as lspeed


# ============================================================= #
# ---------------------------- lst ---------------------------- #
# ============================================================= #
def lst(time, location):
    """ Local sidereal time

        Parameters
        ----------
        time : `astropy.time.Time`
            UTC time
        location : `astropy.coord.EarthLocation`
            Location of the instrument

        Returns
        -------
        lst : float
            Local sidereal time in degrees
    """
    if not isinstance(time, Time):
        raise TypeError(
            'time is not an astropy Time.'
            )
    if not isinstance(location, EarthLocation):
        raise TypeError(
            'time is not an astropy EarthLocation.'
            )
    lon = location.to_geodetic().lon
    lst = time.sidereal_time('apparent', lon)
    return lst.deg#.hourangle
# ============================================================= #


# ============================================================= #
# ---------------------------- lha ---------------------------- #
# ============================================================= #
def lha(time, location, ra):
    """ Local hour angle of an object in the observer's sky

        Parameters
        ----------
        time : `astropy.time.Time`
            UTC time
        location : `astropy.coord.EarthLocation`
            Location of the instrument
        ra : float
            Right Ascension in degrees

        Returns
        -------
        lha : float
            Local hour angle in degrees
    """
    ra = Angle(ra * u.deg).deg#.hourangle
    ha = lst(time, location) - ra
    if ha < 0:
        ha += 360.
    elif ha > 360:
        ha -= 360.
    return ha
# ============================================================= #


# ============================================================= #
# ------------------------- eq_zenith ------------------------- #
# ============================================================= #
def eq_zenith(time, location):
    """ Get the ra dec coordinates of the zenith
        
        Parameters
        ----------
        time : `astropy.time.Time`
            UTC time
        location : `astropy.coord.EarthLocation`
            Location of the instrument

        Returns
        -------
        ra : float
            Right Ascension in degrees
        dec : float
            Declination in degrees
    """
    zen_alt = 90*u.deg
    zen_az = 0*u.deg
    azel = SkyCoord(
        alt=zen_alt,
        az=zen_az,
        obstime=time,
        location=location,
        frame='altaz'
        )
    eq = azel.icrs
    return eq.ra.deg, eq.dec.deg
# ============================================================= #


# ============================================================= #
# ------------------------- eq_zenith ------------------------- #
# ============================================================= #
def to_radec(alt, az, time, location):
    """ Get the ra dec coordinates of the a altaz pointing
        
        Parameters
        ----------
        alt : float
            Elevation in degrees
        az : float
            Azimuth in degrees
        time : `astropy.time.Time`
            UTC time
        location : `astropy.coord.EarthLocation`
            Location of the instrument

        Returns
        -------
        ra : float
            Right Ascension in degrees
        dec : float
            Declination in degrees
    """
    zen_alt = alt*u.deg
    zen_az = az*u.deg
    azel = SkyCoord(
        alt=zen_alt,
        az=zen_az,
        obstime=time,
        location=location,
        frame='altaz'
        )
    eq = azel.icrs
    return eq.ra.deg, eq.dec.deg
# ============================================================= #


# ============================================================= #
# --------------------------- rotz ---------------------------- #
# ============================================================= #
def rotz(array, angle):
    """ Rotate the 3D array by an angle along z-axis
    """
    ang = np.radians(angle)
    cosa = np.cos(ang)
    sina = np.sin(ang)
    rot = np.array([
            [cosa, -sina, 0],
            [sina,  cosa, 0],
            [   0,     0, 1]
        ])
    return np.dot(array, rot)
# ============================================================= #


# ============================================================= #
# ------------------------ wavelength ------------------------- #
# ============================================================= #
def wavelength(freq):
    """ Convert between MHz and wavelength in meters

        Returns
        -------
        wavelength : `np.ndarray`
            Wavelength in meters
    """
    if not hasattr(freq, '__len__'):
        freq = [freq]
    if not isinstance(freq, np.ndarray):
        freq = np.array(freq)
    freq *= u.MHz
    freq = freq.to(u.Hz)
    wavel = lspeed.value / freq.value
    return wavel
# ============================================================= #


