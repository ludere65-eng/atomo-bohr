# atomo-bohr

Librería didáctica en Python para resolver y visualizar el modelo del átomo de Bohr en el hidrógeno y sistemas hidrogenoides (con número atómico $Z$ arbitrario):
Cálculo analítico de niveles de energía, radios orbitales, transiciones espectroscópicas y visualización dual en **Tkinter** y **Streamlit**.

$$E_n = -\frac{\mu e^4 Z^2}{8 \varepsilon_0^2 h^2 n^2}, \qquad r_n = \frac{\varepsilon_0 h^2 n^2}{\pi \mu e^2 Z}$$

## Instalación

```bash
pip install atomo-bohr          # sólo la lógica (depende de numpy)
pip install "atomo-bohr[gui]"   # + matplotlib y streamlit para interfaces gráficas
```
## Uso
```bash
from atomo_bohr import BohrAtom, BohrMasaReducida, BohrRelativista

atomo = BohrAtom(Z=1, estrategia="masa_infinita")
print(atomo.energias_niveles(n_max=5))                # energías en eV
print(atomo.radios_orbitas(n_max=5, unidades="A"))    # radios en Ángstroms

res = atomo.transicion_electronica(n_inicial=3, n_final=2)
print(res.delta_energia_ev, res.frecuencia_hz, res.longitud_onda_nm)

atomo.estrategia = BohrMasaReducida()                 # cambio dinámico de estrategia
```

## Modelos disponibles (FabricaModelos.disponibles()):

Estrategia,Tipo,Descripción Física
BohrMasaInfinita,Analítica clásica,Núcleo estático de masa infinita (μ=me​)
BohrMasaReducida,Corrección nuclear,Incluye movimiento del núcleo con masa reducida μ
BohrRelativista,Corrección relativista,Incorpora corrección cinética de orden (αZ)2

## Arquitectura
core.py — toda la lógica física implementada únicamente con NumPy (sin acoplamiento gráfico).Strategy: ModeloFisico (abstracta) $\rightarrow$BohrMasaInfinita, BohrMasaReducida, BohrRelativista; BohrAtom es el contexto.
Fábrica con registro: FabricaModelos instancia estrategias por nombre.
Observador (ligero): BohrAtom.suscribir(funcion) notifica cada vez que se calcula un TransicionResultado.

graficos.py — generador de figuras Matplotlib para diagramas de niveles y órbitas planas.

GUI.py — interfaz dual que ejecuta simultáneamente Tkinter + Streamlit usando la API pública.

## Desarrollo

Una sola vez, desde la carpeta raíz del proyecto:
``` bash
python -m venv .venv
source .venv/bin/activate             # En Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[gui,dev]"
```

Para ejecutar los ejemplos o lanzar simultáneamente la ventana de Tkinter y la aplicación web en Streamlit:
```bash
python ejemplo_consola.py
python GUI.py
```

## Pruebas
```bash
pytest -v
```

## Autor y Licencia
Autor: Luder Espitia Guzmán

Licencia: MIT