"""Módulo central con la lógica física del modelo atómico de Bohr.

Implementa los patrones de diseño Strategy, Factory y Observer para calcular
niveles de energía, radios orbitales, velocidades y transiciones electrónicas
en el átomo de hidrógeno e iones hidrogenoides, usando únicamente NumPy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Type
import numpy as np


@dataclass(frozen=True)
class TransicionResultado:
    """ Contenedor inmutable con los resultados de una transición electrónica.

    :param n_inicial: Número cuántico principal del estado inicial :math:`n_i`.
    :type n_inicial: int
    :param n_final: Número cuántico principal del estado final :math:`n_f`.
    :type n_final: int
    :param energia_inicial_ev: Energía del nivel inicial en electronvoltios (eV).
    :type energia_inicial_ev: float
    :param energia_final_ev: Energía del nivel final en electronvoltios (eV).
    :type energia_final_ev: float
    :param delta_energia_ev: Diferencia de energía :math:`|\\Delta E|` en eV.
    :type delta_energia_ev: float
    :param delta_energia_joules: Diferencia de energía :math:`|\\Delta E|` en Joules (J).
    :type delta_energia_joules: float
    :param frecuencia_hz: Frecuencia del fotón emitido o absorbido en Hertz (Hz).
    :type frecuencia_hz: float
    :param longitud_onda_m: Longitud de onda del fotón en metros (m).
    :type longitud_onda_m: float
    :param longitud_onda_nm: Longitud de onda del fotón en nanómetros (nm).
    :type longitud_onda_nm: float
    :param tipo_transicion: Indica si el proceso es ``'emisión'`` o ``'absorción'``.
    :type tipo_transicion: str
    :param serie_espectral: Nombre de la serie espectroscópica asociada al nivel inferior.
    :type serie_espectral: str
    """

    n_inicial: int
    n_final: int
    energia_inicial_ev: float
    energia_final_ev: float
    delta_energia_ev: float
    delta_energia_joules: float
    frecuencia_hz: float
    longitud_onda_m: float
    longitud_onda_nm: float
    tipo_transicion: str
    serie_espectral: str


class ModeloFisico(ABC):
    """Interfaz abstracta (Strategy) para variantes del modelo atómico de Bohr.

    Define el contrato para calcular la energía y el radio orbital del nivel :math:`n`
    bajo distintas aproximaciones físicas (núcleo fijo, masa reducida o relativista).
    """

    @abstractmethod
    def calcular_energia_joules(self, n: np.ndarray, atomo: "BohrAtom") -> np.ndarray:
        """Calcula la energía del nivel :math:`n` en Joules.

        :param n: Número(s) cuántico(s) principal(es) :math:`n \\ge 1`.
        :type n: np.ndarray
        :param atomo: Instancia de :class:`BohrAtom` con las constantes físicas.
        :type atomo: BohrAtom
        :return: Arreglo de energías en Joules.
        :rtype: np.ndarray
        """

    @abstractmethod
    def calcular_radio_metros(self, n: np.ndarray, atomo: "BohrAtom") -> np.ndarray:
        """Calcula el radio de la órbita circular para el nivel :math:`n` en metros.

        :param n: Número(s) cuántico(s) principal(es) :math:`n \\ge 1`.
        :type n: np.ndarray
        :param atomo: Instancia de :class:`BohrAtom` con las constantes físicas.
        :type atomo: BohrAtom
        :return: Arreglo de radios orbitales en metros.
        :rtype: np.ndarray
        """


class FabricaModelos:
    """Fábrica con registro para instanciar estrategias de :class:`ModeloFisico` por nombre."""

    _registro: Dict[str, Type[ModeloFisico]] = {}

    @classmethod
    def registrar(cls, nombre: str) -> Callable[[Type[ModeloFisico]], Type[ModeloFisico]]:
        """Decorador para registrar una estrategia física en la fábrica.

        :param nombre: Identificador único de la estrategia.
        :type nombre: str
        :return: Función decoradora de la subclase.
        :rtype: Callable[[Type[ModeloFisico]], Type[ModeloFisico]]
        """
        def decorador(subclase: Type[ModeloFisico]) -> Type[ModeloFisico]:
            cls._registro[nombre.lower()] = subclase
            return subclase
        return decorador

    @classmethod
    def crear(cls, nombre: str) -> ModeloFisico:
        """Crea una instancia de la estrategia solicitada por su nombre.

        :param nombre: Nombre registrado de la estrategia.
        :type nombre: str
        :raises ValueError: Si el nombre no se encuentra registrado.
        :return: Instancia del modelo físico correspondiente.
        :rtype: ModeloFisico
        """
        clave = nombre.lower()
        if clave not in cls._registro:
            disponibles = ", ".join(cls.disponibles())
            raise ValueError(
                f"Estrategia '{nombre}' desconocida. Disponibles: {disponibles}"
            )
        return cls._registro[clave]()

    @classmethod
    def disponibles(cls) -> List[str]:
        """Devuelve la lista de nombres de estrategias registradas.

        :return: Lista de identificadores disponibles.
        :rtype: List[str]
        """
        return list(cls._registro.keys())


@FabricaModelos.registrar("masa_infinita")
class BohrMasaInfinita(ModeloFisico):
    """Modelo clásico de Bohr asumiendo un núcleo estático de masa infinita.

    La energía y el radio vienen dados por:

    .. math::

        E_n = - \\frac{m_e e^4 Z^2}{8 \\varepsilon_0^2 h^2 n^2}, \\quad
        r_n = \\frac{\\varepsilon_0 h^2 n^2}{\\pi m_e e^2 Z}
    """

    def calcular_energia_joules(self, n: np.ndarray, atomo: "BohrAtom") -> np.ndarray:
        """Calcula la energía con masa electrónica en reposo :math:`m_e`."""
        prefactor = -(atomo.m_e * (atomo.e ** 4) * (atomo.Z ** 2)) / (
            8.0 * (atomo.epsilon_0 ** 2) * (atomo.h ** 2)
        )
        return prefactor / (n ** 2)

    def calcular_radio_metros(self, n: np.ndarray, atomo: "BohrAtom") -> np.ndarray:
        """Calcula el radio orbital con núcleo estático."""
        a0 = (atomo.epsilon_0 * (atomo.h ** 2)) / (
            np.pi * atomo.m_e * (atomo.e ** 2)
        )
        return a0 * (n ** 2) / atomo.Z


@FabricaModelos.registrar("masa_reducida")
class BohrMasaReducida(ModeloFisico):
    """Modelo de Bohr corrigiendo por el movimiento del núcleo mediante la masa reducida.

    Sustituye :math:`m_e` por la masa reducida del sistema electrón-núcleo:

    .. math::

        \\mu = \\frac{m_e M_N}{m_e + M_N}
    """

    def calcular_energia_joules(self, n: np.ndarray, atomo: "BohrAtom") -> np.ndarray:
        """Calcula la energía utilizando la masa reducida :math:`\\mu`."""
        mu = atomo.masa_reducida
        prefactor = -(mu * (atomo.e ** 4) * (atomo.Z ** 2)) / (
            8.0 * (atomo.epsilon_0 ** 2) * (atomo.h ** 2)
        )
        return prefactor / (n ** 2)

    def calcular_radio_metros(self, n: np.ndarray, atomo: "BohrAtom") -> np.ndarray:
        """Calcula el radio orbital corregido por masa reducida :math:`\\mu`."""
        mu = atomo.masa_reducida
        a_mu = (atomo.epsilon_0 * (atomo.h ** 2)) / (
            np.pi * mu * (atomo.e ** 2)
        )
        return a_mu * (n ** 2) / atomo.Z


@FabricaModelos.registrar("relativista")
class BohrRelativista(BohrMasaReducida):
    """Modelo con corrección relativista de primer orden en la energía cinética.

    Incorpora el término correctivo dependiente de la constante de estructura fina :math:`\\alpha`:

    .. math::

        E_{n,\\text{rel}} = E_n \\left[ 1 + \\frac{(\\alpha Z)^2}{n^2} \\left( \\frac{n}{n} - \\frac{3}{4} \\right) \\right]
    """

    def calcular_energia_joules(self, n: np.ndarray, atomo: "BohrAtom") -> np.ndarray:
        """Calcula la energía incluyendo la corrección relativista de orden :math:`(\\alpha Z)^2`."""
        e_base = super().calcular_energia_joules(n, atomo)
        alpha = (atomo.e ** 2) / (2.0 * atomo.epsilon_0 * atomo.h * atomo.c)
        correccion = 1.0 + ((alpha * atomo.Z) ** 2 / (n ** 2)) * (1.0 - 0.75)
        return e_base * correccion


class BohrAtom:
    """Clase principal que encapsula el modelo del átomo de Bohr hidrogenoide.

    Almacena las constantes físicas fundamentales y parámetros nucleares,
    exponiendo métodos analíticos para calcular niveles de energía, radios de órbita,
    velocidades orbitales, transiciones electrónicas y representaciones gráficas.

    :param Z: Número atómico (carga nuclear :math:`Z \\ge 1`), por defecto 1 (Hidrógeno).
    :type Z: int
    :param A: Número másico nuclear aproximado en nucleones, por defecto ``None`` (se estima de ``Z``).
    :type A: Optional[float]
    :param estrategia: Estrategia de cálculo físico o su nombre en :class:`FabricaModelos`.
    :type estrategia: ModeloFisico | str
    :raises ValueError: Si ``Z`` no es un entero positivo o si ``A`` no es positivo.
    """

    # Constantes físicas fundamentales (CODATA)
    h: float = 6.62607015e-34          # Constante de Planck (J·s)
    m_e: float = 9.1093837015e-31      # Masa del electrón en reposo (kg)
    m_p: float = 1.67262192369e-27     # Masa del protón (kg)
    e: float = 1.602176634e-19         # Carga elemental (C)
    epsilon_0: float = 8.8541878128e-12  # Permitividad eléctrica del vacío (F/m)
    c: float = 299792458.0             # Velocidad de la luz en el vacío (m/s)

    def __init__(
        self,
        Z: int = 1,
        A: Optional[float] = None,
        estrategia: ModeloFisico | str = "masa_infinita",
    ) -> None:
        if not isinstance(Z, (int, np.integer)) or Z < 1:
            raise ValueError("El número atómico Z debe ser un entero mayor o igual a 1.")
        self.Z: int = int(Z)

        if A is None:
            self.A: float = 1.0 if self.Z == 1 else float(2 * self.Z)
        else:
            if A <= 0:
                raise ValueError("El número másico A debe ser estrictamente positivo.")
            self.A = float(A)

        if isinstance(estrategia, str):
            self._estrategia: ModeloFisico = FabricaModelos.crear(estrategia)
        elif isinstance(estrategia, ModeloFisico):
            self._estrategia = estrategia
        else:
            raise TypeError("La estrategia debe ser una instancia de ModeloFisico o un str.")

        self._observadores: List[Callable[[TransicionResultado], None]] = []

    @property
    def estrategia(self) -> ModeloFisico:
        """Obtiene o modifica la estrategia activa de cálculo físico.

        :return: Estrategia activa.
        :rtype: ModeloFisico
        """
        return self._estrategia

    @estrategia.setter
    def estrategia(self, nueva_estrategia: ModeloFisico | str) -> None:
        if isinstance(nueva_estrategia, str):
            self._estrategia = FabricaModelos.crear(nueva_estrategia)
        elif isinstance(nueva_estrategia, ModeloFisico):
            self._estrategia = nueva_estrategia
        else:
            raise TypeError("La estrategia debe ser una instancia de ModeloFisico o un str.")

    @property
    def masa_reducida(self) -> float:
        """Calcula la masa reducida :math:`\\mu` del sistema electrón-núcleo en kg.

        :return: Masa reducida en kilogramos.
        :rtype: float
        """
        masa_nuclear = self.A * self.m_p
        return (self.m_e * masa_nuclear) / (self.m_e + masa_nuclear)

    @property
    def radio_bohr(self) -> float:
        """Devuelve el radio de Bohr fundamental :math:`a_0` en metros (:math:`\\approx 0.529\\text{ Å}`).

        :return: Radio de Bohr en metros.
        :rtype: float
        """
        return (self.epsilon_0 * (self.h ** 2)) / (np.pi * self.m_e * (self.e ** 2))

    def suscribir(self, funcion: Callable[[TransicionResultado], None]) -> None:
        """Registra un observador que será notificado cada vez que se calcule una transición.

        :param funcion: Función callback que recibe un :class:`TransicionResultado`.
        :type funcion: Callable[[TransicionResultado], None]
        """
        self._observadores.append(funcion)

    @staticmethod
    def _validar_nivel(n: int | Sequence[int] | np.ndarray) -> np.ndarray:
        """Valida que los números cuánticos principales sean enteros mayores o iguales a 1."""
        arr = np.asarray(n)
        if np.any(arr < 1) or not np.all(np.equal(np.mod(arr, 1), 0)):
            raise ValueError("El número cuántico principal n debe ser un entero mayor o igual a 1.")
        return arr.astype(float)

    def energia_nivel(self, n: int, unidades: str = "eV") -> float:
        """Calcula la energía de un electrón en el nivel cuántico :math:`n`.

        :param n: Número cuántico principal (:math:`n \\ge 1`).
        :type n: int
        :param unidades: Unidad de salida: ``'eV'`` (por defecto) o ``'J'`` (Joules).
        :type unidades: str
        :raises ValueError: Si :math:`n < 1` o la unidad no es soportada.
        :return: Energía del estado :math:`n` en la unidad indicada.
        :rtype: float
        """
        arr_n = self._validar_nivel(n)
        energia_j = float(self._estrategia.calcular_energia_joules(arr_n, self))
        u = unidades.lower()
        if u == "ev":
            return energia_j / self.e
        if u in ("j", "joules"):
            return energia_j
        raise ValueError("Unidades no reconocidas. Use 'eV' o 'J'.")

    def energias_niveles(self, n_max: int = 6, unidades: str = "eV") -> np.ndarray:
        """Calcula el arreglo de energías desde :math:`n = 1` hasta :math:`n_{\\max}`.

        :param n_max: Nivel cuántico máximo a evaluar (:math:`n_{\\max} \\ge 1`).
        :type n_max: int
        :param unidades: ``'eV'`` o ``'J'``.
        :type unidades: str
        :return: Vector de NumPy con las energías de cada nivel.
        :rtype: np.ndarray
        """
        if n_max < 1:
            raise ValueError("n_max debe ser mayor o igual a 1.")
        niveles = np.arange(1, n_max + 1, dtype=float)
        energias_j = self._estrategia.calcular_energia_joules(niveles, self)
        u = unidades.lower()
        if u == "ev":
            return energias_j / self.e
        if u in ("j", "joules"):
            return energias_j
        raise ValueError("Unidades no reconocidas. Use 'eV' o 'J'.")

    def radio_orbita(self, n: int, unidades: str = "m") -> float:
        """Calcula el radio de la órbita circular correspondiente al nivel :math:`n`.

        :param n: Número cuántico principal (:math:`n \\ge 1`).
        :type n: int
        :param unidades: ``'m'`` (metros), ``'A'`` (Ángstroms), ``'nm'`` o ``'a0'`` (radios de Bohr).
        :type unidades: str
        :raises ValueError: Si :math:`n < 1` o la unidad es inválida.
        :return: Radio orbital en la unidad seleccionada.
        :rtype: float
        """
        arr_n = self._validar_nivel(n)
        radio_m = float(self._estrategia.calcular_radio_metros(arr_n, self))
        u = unidades.lower()
        if u == "m":
            return radio_m
        if u in ("a", "angstrom", "å"):
            return radio_m * 1e10
        if u == "nm":
            return radio_m * 1e9
        if u == "a0":
            return radio_m / self.radio_bohr
        raise ValueError("Unidades no reconocidas. Use 'm', 'A', 'nm' o 'a0'.")

    def radios_orbitas(self, n_max: int = 6, unidades: str = "A") -> np.ndarray:
        """Devuelve un vector con los radios orbitales desde :math:`n = 1` hasta :math:`n_{\\max}`.

        :param n_max: Nivel cuántico máximo (:math:`n_{\\max} \\ge 1`).
        :type n_max: int
        :param unidades: ``'m'``, ``'A'``, ``'nm'`` o ``'a0'``.
        :type unidades: str
        :return: Vector de NumPy con los radios orbitales.
        :rtype: np.ndarray
        """
        if n_max < 1:
            raise ValueError("n_max debe ser mayor o igual a 1.")
        niveles = np.arange(1, n_max + 1, dtype=float)
        radios_m = self._estrategia.calcular_radio_metros(niveles, self)
        u = unidades.lower()
        if u == "m":
            return radios_m
        if u in ("a", "angstrom", "å"):
            return radios_m * 1e10
        if u == "nm":
            return radios_m * 1e9
        if u == "a0":
            return radios_m / self.radio_bohr
        raise ValueError("Unidades no reconocidas. Use 'm', 'A', 'nm' o 'a0'.")

    def velocidad_orbita(self, n: int) -> float:
        """Calcula la rapidez orbital tangencial del electrón en el nivel :math:`n` en m/s.

        .. math::

            v_n = \\frac{Z e^2}{2 \\varepsilon_0 h n}

        :param n: Número cuántico principal (:math:`n \\ge 1`).
        :type n: int
        :return: Velocidad orbital en metros por segundo (m/s).
        :rtype: float
        """
        arr_n = self._validar_nivel(n)
        return float((self.Z * (self.e ** 2)) / (2.0 * self.epsilon_0 * self.h * arr_n))

    @staticmethod
    def _identificar_serie(n_inferior: int) -> str:
        """Identifica el nombre de la serie espectral según el nivel inferior de la transición."""
        series = {
            1: "Lyman (UV)",
            2: "Balmer (Visible/UV)",
            3: "Paschen (IR)",
            4: "Brackett (IR)",
            5: "Pfund (IR)",
            6: "Humphreys (IR)",
        }
        return series.get(n_inferior, f"Serie n_min={n_inferior}")

    def transicion_electronica(self, n_inicial: int, n_final: int) -> TransicionResultado:
        """Calcula los parámetros físicos de la transición electrónica entre :math:`n_i` y :math:`n_f`.

        Determina la diferencia de energía :math:`|\\Delta E|`, la frecuencia :math:`\\nu = |\\Delta E|/h`
        y la longitud de onda :math:`\\lambda = c / \\nu` del fotón emitido o absorbido, notificando
        a los observadores suscritos.

        :param n_inicial: Nivel cuántico inicial :math:`n_i \\ge 1`.
        :type n_inicial: int
        :param n_final: Nivel cuántico final :math:`n_f \\ge 1` (:math:`n_f \\ne n_i`).
        :type n_final: int
        :raises ValueError: Si :math:`n_i = n_f` o algún nivel es menor que 1.
        :return: Objeto :class:`TransicionResultado` con todos los datos espectrales.
        :rtype: TransicionResultado
        """
        self._validar_nivel([n_inicial, n_final])
        if n_inicial == n_final:
            raise ValueError("El nivel inicial y final deben ser distintos para existir transición.")

        e_i_j = self.energia_nivel(n_inicial, unidades="J")
        e_f_j = self.energia_nivel(n_final, unidades="J")
        e_i_ev = e_i_j / self.e
        e_f_ev = e_f_j / self.e

        delta_j = abs(e_f_j - e_i_j)
        delta_ev = abs(e_f_ev - e_i_ev)
        frecuencia = delta_j / self.h
        longitud_onda_m = self.c / frecuencia
        longitud_onda_nm = longitud_onda_m * 1e9

        tipo = "emisión" if n_inicial > n_final else "absorción"
        serie = self._identificar_serie(min(n_inicial, n_final))

        resultado = TransicionResultado(
            n_inicial=int(n_inicial),
            n_final=int(n_final),
            energia_inicial_ev=e_i_ev,
            energia_final_ev=e_f_ev,
            delta_energia_ev=delta_ev,
            delta_energia_joules=delta_j,
            frecuencia_hz=frecuencia,
            longitud_onda_m=longitud_onda_m,
            longitud_onda_nm=longitud_onda_nm,
            tipo_transicion=tipo,
            serie_espectral=serie,
        )

        for callback in self._observadores:
            callback(resultado)

        return resultado

    def graficar_niveles(
        self,
        n_max: int = 6,
        transiciones: Optional[Sequence[Tuple[int, int]]] = None,
        ax: Optional[" object "] = None,
    ):
        """Genera el diagrama de niveles de energía y transiciones posibles.

        :param n_max: Número máximo de niveles a dibujar.
        :type n_max: int
        :param transiciones: Lista de pares ``(n_i, n_f)`` a destacar con flechas.
        :type transiciones: Optional[Sequence[Tuple[int, int]]]
        :param ax: Eje de Matplotlib existente (opcional).
        :return: Figura de Matplotlib con el diagrama de niveles.
        """
        from .graficos import dibujar_niveles_energia
        return dibujar_niveles_energia(self, n_max=n_max, transiciones=transiciones, ax=ax)

    def graficar_orbitas(
        self,
        n_max: int = 4,
        transicion: Optional[Tuple[int, int]] = None,
        ax: Optional[" object "] = None,
    ):
        """Dibuja las órbitas electrónicas circulares en el plano 2D.

        :param n_max: Número máximo de órbitas concéntricas a representar.
        :type n_max: int
        :param transicion: Tupla opcional ``(n_i, n_f)`` para ilustrar el salto del electrón.
        :type transicion: Optional[Tuple[int, int]]
        :param ax: Eje de Matplotlib existente (opcional).
        :return: Figura de Matplotlib con el diagrama de órbitas en el plano.
        """
        from .graficos import dibujar_orbitas_planas
        return dibujar_orbitas_planas(self, n_max=n_max, transicion=transicion, ax=ax)