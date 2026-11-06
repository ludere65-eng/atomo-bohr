.. atomo-bohr documentation master file

Bienvenido a la documentación de atomo-bohr
===========================================

Librería didáctica en Python para resolver sistemas del átomo de Bohr en átomos hidrogenoides, implementando patrones de diseño de software (Strategy, Factory, Observer) y visualización gráfica dual.

Instalación
-----------

.. code-block:: bash

   pip install atomo-bohr
   pip install "atomo-bohr[gui]"

Módulo Principal (Core)
-----------------------

Contiene toda la lógica física y analítica del sistema.

.. automodule:: atomo_bohr.core
   :members:
   :undoc-members:
   :show-inheritance:

Módulo de Gráficos (Visualización)
----------------------------------

Contiene las funciones para renderizar niveles de energía y órbitas planas usando Matplotlib.

.. automodule:: atomo_bohr.graficos
   :members:
   :undoc-members:
   :show-inheritance:

Índices y tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`