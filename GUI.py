"""Interfaz gráfica dual (Tkinter + Streamlit simultáneos) para el Átomo de Bohr.

Al ejecutarse desde la terminal con ``python GUI.py``, levanta en segundo plano el
servidor interactivo de Streamlit y abre simultáneamente la ventana nativa de Tkinter,
compartiendo el mismo motor de cálculo y generación de figuras Matplotlib.
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

from atomo_bohr import BohrAtom, FabricaModelos
from atomo_bohr.graficos import crear_figura_dual


def _ejecutando_en_streamlit() -> bool:
    """Detecta si el archivo actual está siendo interpretado dentro del runtime de Streamlit."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


# =====================================================================
# MODO 1: INTERFAZ WEB EN STREAMLIT
# =====================================================================
def ejecutar_interfaz_streamlit() -> None:
    """Renderiza el panel gráfico interactivo en Streamlit."""
    import streamlit as st

    st.set_page_config(
        page_title="Átomo de Bohr - Simulador Cuántico",
        layout="wide",
    )
    st.title("Simulador del Modelo Atómico de Bohr (Vista Streamlit)")
    st.markdown(
        "Cálculo analítico y proyección gráfica de **órbitas electrónicas en el plano** "
        "y **diagramas de niveles de energía** para átomos hidrogenoides."
    )

    with st.sidebar:
        st.header("Parámetros del Sistema")
        z_val = st.slider("Número atómico (Z)", min_value=1, max_value=10, value=1, step=1)
        estrategia_nombre = st.selectbox(
            "Estrategia física (Strategy)",
            options=FabricaModelos.disponibles(),
            index=0,
        )
        n_max = st.slider("Nivel cuántico máximo (n_max)", min_value=2, max_value=8, value=5)
        n_inicial = st.number_input("Nivel inicial (n_i)", min_value=1, max_value=n_max, value=min(3, n_max))
        n_final = st.number_input("Nivel final (n_f)", min_value=1, max_value=n_max, value=min(2, n_max))

    atomo = BohrAtom(Z=int(z_val), estrategia=estrategia_nombre)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"Energía E({n_inicial})", f"{atomo.energia_nivel(int(n_inicial)):.4f} eV")
    col2.metric(f"Radio r({n_inicial})", f"{atomo.radio_orbita(int(n_inicial), unidades='A'):.4f} Å")

    if int(n_inicial) != int(n_final):
        res = atomo.transicion_electronica(int(n_inicial), int(n_final))
        col3.metric(f"ΔE ({res.tipo_transicion})", f"{res.delta_energia_ev:.4f} eV")
        col4.metric("Longitud de onda (λ)", f"{res.longitud_onda_nm:.2f} nm ({res.serie_espectral})")
    else:
        col3.metric("Transición", "Estado estacionario")
        col4.metric("Longitud de onda (λ)", "N/A (n_i = n_f)")

    fig = crear_figura_dual(
        atomo,
        n_max=int(n_max),
        n_inicial=int(n_inicial),
        n_final=int(n_final),
    )
    st.pyplot(fig)


# =====================================================================
# MODO 2: INTERFAZ DE ESCRITORIO EN TKINTER + LANZADOR SIMULTÁNEO
# =====================================================================
def ejecutar_interfaz_tkinter(lanzar_streamlit: bool = True) -> None:
    """Inicia la ventana gráfica en Tkinter y levanta Streamlit simultáneamente."""
    import tkinter as tk
    from tkinter import ttk, messagebox
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

    proceso_streamlit = None
    if lanzar_streamlit and os.environ.get("BOHR_STREAMLIT_ACTIVO") != "1":
        entorno = os.environ.copy()
        entorno["BOHR_STREAMLIT_ACTIVO"] = "1"
        ruta_script = str(Path(__file__).resolve())
        try:
            proceso_streamlit = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", ruta_script],
                env=entorno,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("-> Servidor Streamlit iniciado simultáneamente en http://localhost:8501")
        except Exception as exc:
            print(f"Aviso: No se pudo lanzar Streamlit en segundo plano: {exc}")

    raiz = tk.Tk()
    raiz.title("Átomo de Bohr - Interfaz Tkinter (Sincronizada con Motor Matplotlib)")
    raiz.geometry("1280x720")

    # Variables de control
    var_z = tk.IntVar(value=1)
    var_estrategia = tk.StringVar(value=FabricaModelos.disponibles()[0])
    var_nmax = tk.IntVar(value=5)
    var_ni = tk.IntVar(value=3)
    var_nf = tk.IntVar(value=2)
    var_resumen = tk.StringVar(value="")

    marco_ctrl = ttk.LabelFrame(raiz, text="Parámetros Físicos y Cuánticos", padding=10)
    marco_ctrl.pack(side=tk.TOP, fill=tk.X, padx=10, pady=6)

    ttk.Label(marco_ctrl, text="Z (Carga nuclear):").grid(row=0, column=0, padx=5, pady=4, sticky="w")
    spin_z = ttk.Spinbox(marco_ctrl, from_=1, to=20, textvariable=var_z, width=6)
    spin_z.grid(row=0, column=1, padx=5, pady=4)

    ttk.Label(marco_ctrl, text="Estrategia:").grid(row=0, column=2, padx=5, pady=4, sticky="w")
    combo_est = ttk.Combobox(
        marco_ctrl,
        textvariable=var_estrategia,
        values=FabricaModelos.disponibles(),
        state="readonly",
        width=16,
    )
    combo_est.grid(row=0, column=3, padx=5, pady=4)

    ttk.Label(marco_ctrl, text="n_max:").grid(row=0, column=4, padx=5, pady=4, sticky="w")
    spin_nmax = ttk.Spinbox(marco_ctrl, from_=2, to=8, textvariable=var_nmax, width=6)
    spin_nmax.grid(row=0, column=5, padx=5, pady=4)

    ttk.Label(marco_ctrl, text="n inicial (n_i):").grid(row=0, column=6, padx=5, pady=4, sticky="w")
    spin_ni = ttk.Spinbox(marco_ctrl, from_=1, to=8, textvariable=var_ni, width=6)
    spin_ni.grid(row=0, column=7, padx=5, pady=4)

    ttk.Label(marco_ctrl, text="n final (n_f):").grid(row=0, column=8, padx=5, pady=4, sticky="w")
    spin_nf = ttk.Spinbox(marco_ctrl, from_=1, to=8, textvariable=var_nf, width=6)
    spin_nf.grid(row=0, column=9, padx=5, pady=4)

    etiqueta_info = ttk.Label(
        raiz,
        textvariable=var_resumen,
        font=("Consolas", 10, "bold"),
        foreground="#1e3a8a",
        padding=(10, 4),
    )
    etiqueta_info.pack(side=tk.TOP, fill=tk.X)

    marco_graf = ttk.Frame(raiz)
    marco_graf.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

    figura_actual = None
    canvas_widget = None
    toolbar_widget = None

    def actualizar_graficos() -> None:
        nonlocal figura_actual, canvas_widget, toolbar_widget
        try:
            z = int(var_z.get())
            n_max = int(var_nmax.get())
            n_i = int(var_ni.get())
            n_f = int(var_nf.get())
            est = var_estrategia.get()

            if n_i > n_max or n_f > n_max:
                messagebox.showwarning(
                    "Rango cuántico",
                    "n_inicial y n_final deben ser menores o iguales a n_max.",
                )
                return

            atomo = BohrAtom(Z=z, estrategia=est)
            e_ni = atomo.energia_nivel(n_i, unidades="eV")
            r_ni = atomo.radio_orbita(n_i, unidades="A")

            if n_i != n_f:
                res = atomo.transicion_electronica(n_i, n_f)
                texto = (
                    f"[Z={z} | {est}]  E({n_i}) = {e_ni:.3f} eV  |  r({n_i}) = {r_ni:.3f} Å  |  "
                    f"Transición {n_i} -> {n_f} ({res.tipo_transicion}): "
                    f"ΔE = {res.delta_energia_ev:.4f} eV  |  ν = {res.frecuencia_hz:.3e} Hz  |  "
                    f"λ = {res.longitud_onda_nm:.2f} nm ({res.serie_espectral})"
                )
            else:
                texto = (
                    f"[Z={z} | {est}]  Estado estacionario n={n_i}:  "
                    f"E({n_i}) = {e_ni:.4f} eV  |  r({n_i}) = {r_ni:.4f} Å"
                )
            var_resumen.set(texto)

            if figura_actual is not None:
                plt.close(figura_actual)
            if canvas_widget is not None:
                canvas_widget.get_tk_widget().destroy()
            if toolbar_widget is not None:
                toolbar_widget.destroy()

            figura_actual = crear_figura_dual(atomo, n_max=n_max, n_inicial=n_i, n_final=n_f)
            canvas_widget = FigureCanvasTkAgg(figura_actual, master=marco_graf)
            canvas_widget.draw()
            toolbar_widget = NavigationToolbar2Tk(canvas_widget, marco_graf)
            toolbar_widget.update()
            canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        except Exception as err:
            messagebox.showerror("Error en el cálculo", str(err))

    btn_calc = ttk.Button(marco_ctrl, text="Actualizar Gráficos", command=actualizar_graficos)
    btn_calc.grid(row=0, column=10, padx=10, pady=4)

    def al_cerrar() -> None:
        if proceso_streamlit is not None and proceso_streamlit.poll() is None:
            proceso_streamlit.terminate()
        if figura_actual is not None:
            plt.close(figura_actual)
        raiz.destroy()

    raiz.protocol("WM_DELETE_WINDOW", al_cerrar)
    actualizar_graficos()
    raiz.mainloop()


if __name__ == "__main__":
    if _ejecutando_en_streamlit():
        ejecutar_interfaz_streamlit()
    else:
        ejecutar_interfaz_tkinter(lanzar_streamlit=True)