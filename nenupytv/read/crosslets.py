#! /usr/bin/python3
# -*- coding: utf-8 -*-


__author__ = 'Alan Loh, Julien Girard'
__copyright__ = 'Copyright 2019, nenupytv'
__credits__ = ['Alan Loh', 'Julien Girard']
__maintainer__ = 'Alan'
__email__ = 'alan.loh@obspm.fr'
__status__ = 'Production'
__all__ = [
    'Crosslets'
    ]


import numpy as np
from os.path import abspath, isfile
from itertools import islice
from astropy.time import Time


# ============================================================= #
# ------------------------ Crosslets -------------------------- #
# ============================================================= #
class Crosslets(object):
    """
    """

    def __init__(self, xst_bin):
        self.meta = {}
        self.data = None
        self.time = None
        self.xst_bin = xst_bin


    # --------------------------------------------------------- #
    # --------------------- Getter/Setter --------------------- #
    @property
    def xst_bin(self):
        """ NenuFAR TV XST snapshot binary file
        """
        return self._xst_bin
    @xst_bin.setter
    def xst_bin(self, x):
        if not isinstance(x, str):
            raise TypeError(
                'String expected.'
                )
        x = abspath(x)
        if not isfile(x):
            raise FileNotFoundError(
                'Unable to find {}'.format(x)
                )
        self._xst_bin = x
        self._load()
    

    # --------------------------------------------------------- #
    # ------------------------ Methods ------------------------ #
    def cross_corr(self, vis=None, polar='xx'):
        """ Given XST visibilities, returns the cross-correlation
            matrix
        """
        if vis is None:
            vis = self.data[0, 0, :] # time, freq, vis

        n_ma = self.meta['ma'].size
        mat_size = n_ma*2
        
        mat_tot = np.zeros(
            (mat_size, mat_size),
            dtype='complex64'
            )
        mat_pol = np.zeros(
            (n_ma, n_ma),
            dtype='complex64'
            )
        
        indices = np.tril_indices(mat_size, 0)
        pol_idx = np.tril_indices(n_ma, 0)
        diag_idx = np.arange(mat_size-1)

        mat_tot[indices] = vis

        # Reconstruct missing XY
        mat_tot[diag_idx, diag_idx+1] = mat_tot[diag_idx+1, diag_idx].conj()

        if polar.lower() == 'xx':
            xx_idx = tuple([
                pol_idx[0]*2,
                pol_idx[1]*2
                ])
            # mat = mat_tot[::2, ::2]
            selected_pol = mat_tot[xx_idx]
        elif polar.lower() == 'xy':
            xy_idx = tuple([
                pol_idx[0]*2,
                pol_idx[1]*2 + 1
                ])
            # mat = mat_tot[::2, 1::2]
            selected_pol = mat_tot[xy_idx]
        elif polar.lower() == 'yx':
            yx_idx = tuple([
                pol_idx[0]*2 + 1,
                pol_idx[1]*2
                ])
            # mat = mat_tot[1::2, ::2]
            selected_pol = mat_tot[yx_idx]
        elif polar.lower() == 'yy':
            yy_idx = tuple([
                pol_idx[0]*2 + 1,
                pol_idx[1]*2 + 1
                ])
            # mat = mat_tot[1::2, 1::2]
            selected_pol = mat_tot[yy_idx]
        else:
            raise ValueError(
                'Polarization not understood.'
                )

        mat_pol[pol_idx] = selected_pol

        return mat_pol


    def gen_cross(self, freq=None, polar='xx'):
        """ Generator of correlation matrices for each time
            at a particular frequency.
        """
        if freq is None:
            freq = self.meta['freq'][0]
        sb_idx = np.argmin(np.abs(freq - self.meta['freq']))
        
        for it in range(self.time.size):
            matrix = self.cross_corr(
                vis=self.data[it, sb_idx, :],
                polar=polar
                )

            yield matrix


    # --------------------------------------------------------- #
    # ----------------------- Internal ------------------------ #
    def _load(self):
        """ Read the binary file
        """
        # Extract the ASCII header (5 first lines)
        with open(self._xst_bin, 'rb') as f:
            header = list(islice(f, 0, 5))
        assert header[0] == b'HeaderStart\n',\
            'Wrong header start'
        assert header[-1] == b'HeaderStop\n',\
            'Wrong header stop'
        header = [s.decode('utf-8') for s in header]
        hd_size = sum([len(s) for s in header])

        # Parse informations into a metadata dictionnary
        keys = ['freq', 'ma', 'accu']
        search = ['Freq.List', 'Mr.List', 'accumulation']
        types = ['float64', 'int', 'int']
        for key, word, typ in zip(keys, search, types):
            for h in header:
                if word in h:
                    self.meta[key] = np.array(
                        h.split('=')[1].split(','),
                        dtype=typ
                        )

        # Deduce the dtype for decoding
        n_ma = self.meta['ma'].size
        n_sb = self.meta['freq'].size
        dtype = np.dtype(
            [('jd', 'float64'),
            ('data', 'complex64', (n_sb, n_ma*n_ma*2 + n_ma))]
            )

        # Decoding the binary file
        tmp = np.memmap(
            filename=self._xst_bin,
            dtype='int8',
            mode='r',
            offset=hd_size
            )
        decoded = tmp.view(dtype)

        self.data = decoded['data'] / self.meta['accu']
        self.time = Time(decoded['jd'], format='jd', precision=0)

        return
# ============================================================= #

