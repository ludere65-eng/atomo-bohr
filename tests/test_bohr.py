"""Pruebas unitarias con pytest para la librería atomo_bohr."""

import numpy as np
import pytest
import matplotlib.pyplot as plt

from atomo_bohr import (
    BohrAtom,
    BohrMasaInfinita,
    BohrMasaReducida,
    BohrRelativista,
    FabricaModelos,
)


def test_energia_estado_base_hidrogeno():
    """Verifica que la energía fundamental del hidrógeno sea aproximadamente -13.6057 eV."""
    atomo = BohrAtom(Z=1, estrategia=BohrMasaInfinita())
    e1 = atomo.energia_nivel(1, unidades="eV")
    assert np.isclose(e1, -13.605693, atol=1e-4)


def test_escalamiento_hidrogenoide_helio():
    """Verifica que para He+ (Z=2) la energía escale con Z^2 y el radio con 1/Z."""
    h = BohrAtom(Z=1)
    he_plus = BohrAtom(Z=2)
    assert np.isclose(he_plus.energia_nivel(1), 4.0 * h.energia_nivel(1), rtol=1e-6)
    assert np.isclose(he_plus.radio_orbita(1, "A"), 0.5 * h.radio_orbita(1, "A"), rtol=1e-6)


def test_radio_bohr_fundamental():
    """Comprueba que el radio de la primera órbita del hidrógeno sea a_0 ≈ 0.529177 Å."""
    atomo = BohrAtom(Z=1)
    r1_angstrom = atomo.radio_orbita(1, unidades="A")
    r1_a0 = atomo.radio_orbita(1, unidades="a0")
    assert np.isclose(r1_angstrom, 0.529177, atol=1e-4)
    assert np.isclose(r1_a0, 1.0, atol=1e-9)


def test_transicion_emision_y_absorcion():
    """Verifica el cálculo de ΔE, frecuencia y longitud de onda en emisión y absorción."""
    eventos = []
    atomo = BohrAtom(Z=1)
    atomo.suscribir(lambda r: eventos.append(r))

    emision = atomo.transicion_electronica(3, 2)
    absorcion = atomo.transicion_electronica(2, 3)

    assert emision.tipo_transicion == "emisión"
    assert absorcion.tipo_transicion == "absorción"
    assert np.isclose(emision.delta_energia_ev, absorcion.delta_energia_ev)
    assert np.isclose(emision.longitud_onda_nm, 656.11, atol=0.5)
    assert len(eventos) == 2


def test_cambio_estrategia_y_fabrica():
    """Verifica el patrón Strategy y la fábrica de modelos."""
    disponibles = FabricaModelos.disponibles()
    assert "masa_infinita" in disponibles
    assert "masa_reducida" in disponibles
    assert "relativista" in disponibles

    atomo = BohrAtom(Z=1, estrategia="masa_infinita")
    e_inf = atomo.energia_nivel(1)

    atomo.estrategia = BohrMasaReducida()
    e_red = atomo.energia_nivel(1)

    # Al usar masa reducida mu < m_e, la energía en magnitud es ligeramente menor
    assert abs(e_red) < abs(e_inf)

    atomo.estrategia = BohrRelativista()
    e_rel = atomo.energia_nivel(1)
    assert abs(e_rel) > abs(e_red)


def test_validaciones_errores():
    """Comprueba que entradas físicas inválidas lancen ValueError."""
    with pytest.raises(ValueError):
        BohrAtom(Z=0)
    atomo = BohrAtom(Z=1)
    with pytest.raises(ValueError):
        atomo.energia_nivel(0)
    with pytest.raises(ValueError):
        atomo.transicion_electronica(2, 2)


def test_generacion_graficos():
    """Verifica que los métodos gráficos generen figuras de Matplotlib válidas."""
    atomo = BohrAtom(Z=1)
    fig_niv = atomo.graficar_niveles(n_max=4, transiciones=[(3, 2)])
    fig_orb = atomo.graficar_orbitas(n_max=4, transicion=(3, 2))
    assert fig_niv is not None
    assert fig_orb is not None
    plt.close("all")