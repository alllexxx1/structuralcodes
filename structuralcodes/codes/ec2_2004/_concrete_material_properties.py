"""Concrete material properties according to Tab. 3.1."""

import math

from structuralcodes.codes import mc2010


def fcm(fck: float, delta_f: float = 8) -> float:
    """The mean compressive strength of concrete.

    EN 1992-1-1:2004, Table 3.1.

    Args:
        fck (float): The caracteristic compressive strength of concrete.
    """
    return mc2010.fcm(fck=fck, delta_f=delta_f)


def fctm(fck: float) -> float:
    """The mean tensile strength of concrete.

    EN 1992-1-1: 2004, Table 3.1.

    Args:
        fck (float): The caracteristic compressive strength of concrete.
    """
    return mc2010.fctm(fck=fck)


def fctk_5(_fctm: float) -> float:
    """The 5% fractile of the tensile strength of concrete.

    EN 1992-1-1: 2004, Table 3.1.

    Args:
        _fctm (float): The mean tensile strength of concrete.
    """
    return mc2010.fctkmin(_fctm=_fctm)


def fctk_95(_fctm: float) -> float:
    """The 95% fractile of the tensile strength of concrete.

    EN 1992-1-1: 2004, Table 3.1.

    Args:
        _fctm (float): The mean tensile strength of concrete.
    """
    return mc2010.fctkmax(_fctm=_fctm)


def Ecm(_fcm: float) -> float:
    """The secant modulus of concrete.

    EN 1992-1-1:2004, Table 3.1.

    Args:
        _fcm (float): The mean compressive strength of concrete.
    """
    return 22000.0 * math.pow(_fcm / 10, 0.3)


def eps_c1(_fcm: float) -> float:
    """The strain at maximum compressive stress of concrete (fcm) for the
    Sargin constitutive law.

    EN 1992-1-1:2004, Table 3.1.

    Args:
        _fcm (float): The mean compressive strength of concrete.
    """
    return min(0.7 * math.pow(_fcm, 0.31), 2.8) / 1000
