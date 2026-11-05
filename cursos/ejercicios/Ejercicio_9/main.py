"""Corre encadenamiento hacia adelante y hacia atrás sobre la base de la biblioteca.

Uso:
    python main.py                                # las 3 consultas, sin hechos extra
    python main.py --extra "TieneCredencial(Luis)"  # añade hechos y repite
"""

from __future__ import annotations

import argparse
from pathlib import Path

from logic.atoms import parse_atom
from logic.backward import backward_chain
from logic.forward import forward_chain
from logic.kb import load_kb

KB_PATH = Path(__file__).parent / "kb" / "biblioteca.yaml"

ESPERADO_ADELANTE = [
    "Miembro(Ana)",
    "Miembro(Marta)",
    "Becario(Ana)",
    "AccesoNoche(Ana)",
    "AccesoNoche(Marta)",
]
ESPERADO_PROBADA = {
    "AccesoNoche(Ana)": True,
    "AccesoNoche(Luis)": False,
    "AccesoNoche(Marta)": True,
}


def imprimir(titulo: str, resultado) -> None:
    print(f"\n### {titulo}")
    print(f"Probada: {'SÍ' if resultado.proved else 'NO'}")
    for evento in resultado.events:
        print("  " + evento)


def verificar(resultados: dict) -> None:
    """Criterios de aceptación del ejercicio (base original, sin hechos extra)"""
    for consulta, (adelante, atras) in resultados.items():
        assert [str(a) for a in adelante.inferred] == ESPERADO_ADELANTE, consulta
        assert adelante.proved == ESPERADO_PROBADA[consulta], consulta
        assert atras.proved == ESPERADO_PROBADA[consulta], consulta

    traza_ana = "\n".join(resultados["AccesoNoche(Ana)"][1].events)
    assert "R_acceso" in traza_ana and "R_miembro_est" in traza_ana
    for prohibido in ("Luis", "Marta", "R_beca", "Becario"):
        assert prohibido not in traza_ana, prohibido

    traza_marta = resultados["AccesoNoche(Marta)"][1].events
    texto = "\n".join(traza_marta)
    assert texto.index("R_miembro_est") < texto.index("R_miembro_prof")
    assert "falla  Estudiante(Marta)" in texto
    assert "hecho  Profesor(Marta)" in texto

    traza_luis = "\n".join(resultados["AccesoNoche(Luis)"][1].events)
    assert "falla  TieneCredencial(Luis)" in traza_luis
    assert "falla  Profesor(Luis)" in traza_luis
    print("\nCriterios de aceptación: OK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra", action="append", default=[], help="hecho extra, p. ej. 'TieneCredencial(Luis)'")
    args = parser.parse_args()

    kb, consultas = load_kb(KB_PATH)
    extra = [parse_atom(e) for e in args.extra]
    if extra:
        kb = kb.with_extra_facts(extra)
        print("Hechos añadidos: " + ", ".join(str(a) for a in extra))

    resultados = {}
    for consulta in consultas:
        print("\n" + "=" * 70)
        print(f"CONSULTA {consulta}")
        adelante = forward_chain(kb, consulta)
        atras = backward_chain(kb, consulta)
        imprimir("Encadenamiento hacia adelante", adelante)
        print("  Átomos nuevos: " + (", ".join(str(a) for a in adelante.inferred) or "(ninguno)"))
        imprimir("Encadenamiento hacia atrás", atras)
        resultados[str(consulta)] = (adelante, atras)

    if not extra:
        verificar(resultados)


if __name__ == "__main__":
    main()
