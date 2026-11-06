"""Paquete principal del modelo del átomo de Bohr para sistemas hidrogenoides.

Expone la clase principal :class:`BohrAtom`, las estrategias de corrección física
y la fábrica de modelos para cálculos analíticos y representaciones gráficas.
"""

from .core import (
    BohrAtom,
    BohrMasaInfinita,
    BohrMasaReducida,
    BohrRelativista,
    FabricaModelos,
    ModeloFisico,
    TransicionResultado,
)

__all__ = [
    "BohrAtom",
    "TransicionResultado",
    "ModeloFisico",
    "BohrMasaInfinita",
    "BohrMasaReducida",
    "BohrRelativista",
    "FabricaModelos",
]

__version__ = "0.1.0"