"""Abstract base classes"""
import abc
import typing as t
import warnings


class Material(abc.ABC):
    """Abstract base class for materials."""

    __materials__: t.Tuple[str] = ()

    def __init__(self, density: float, name: t.Optional[str] = None) -> None:
        """Initializes an instance of a new material

        Args:
            density (float): density of the material in kg/m3

        Keyword Args:
            name (Optional[str]): descriptive name of the material
        """
        self._density = abs(density)
        self._name = name if name is not None else "Material"

    def update_attributes(self, updated_attributes: t.Dict) -> None:
        """Function for updating the attributes specified in the input
        dictionary

        Args:
            updated_attributes (dict): the dictionary of parameters to be
                updated (not found parameters are skipped with a warning)
        """
        for key, value in updated_attributes.items():
            if not hasattr(self, '_' + key):
                str_list_keys = ', '.join(updated_attributes.keys())
                str_warn = (
                    f"WARNING: attribute '{key}' not found."
                    " Ignoring the entry.\n"
                    f"Used keys in the call: {str_list_keys}"
                )
                warnings.warn(str_warn)
                continue
            setattr(self, '_' + key, value)

    @property
    def name(self):
        """Returns the name of the material"""
        return self._name

    @property
    def density(self):
        """Returns the density of the material in kg/m3"""
        return self._density


class ConstitutiveLaw(abc.ABC):
    """Abstract base class for constitutive laws."""

    constitutive_law_counter: t.ClassVar[int] = 0

    def __init__(self, name: t.Optional[str] = None) -> None:
        self.id = self.constitutive_law_counter
        self._name = name if name is not None else f"ConstitutiveLaw_{self.id}"
        self._increase_global_counter()

    @property
    def name(self):
        """Returns the name of the constitutive law"""
        return self._name

    @classmethod
    def _increase_global_counter(cls):
        cls.constitutive_law_counter += 1

    @abc.abstractmethod
    def get_stress(self, eps: float) -> float:
        """Each constitutive law should provide a method to return the
        stress given the strain level"""

    @abc.abstractmethod
    def get_tangent(self, eps: float) -> float:
        """Each constitutive law should provide a method to return the
        tangent at a given strain level"""

    def get_secant(self, eps: float) -> float:
        """Method to return the
        secant at a given strain level"""
        sig = self.get_stress(eps)
        return sig / eps
