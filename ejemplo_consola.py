"""Ejemplo de uso por consola de la librería atomo_bohr."""

from atomo_bohr import BohrAtom, BohrMasaReducida, BohrRelativista, FabricaModelos


def main() -> None:
    print("Modelos disponibles en fábrica:", FabricaModelos.disponibles())

    # 1. Instanciar átomo de Hidrógeno (Z=1) con estrategia por defecto
    hidrogeno = BohrAtom(Z=1, estrategia="masa_infinita")

    # Suscribir un observador ligero para registrar transiciones
    hidrogeno.suscribir(
        lambda res: print(
            f"[Observador] Transición {res.n_inicial} -> {res.n_final} ({res.tipo_transicion}): "
            f"ΔE = {res.delta_energia_ev:.4f} eV, λ = {res.longitud_onda_nm:.2f} nm ({res.serie_espectral})"
        )
    )

    print("\n--- Energías de los primeros 5 niveles (eV) ---")
    print(hidrogeno.energias_niveles(n_max=5, unidades="eV"))

    print("\n--- Radios de las primeras 5 órbitas (Å) ---")
    print(hidrogeno.radios_orbitas(n_max=5, unidades="A"))

    print("\n--- Transición H-alfa (n=3 -> n=2) con núcleo fijo ---")
    res_clasico = hidrogeno.transicion_electronica(n_inicial=3, n_final=2)

    # 2. Cambiar estrategia en tiempo de ejecución sin tocar el resto del código
    print("\n--- Cambio de estrategia a Masa Reducida y Relativista ---")
    hidrogeno.estrategia = BohrMasaReducida()
    res_reducida = hidrogeno.transicion_electronica(n_inicial=3, n_final=2)

    hidrogeno.estrategia = BohrRelativista()
    res_relativista = hidrogeno.transicion_electronica(n_inicial=3, n_final=2)

    print(
        f"\nComparación λ (nm): Clásico={res_clasico.longitud_onda_nm:.4f} nm | "
        f"Masa reducida={res_reducida.longitud_onda_nm:.4f} nm | "
        f"Relativista={res_relativista.longitud_onda_nm:.4f} nm"
    )


if __name__ == "__main__":
    main()