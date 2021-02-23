import numpy as np
import math
from scipy.optimize import minimize
from abc import ABC, abstractmethod


class CTBendBase(ABC):
    """Base class from which all ctbend models are to be derived.
    """

    def __init__(self, parameters):
        # type: (dict) -> None

        """Constructor.

        Args:
            parameters: parameters of the bending model.
        """

        self.parameters = parameters

        self.deg2arcsec = 3600.
        self._math = np

    @abstractmethod
    def azimuth_model_terms(self, az_rad, el_rad):
        pass

    @abstractmethod
    def azimuth_derivative_phi(self, az_rad, el_rad):
        pass

    @abstractmethod
    def azimuth_derivative_theta(self, az_rad, el_rad):
        pass

    @abstractmethod
    def elevation_model_terms(self, az_rad, el_rad):
        pass

    @abstractmethod
    def elevation_derivative_phi(self, az_rad, el_rad):
        pass

    @abstractmethod
    def azimuth_derivative_theta(self, az_rad, el_rad):
        pass

    @classmethod
    def modelname(cls):
        return cls.__name__

    def _pointing_correction(self, az, el, altaz):
        # type: (float, float, str) -> float

        """Pointing correction.

        Args:
            az: Requested azimuth in degrees.
            el: Requested elevation in degrees.
            altaz: Requested axis; Either 'azimuth' or 'elevation'.

        Returns:
            Pointing correction for the requested axis in degrees.
        """

        if altaz not in ["azimuth", "elevation"]:
            info ="altaz argument must be either azimuth or"
            info += " elevation"
            raise RuntimeError(info)

        p = self.model_parameters
        az_rad = np.radians(az)
        el_rad = np.radians(el)

        term_function = {}
        term_function["azimuth"] = self.azimuth_model_terms
        term_function["elevation"] = self.elevation_model_terms

        term_dict = term_function[altaz](az_rad, el_rad)
        
        delta = 0.
        for term in term_dict.keys():
            delta += p[term] * term_dict[term]

        return delta

    def delta_azimuth_derivative_phi(self, az, el):

        p = self.model_parameters
        az_rad = np.radians(az)
        el_rad = np.radians(el)

        term_dict = self.azimuth_derivative_phi(az_rad, el_rad)
        delta = 0.
        for term in term_dict.keys():
            delta += p[term] * term_dict[term]

        return np.radians(delta)

    def delta_elevation_derivative_phi(self, az, el):

        p = self.model_parameters
        az_rad = np.radians(az)
        el_rad = np.radians(el)

        term_dict = self.elevation_derivative_phi(az_rad, el_rad)
        delta = 0.
        for term in term_dict.keys():
            delta += p[term] * term_dict[term]

        return np.radians(delta)

    def delta_azimuth_derivative_theta(self, az, el):

        p = self.model_parameters
        az_rad = np.radians(az)
        el_rad = np.radians(el)

        term_dict = self.azimuth_derivative_theta(az_rad, el_rad)
        delta = 0.
        for term in term_dict.keys():
            delta += p[term] * term_dict[term]

        return np.radians(delta)

    def delta_elevation_derivative_theta(self, az, el):

        p = self.model_parameters
        az_rad = np.radians(az)
        el_rad = np.radians(el)

        term_dict = self.elevation_derivative_theta(az_rad, el_rad)
        delta = 0.
        for term in term_dict.keys():
            delta += p[term] * term_dict[term]

        return np.radians(delta)

    def delta_azimuth(self, az, el):
        # type: (float, float) -> float

        """Pointing correction in azimuth.

        Args:
            az: Requested azimuth in degrees.
            el: Requested elevation in degrees.

        Returns:
            Pointing correction in azimuth in degrees.
        """

        return self._pointing_correction(az, el, altaz="azimuth")

    def delta_elevation(self, az, el):
        # type: (float, float) -> float

        """Pointing correction in elevation.

        Args:
            az: Requested azimuth in degrees.
            el: Requested elevation in degrees.

        Returns:
            Pointing correction in elevation in degrees.
        """

        return self._pointing_correction(az, el, altaz="elevation")

    @property
    def model_parameter_names(self):

        name_list = list(self.azimuth_model_terms(0, 0).keys())
        name_list += list(self.elevation_model_terms(0, 0).keys())

        return np.unique(name_list)

    @property
    def model_parameters(self):

        try:
            mean = self.parameters["model"]["mean"]
        except KeyError:
            mean = self.parameters["mean"]
        return mean
        """
        parameter_dict = {}
        for parameter in self.model_parameter_names:
            parameter_dict[parameter] = self.parameters["priors"][parameter]

        return parameter_dict
        """
    def invert_bending_model(self, azimuth, elevation, verbose=False):

        uncorrected_azimuth = []
        uncorrected_elevation = []
        tolerance = 1.e-8

        def _telescope_pointing_inverter_loss_function(x, az, el):
            az0 = x[0]
            el0 = x[1]
            a = np.abs(az - az0 - self.delta_azimuth(az0, el0))
            b = np.abs(el - el0 - self.delta_elevation(az0, el0))
    
            loss = a + b

            return loss


        for az, el in zip(azimuth, elevation):
            range_error = False
            x0 = (az, el)
            res = minimize(_telescope_pointing_inverter_loss_function,
                           x0, args=(az, el), method="nelder-mead",
                           options={"xtol": tolerance, "disp": verbose})

            if range_error or res.success is False:
                res = minimize(self._telescope_pointing_inverter_loss_function,
                               x0, args=(az, el), method="L-BFGS-B",
                               options={"disp": verbose})

            uncorrected_azimuth.append(res.x[0])
            uncorrected_elevation.append(res.x[1])

        return np.array(uncorrected_azimuth), np.array(uncorrected_elevation)