#! /usr/bin/python3
# -*- coding: utf-8 -*-


__author__ = 'Alan Loh, Julien Girard'
__copyright__ = 'Copyright 2019, nenupytv'
__credits__ = ['Alan Loh', 'Julien Girard']
__maintainer__ = 'Alan'
__email__ = 'alan.loh@obspm.fr'
__status__ = 'Production'
__all__ = [
    'NenuFAR'
    ]


from astropy import units as u
from astropy.coordinates import EarthLocation 
from itertools import permutations
import numpy as np

from nenupytv.instru import ma_names, ma_positions, ma_indices


# ============================================================= #
# ------------------------ Crosslets -------------------------- #
# ============================================================= #
class NenuFAR(object):
    """ NenuFAR array object
    """

    def __init__(self):
        self.lon = 47.375944 * u.deg
        self.lat = 2.193361 * u.deg
        self.height = 136.195 * u.m

        self.ma = ma_indices
        self.pos = ma_positions


    # --------------------------------------------------------- #
    # --------------------- Getter/Setter --------------------- #
    @property
    def coord(self):
        """ Coordinate object of NenuFAR

            Returns
            -------
            coord : `astropy.coordinates.EarthLocation`
                Coordinates of the whole NenuFAR array
        """
        return EarthLocation(
            lat=self.lat,
            lon=self.lon,
            height=self.height
            )


    @property
    def baselines(self):
        """ Baselines computed for all active Mini-Arrays of 
            NenuFAR.

            Returns
            -------
            baselines : `np.ndarray`
                Array of baseline (length-2 tuples of antennae)
        """
        bsl = list(permutations(self.ma, 2))
        # Add auto-correlations
        for m in self.ma:
            bsl.append((m, m))
        return np.array(bsl)
    
    

    # --------------------------------------------------------- #
    # ------------------------ Methods ------------------------ #

    # --------------------------------------------------------- #
    # ----------------------- Internal ------------------------ #

# ============================================================= #