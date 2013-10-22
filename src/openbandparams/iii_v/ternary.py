#
#   Copyright (c) 2013, Scott J Maddox
#
#   This file is part of OpenBandParams.
#
#   OpenBandParams is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   PhotonAcq is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with PhotonAcq.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

# std lib imports
import logging; log = logging.getLogger(__name__)

# third party imports

# local imports
from openbandparams.base_material import AlloyBase

class Ternary(AlloyBase):
    _bowing_Eg_Gamma = 0
    _bowing_Eg_X = 0
    _bowing_Eg_L = 0
    _bowing_Delta_SO = 0
    _bowing_meff_e_Gamma = 0
    _bowing_meff_HH_DOS = 0
    _bowing_meff_LH_DOS = 0
    _bowing_Ep = 0
    _bowing_F = 0
    _bowing_VBO = 0
    _bowing_a_c = 0
    def __init__(self, x=None, **kwargs):
        AlloyBase.__init__(self)
        if x is not None:
            self._x = float(x)
        elif self.element1 in kwargs:
            self._x = float(kwargs[self.element1])
        elif self.element2 in kwargs:
            self._x = (1 - float(kwargs[self.element2]))
        self._init() # initialize any values that depend on self._x
    
    def _init(self):
        '''
        Initializes any values that depend on `self._x`, the alloy fraction.
        
        Should be overidden when calling `create_ternary`, e.g.
        
            def AlGaAs_init(self):
                """Defines AlGaAs params that depend on self._x"""
                self._new_param = self._x * 3
            create_ternary('AlGaAs', 'Al', AlAs, 'Ga', GaAs,
                           { '_init' : AlGaAs_init })
        '''
        pass
    def _interpolate(self, param, T=None):
        vals = []
        for b in [self.binary1, self.binary2]:
            try:
                vals.append(getattr(b, param))
            except AttributeError as e:
                e.message +='. Binary `%s`'%b.name
                e.message +=' missing param `%s`'%param
                raise e
        x = self._x
        if T is None:
            A = vals[0]
            B = vals[1]
        else:
            A = vals[0](T)
            B = vals[1](T)
        if hasattr(self, '_bowing_%s'%param):
            C = getattr(self, '_bowing_%s'%param)
            return A*x + B*(1-x) - C*x*(1-x)
        else:
            return A*x + B*(1-x)
    
    def a(self, T=300):
        '''
        Returns the lattice parameter, a, in Angstroms at a given
        temperature, T, in Kelvin (default: 300 K)
        '''
        return self._interpolate('a', T)
    def Eg_Gamma(self, T=300):
        '''
        Returns the Gamma-valley bandgap, Eg_Gamma, in electron Volts at a given
        temperature, T, in Kelvin (default: 300 K)
        '''
        return self._interpolate('Eg_Gamma', T)
    def Eg_X(self, T=300):
        '''
        Returns the X-valley bandgap, Eg_X, in electron Volts at a given
        temperature, T, in Kelvin (default: 300 K)
        '''
        return self._interpolate('Eg_X', T)
    def Eg_L(self, T=300):
        '''
        Returns the L-valley bandgap, Eg_L, in electron Volts at a given
        temperature, T, in Kelvin (default: 300 K)
        '''
        return self._interpolate('Eg_L', T)
    def Eg(self, T=300):
        '''
        Returns the bandgap, Eg, in electron Volts at a given
        temperature, T, in Kelvin (default: 300 K)
        '''
        return min(self.Eg_Gamma(T), self.Eg_X(T), self.Eg_L(T))

class ReversedTernary(Ternary):
    def __init__(self, x=None, **kwargs):
        Ternary.__init__(self, x, **kwargs)
        self.reversed_ternary_inst = self.reversed_ternary(1 - self._x)

def create_ternary(name, element1, binary1, element2, binary2, params):
    new_type= type(name, (Ternary,), params)
    new_type.name = name
    new_type.element1 = element1
    new_type.binary1 = binary1
    new_type.element2 = element2
    new_type.binary2 = binary2
    return new_type

def create_reversed_ternary(name, reversed_ternary):
    new_type= type(name, (Ternary,), {})
    new_type.name = name
    new_type.reversed_ternary = reversed_ternary
    new_type.element1 = reversed_ternary.element2
    new_type.binary1 = reversed_ternary.binary2
    new_type.element2 = reversed_ternary.element1
    new_type.binary2 = reversed_ternary.binary1
    return new_type