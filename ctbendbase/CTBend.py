from ctbend.ctbendbase.CTBendBase import CTBendBase
import sys

"""
class ConstantOffsetModel(CTBendBase):

    def __init__(self, parameters):

        self.azimuth_parameter_name = "DeltaAzimuth"
        self.elevation_parameter_name = "DeltaElevation"

        azimuth_offset_deg = parameters["azimuth_offset_deg"]
        elevation_offset_deg = parameters["elevation_offset_deg"]

        parameters = {"model": {}}
        az_name = self.azimuth_parameter_name
        el_name = self.elevation_parameter_name
        parameters["model"]["mean"] = {az_name: azimuth_offset_deg,
                                       el_name: elevation_offset_deg}

        super().__init__(parameters)
        self.name = self.modelname()

    def azimuth_model_terms(self, az_rad, el_rad):

        terms = {self.azimuth_parameter_name: 1.}

        return terms

    def elevation_model_terms(self, az_rad, el_rad):

        terms = {self.elevation_parameter_name: 1.}

        return terms
"""

class CTBendBasic4(CTBendBase):

    def __init__(self, parameters={}):
        super().__init__(parameters)
        self.name = self.modelname()

    def azimuth_model_terms(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IA": -1.,
                 "AW": -cos(az_rad) * tan(el_rad),
                 "AN": -sin(az_rad) * tan(el_rad),
                 }

        return terms

    def azimuth_derivative_phi(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IA": 0.,
                 "AW": sin(az_rad) * tan(el_rad),
                 "AN": -cos(az_rad) * tan(el_rad),
                 }

        return terms
    def azimuth_derivative_theta(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IA": 0.,
                 "AW": -cos(az_rad) / (cos(el_rad) * cos(el_rad)),
                 "AN": -sin(az_rad) / (cos(el_rad) * cos(el_rad)),
                 }

        return terms
    def elevation_model_terms(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin

        terms = {"IE": 1.,
                 "AW":-sin(az_rad),
                 "AN": -cos(az_rad),
                 }

        return terms

    def elevation_derivative_phi(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IE": 0.,
                 "AW": -cos(az_rad),
                 "AN": sin(az_rad),
                 }

        return terms

    def elevation_derivative_theta(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IE": 0.,
                 "AW": 0.,
                 "AN": 0.,
                 }

        return terms


class CTBendBasic8(CTBendBase):

    def __init__(self, parameters={}):
        super().__init__(parameters)
        self.name = self.modelname()

    def azimuth_model_terms(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IA": -1.,
                 "NPAE": -tan(el_rad),
                 "AW": -cos(az_rad) * tan(el_rad),
                 "AN": -sin(az_rad) * tan(el_rad),
                 "ACES": sin(az_rad),
                 "ACEC": cos(az_rad)
                 }

        return terms

    def azimuth_derivative_phi(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IA": 0.,
                 "NPAE": 0.,
                 "AW": sin(az_rad) * tan(el_rad),
                 "AN": -cos(az_rad) * tan(el_rad),
                 "ACES": cos(az_rad),
                 "ACEC": -sin(az_rad)
                 }

        return terms

    def azimuth_derivative_theta(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IA": 0.,
                 "NPAE": -1. / (cos(el_rad) * cos(el_rad)),
                 "AW": -cos(az_rad) / (cos(el_rad) * cos(el_rad)),
                 "AN": -sin(az_rad) / (cos(el_rad) * cos(el_rad)),
                 "ACES": 0.,
                 "ACEC": 0.
                 }

        return terms

    def elevation_model_terms(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin

        terms = {"IE": 1.,
                 "AW":-sin(az_rad),
                 "AN": -cos(az_rad),
                 "TF": cos(el_rad)
                 }

        return terms

    def elevation_derivative_phi(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IE": 0.,
                 "AW": -cos(az_rad),
                 "AN": sin(az_rad),
                 "TF": 0.
                 }

        return terms

    def elevation_derivative_theta(self, az_rad, el_rad):

        cos = self._math.cos
        sin = self._math.sin
        tan = self._math.tan

        terms = {"IE": 0.,
                 "AW": 0.,
                 "AN": 0.,
                 "TF": -sin(el_rad)
                 }

        return terms


def bending_factory(model_json):

    requested_model = model_json["name"]
    return getattr(sys.modules[__name__],
                   requested_model)(parameters=model_json)

if __name__ == "__main__":

    import numpy as np
    model_list = ["CTBendBasic4", "CTBendBasic8", ]

    for model in model_list:
        print(model)
        testmodel = globals()[model](parameters={})
        print("-h")
        parameter_list = testmodel.model_parameter_names
        parameters = {"model": {"mean": {}}}

        for parameter in parameter_list:
            parameters["model"]["mean"][parameter] = np.random.uniform(-3, 3)

        testmodel = globals()[model](parameters) 
    print("-------------------------------------------------")
    print("-------------------------------------------------")
