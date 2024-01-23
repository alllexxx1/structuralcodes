"""Integration of area moments using algorithms by Joaquin Marin.

Marin, J.: Computing columns, footings and gates through moments of area.
Computers and Structures, 18(2), pp. 343-349, 1984.
"""
import functools
import math


@functools.lru_cache
def _coeff(m, n, j, k):
    """Calculate the binomial coefficient used in Marin integration."""
    return math.comb(j + k, j) * math.comb(m + n - j - k, n - k)


def marin_integration(y: list[float], z: list[float], m: int, n: int) -> float:
    """Marin's algorithm for integrating a polynomial over a closed polygon.

    The order of the polygon vertices is significant. If the points are in
    counterclockwise order the integral is positive, otherwise the integral
    is negative.

    Arguments:
        y, z (lists of floats): Coordinates of polygon vertices.
        m (int): The degree of the polynomial in the y direction.
        n (int): The degree of the polynomial in the z direction.
    """
    mom = 0
    for i in range(len(y) - 1):
        # Sum over j
        ssj = 0
        for j in range(m + 1):
            # Sum over k
            ssk = 0
            for k in range(n + 1):
                ssk += _coeff(m, n, j, k) * z[i] ** (n - k) * z[i + 1] ** k
            ssj += ssk * y[i] ** (m - j) * y[i + 1] ** j
        mom += ssj * (y[i] * z[i + 1] - y[i + 1] * z[i])
    return mom / (math.comb(m + n, n) * (m + n + 1) * (m + n + 2))
