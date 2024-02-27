"""Tests for the concrete material properties of Eurocode 2, 2004, Tab. 3.1."""

import math

import pytest

from structuralcodes.codes.ec2_2004 import _concrete_material_properties


@pytest.mark.parametrize(
    'test_input, expect',
    [
        (12, 20),
        (16, 24),
        (20, 28),
        (25, 33),
        (30, 38),
        (35, 43),
        (40, 48),
        (45, 53),
        (50, 58),
        (55, 63),
        (60, 68),
        (70, 78),
        (80, 88),
        (90, 98),
    ],
)
def test_fcm(test_input, expect):
    """Test the fcm function."""
    assert math.isclose(_concrete_material_properties.fcm(test_input), expect)


@pytest.mark.parametrize(
    'test_input, expect',
    [
        (12, 1.6),
        (16, 1.9),
        (20, 2.2),
        (25, 2.6),
        (30, 2.9),
        (35, 3.2),
        (40, 3.5),
        (45, 3.8),
        (50, 4.1),
        (55, 4.2),
        (60, 4.4),
        (70, 4.6),
        (80, 4.8),
        (90, 5.0),
    ],
)
def test_fctm(test_input, expect):
    """Test the fctm function."""
    assert math.isclose(
        _concrete_material_properties.fctm(test_input), expect, rel_tol=2e-2
    )


@pytest.mark.parametrize(
    'test_input, expect',
    [
        (12, 1.1),
        (16, 1.3),
        (20, 1.5),
        (25, 1.8),
        (30, 2.0),
        (35, 2.2),
        (40, 2.5),
        (45, 2.7),
        (50, 2.9),
        (55, 3.0),
        (60, 3.1),
        (70, 3.2),
        (80, 3.4),
        (90, 3.5),
    ],
)
def test_fctk_5(test_input, expect):
    """Test the fctk_5 function."""
    assert math.isclose(
        _concrete_material_properties.fctk_5(
            _concrete_material_properties.fctm(test_input)
        ),
        expect,
        rel_tol=3.1e-2,
    )


@pytest.mark.parametrize(
    'test_input, expect',
    [
        (12, 2.0),
        (16, 2.5),
        (20, 2.9),
        (25, 3.3),
        (30, 3.8),
        (35, 4.2),
        (40, 4.6),
        (45, 4.9),
        (50, 5.3),
        (55, 5.5),
        (60, 5.7),
        (70, 6.0),
        (80, 6.3),
        (90, 6.6),
    ],
)
def test_fctk_95(test_input, expect):
    """Test the fctk_95 function."""
    assert math.isclose(
        _concrete_material_properties.fctk_95(
            _concrete_material_properties.fctm(test_input)
        ),
        expect,
        rel_tol=2.2e-2,
    )


@pytest.mark.parametrize(
    'test_input, expect',
    [
        (12, 27000),
        (16, 29000),
        (20, 30000),
        (25, 31000),
        (30, 33000),
        (35, 34000),
        (40, 35000),
        (45, 36000),
        (50, 37000),
        (55, 38000),
        (60, 39000),
        (70, 41000),
        (80, 42000),
        (90, 44000),
    ],
)
def test_Ecm(test_input, expect):
    """Test the Ecm function."""
    assert math.isclose(
        _concrete_material_properties.Ecm(
            _concrete_material_properties.fcm(test_input)
        ),
        expect,
        rel_tol=2e-2,
    )


@pytest.mark.parametrize(
    'test_input, expect',
    [
        (12, 1.8e-3),
        (16, 1.9e-3),
        (20, 2.0e-3),
        (25, 2.1e-3),
        (30, 2.2e-3),
        (35, 2.25e-3),
        (40, 2.3e-3),
        (45, 2.4e-3),
        (50, 2.45e-3),
        (55, 2.5e-3),
        (60, 2.6e-3),
        (70, 2.7e-3),
        (80, 2.8e-3),
        (90, 2.8e-3),
    ],
)
def test_eps_c1(test_input, expect):
    """Test the eps_c1 function."""
    assert math.isclose(
        _concrete_material_properties.eps_c1(
            _concrete_material_properties.fcm(test_input)
        ),
        expect,
        rel_tol=2e-2,
    )
