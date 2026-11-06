import os
import sys

# Le indicamos a Sphinx dónde encontrar el código fuente (carpeta src)
sys.path.insert(0, os.path.abspath('../src'))

project = 'atomo-bohr'
copyright = '2026, Luder Espitia Guzmán'
author = 'Luder Espitia Guzmán'
release = '0.1.0'

# Extensiones necesarias
extensions = [
    'sphinx.ext.autodoc',      # Extrae los docstrings automáticamente
    'sphinx.ext.viewcode',     # Agrega un botón para ver el código fuente en la web
    'sphinx.ext.mathjax',      # Renderiza fórmulas matemáticas LaTeX
    'sphinx.ext.napoleon',     # Soporte para docstrings estilo Google/NumPy
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Configuración visual (Tema clásico tipo documentación de Python)
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']