"""Classes for integrating the response of sections."""
import abc
import typing as t

import numpy as np
from numpy.typing import ArrayLike

from math import atan2, cos, sin

from shapely.geometry.polygon import orient
from shapely import MultiLineString, Polygon, MultiPolygon

from ._generic import CompoundGeometry
from ._geometry import create_line_point_angle
from ._marin_integration import marin_integration


class SectionIntegrator(abc.ABC):
    """Abstract base class for section integrators."""

    @abc.abstractmethod
    def prepare_input(self, geo: CompoundGeometry, strain: ArrayLike):
        """Prepare general input to the integration method.

        Args:
            geo (CompoundGeometry): The geometry to integrate over.
            strain (ArrayLike): The scalar strain components necessary for
                describing the assumed strain distribution over the geometry.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def integrate(self, *prepared_input, **kwargs) -> float:
        """Integrate stresses over the gemetry.

        The input to this method is generated by the prepare_input method. It
        also takes kwargs depending on the concrete implementation.

        Arguments:
            *prepared_input: The input prepared by the prepare_input method.

        Keyword Arguments:
            **kwargs: Keyword arguments depending on the concrete
                implementation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def integrate_strain_response_on_geometry(
        self, geo: CompoundGeometry, strain: ArrayLike
    ):
        """Integrate over the geometry to obtain the response due
        to strains.
        """
        raise NotImplementedError


class MarinIntegrator(SectionIntegrator):
    """Section integrator based on the Marin algorithm."""

    def prepare_input(
        self, geo: CompoundGeometry, strain: ArrayLike
    ) -> t.Tuple[t.Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Prepare general input to the integration.

        Calculate the stresses based on strains in a set of points.

        Args:
            geo (CompoundGeometry): The geometry of the section.
            strain (ArrayLike): The strains and curvatures of the section.
                                given in the format (ea, ky, kz) which are
                                strain at 0,0
                                curvature y axis
                                curvature z axis
        """
        # This method should do the following tasks:
        # - For each geo:
        #   - ask constitutive law strain limits and coefficients
        #   - For each material part, the part should furthermore be split
        # according to constant, linear and parabolic stress distribution.
        #   - For each part collect coordinates y and z in separate np.ndarray
        # iterables, and stress coefficients in a two-dimensional np.ndarray.
        #
        # The method should therefore return a tuple that collects the y, z,
        # and stress coefficients for each part.
        prepared_input = []
        # 1. Rotate section in order to have neutral axis horizontal
        angle = atan2(strain[2], strain[1])

        rotated_geom = geo.rotate(angle)
        # 2. Get y coordinate of neutral axis in this new CRS
        strain_rotated = [strain[0], (strain[2] ** 2 + strain[1] ** 2) ** 0.5]

        # 3. For each SurfaceGeometry on the CompoundGeometry:
        for g in rotated_geom.geometries:
            # 3a. get coefficients and strain limits from constitutive law
            strains, coeffs = g.material.__marin__(strain_rotated)

            # 3b. Subdivide the polygon at the different strain limits
            for p in range(len(strains)):
                # Create the two lines for selecting the needed part
                y0 = (strain_rotated[0] - strains[p][0]) / strain_rotated[1]
                y1 = (strain_rotated[0] - strains[p][1]) / strain_rotated[1]
                if y0 > y1:
                    y0, y1 = y1, y0
                bbox = g.polygon.bounds
                line0 = create_line_point_angle((0, y0), 0, bbox)
                line1 = create_line_point_angle((0, y1), 0, bbox)
                lines = MultiLineString((line0, line1))
                # intersection
                result = g.split_two_lines(lines=lines)

                def get_input_polygon(polygon, coeffs):
                    # Let's be sure to orient in the right way
                    polygon = orient(polygon, 1)
                    if not polygon.exterior.is_ccw:
                        raise ValueError(
                            'The exterior of a polygon should have vertices \
                                         ordered ccw'
                        )
                    # Manage exterior part
                    x, y = polygon.exterior.coords.xy
                    x = np.array(x)
                    y = np.array(y)
                    prepared_input.append(
                        (0, np.array(x), np.array(y), np.array(coeffs))
                    )
                    # Manage holes
                    for i in polygon.interiors:
                        if i.is_ccw:
                            raise ValueError(
                                'A inner hole should have cw coordinates'
                            )
                        x, y = i.coords.xy
                        prepared_input.append(
                            (0, np.array(x), np.array(y), np.array(coeffs))
                        )

                if isinstance(result, Polygon):
                    # If the result is a single polygon
                    get_input_polygon(result, coeffs[p])
                elif isinstance(result, MultiPolygon):
                    # If the result is a MultiPolygon
                    for polygon in result.geoms:
                        get_input_polygon(polygon, coeffs[p])
        # Tentative proposal for managing reinforcement (PointGeometry)
        x = []
        y = []
        F = []
        for pg in rotated_geom.point_geometries:
            xp, yp = pg._point.coords.xy
            xp = xp[0]
            yp = yp[0]
            A = pg.area
            strain = strain_rotated[0] - strain_rotated[1] * yp
            x.append(xp)
            y.append(yp)
            F.append(pg.material.get_stress(strain)[0] * A)
        prepared_input.append((1, np.array(x), np.array(y), np.array(F)))

        return angle, prepared_input

    def integrate(
        self,
        angle: float,
        prepared_input: t.List[
            t.Tuple[int, np.ndarray, np.ndarray, np.ndarray]
        ],
    ) -> t.Tuple[float, float, float]:
        """Integrate stresses over the geometry."""
        # Set the stress resultants to zero
        N, Mx, My = 0.0, 0.0, 0.0

        # Loop through all parts of the section and add contributions
        for i, y, z, stress_coeff in prepared_input:
            if i == 0:
                # Find integration order from shape of stress coeff array
                n = stress_coeff.shape[0]

                # Calculate area moments
                area_moments_N = np.array(
                    [marin_integration(y, z, 0, k) for k in range(n)]
                )
                area_moments_Mx = np.array(
                    [marin_integration(y, z, 0, k + 1) for k in range(n)]
                )
                area_moments_My = np.array(
                    [marin_integration(y, z, 1, k) for k in range(n)]
                )

                # Calculate contributions to stress resultants
                N += sum(stress_coeff * area_moments_N)
                Mx += sum(stress_coeff * area_moments_Mx)
                My += sum(stress_coeff * area_moments_My)
            elif i == 1:
                # Reinforcement
                N += sum(stress_coeff)
                Mx += sum(stress_coeff * z)
                My += sum(stress_coeff * y)
        
        # Rotate back to section CRS
        print(angle)

        T = np.array([[cos(angle), sin(angle)],[-sin(angle), cos(angle)]])
        M = T @ np.array([[Mx],[My]])

        return N, M[0,0], M[1,0]

    def integrate_strain_response_on_geometry(
        self, geo: CompoundGeometry, strain: ArrayLike
    ):
        """Integrate the strain response with the Marin algorithm."""
        # Prepare the general input based on the geometry and the input strains
        angle, prepared_input = self.prepare_input(geo, strain)

        # Return the calculated response
        return self.integrate(angle, prepared_input)


integrator_registry = {'Marin': MarinIntegrator}


class IntegratorFactory:
    """A factory for integrators."""

    instances: t.Dict  # A dict of integrators that have been created.
    registry: t.Dict[str, SectionIntegrator]

    def __init__(self, registry: t.Dict[str, SectionIntegrator]):
        self.instances = {}
        self.registry = registry

    def __call__(self, method: str) -> SectionIntegrator:
        """Create an integrator based on its name."""
        self.instances.setdefault(
            method, self.registry.get(method, MarinIntegrator)
        )
        # Here we should throw a warning if the user input an integrator not
        # given in the registry.
        return self.instances.get(method)


integrator_factory = IntegratorFactory(integrator_registry)
