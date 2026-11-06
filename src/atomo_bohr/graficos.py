"""Módulo de representaciones gráficas para el modelo del átomo de Bohr.

Proporciona funciones que devuelven objetos ``matplotlib.figure.Figure`` listos
para ser incrustados tanto en interfaces de escritorio (Tkinter) como en aplicaciones
web interactivas (Streamlit).
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .core import BohrAtom


def dibujar_niveles_energia(
    atomo: BohrAtom,
    n_max: int = 6,
    transiciones: Optional[Sequence[Tuple[int, int]]] = None,
    ax: Optional[Axes] = None,
) -> Figure:
    """Representa en un diagrama los niveles de energía y las transiciones entre ellos.

    :param atomo: Instancia de :class:`BohrAtom`.
    :type atomo: BohrAtom
    :param n_max: Nivel cuántico máximo a graficar (:math:`n_{\\max} \\ge 2`).
    :type n_max: int
    :param transiciones: Secuencia de tuplas ``(n_inicial, n_final)`` a dibujar.
    :type transiciones: Optional[Sequence[Tuple[int, int]]]
    :param ax: Eje de Matplotlib sobre el cual dibujar. Si es ``None``, crea una figura nueva.
    :type ax: Optional[Axes]
    :return: Figura de Matplotlib generada.
    :rtype: Figure
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.5, 5.2), dpi=100)
    else:
        fig = ax.figure

    energias = atomo.energias_niveles(n_max=n_max, unidades="eV")
    niveles = np.arange(1, n_max + 1)

    for n, e_val in zip(niveles, energias):
        ax.hlines(e_val, xmin=0.1, xmax=0.9, color="#1f77b4", linewidth=2.0)
        ax.text(
            0.92,
            e_val,
            f"n={n} ({e_val:.2f} eV)",
            va="center",
            ha="left",
            fontsize=8.5,
            fontweight="bold",
            color="#1f2937",
        )

    ax.axhline(0.0, color="#6b7280", linestyle="--", linewidth=1.0, label="Ionización (0 eV)")

    if transiciones:
        num_t = len(transiciones)
        posiciones_x = np.linspace(0.25, 0.75, max(num_t, 1))
        for idx, (n_i, n_f) in enumerate(transiciones):
            if n_i == n_f or max(n_i, n_f) > n_max or min(n_i, n_f) < 1:
                continue
            res = atomo.transicion_electronica(n_i, n_f)
            e_i = res.energia_inicial_ev
            e_f = res.energia_final_ev
            x_pos = posiciones_x[idx]
            color_flecha = "#dc2626" if res.tipo_transicion == "emisión" else "#059669"

            ax.annotate(
                "",
                xy=(x_pos, e_f),
                xytext=(x_pos, e_i),
                arrowprops=dict(arrowstyle="->", color=color_flecha, lw=2.2),
            )
            e_med = 0.5 * (e_i + e_f)
            ax.text(
                x_pos + 0.02,
                e_med,
                f"{res.longitud_onda_nm:.1f} nm\n({res.tipo_transicion})",
                fontsize=7.8,
                color=color_flecha,
                va="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color_flecha, alpha=0.85),
            )

    ax.set_xlim(0.0, 1.35)
    e_min = energias[0]
    ax.set_ylim(e_min * 1.12, abs(e_min) * 0.08)
    ax.set_xticks([])
    ax.set_ylabel("Energía $E_n$ (eV)", fontsize=10)
    ax.set_title(f"Niveles de Energía y Transiciones (Z = {atomo.Z})", fontsize=11, fontweight="bold")
    ax.grid(axis="y", linestyle=":", alpha=0.45)
    return fig


def dibujar_orbitas_planas(
    atomo: BohrAtom,
    n_max: int = 4,
    transicion: Optional[Tuple[int, int]] = None,
    ax: Optional[Axes] = None,
) -> Figure:
    """Dibuja de manera simplificada las órbitas electrónicas circulares en el plano 2D.

    :param atomo: Instancia de :class:`BohrAtom`.
    :type atomo: BohrAtom
    :param n_max: Número máximo de órbitas a mostrar.
    :type n_max: int
    :param transicion: Par ``(n_inicial, n_final)`` para resaltar el salto orbital del electrón.
    :type transicion: Optional[Tuple[int, int]]
    :param ax: Eje de Matplotlib existente (opcional).
    :type ax: Optional[Axes]
    :return: Figura de Matplotlib con las órbitas en el plano XY.
    :rtype: Figure
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.0, 5.2), dpi=100)
    else:
        fig = ax.figure

    radios = atomo.radios_orbitas(n_max=n_max, unidades="A")
    theta = np.linspace(0.0, 2.0 * np.pi, 300)

    # Núcleo central
    ax.scatter([0.0], [0.0], color="#d97706", s=95, zorder=5, label=f"Núcleo (+{atomo.Z}e)")

    colores = plt.cm.viridis(np.linspace(0.15, 0.85, n_max))
    for idx, (n, r_val) in enumerate(zip(range(1, n_max + 1), radios)):
        x_orb = r_val * np.cos(theta)
        y_orb = r_val * np.sin(theta)
        ax.plot(
            x_orb,
            y_orb,
            linestyle="--",
            linewidth=1.5,
            color=colores[idx],
            label=f"n={n} (r={r_val:.2f} Å)",
        )

    if transicion is not None:
        n_i, n_f = transicion
        if 1 <= n_i <= n_max and 1 <= n_f <= n_max and n_i != n_f:
            r_i = atomo.radio_orbita(n_i, unidades="A")
            r_f = atomo.radio_orbita(n_f, unidades="A")
            ang = np.pi / 4.0
            xi, yi = r_i * np.cos(ang), r_i * np.sin(ang)
            xf, yf = r_f * np.cos(ang), r_f * np.sin(ang)

            ax.scatter([xi], [yi], color="#dc2626", s=60, zorder=6, label=f"e⁻ inicial (n={n_i})")
            ax.scatter([xf], [yf], color="#2563eb", s=60, zorder=6, label=f"e⁻ final (n={n_f})")
            ax.annotate(
                "",
                xy=(xf, yf),
                xytext=(xi, yi),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=2.0),
            )

    r_max = radios[-1] * 1.18
    ax.set_xlim(-r_max, r_max)
    ax.set_ylim(-r_max, r_max)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x (Å)", fontsize=10)
    ax.set_ylabel("y (Å)", fontsize=10)
    ax.set_title(f"Órbitas Electrónicas en el Plano (Z = {atomo.Z})", fontsize=11, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.45)
    ax.legend(loc="upper right", fontsize=7.8, framealpha=0.9)
    return fig


def crear_figura_dual(
    atomo: BohrAtom,
    n_max: int = 5,
    n_inicial: int = 3,
    n_final: int = 2,
) -> Figure:
    """Crea una figura combinada con las órbitas en el plano y los niveles de energía.

    Esta función alimenta simultáneamente el lienzo de Tkinter y la vista de Streamlit.

    :param atomo: Instancia configurada de :class:`BohrAtom`.
    :type atomo: BohrAtom
    :param n_max: Nivel cuántico máximo a mostrar en ambos paneles.
    :type n_max: int
    :param n_inicial: Nivel inicial de la transición activa.
    :type n_inicial: int
    :param n_final: Nivel final de la transición activa.
    :type n_final: int
    :return: Figura de Matplotlib con dos subgráficos.
    :rtype: Figure
    """
    fig, (ax_orb, ax_niv) = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=100)
    transicion = (n_inicial, n_final) if n_inicial != n_final else None
    lista_trans = [transicion] if transicion is not None else []

    dibujar_orbitas_planas(atomo, n_max=n_max, transicion=transicion, ax=ax_orb)
    dibujar_niveles_energia(atomo, n_max=n_max, transiciones=lista_trans, ax=ax_niv)
    fig.tight_layout()
    return fig