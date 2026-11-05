"""Encadenamiento hacia adelante sobre cláusulas definidas"""

from __future__ import annotations

from logic.atoms import Atom, apply_atom, format_subst, unify
from logic.kb import KnowledgeBase, Rule
from logic.result import InferenceResult


def renombrar(rule: Rule, n: int) -> Rule:
    """Renombra las variables de la regla (x -> x_n) para que dos usos no compartan variable"""
    mapa: dict[str, str] = {}

    def ren(atom: Atom) -> Atom:
        args = []
        for arg in atom.args:
            if arg[:1].islower():
                mapa.setdefault(arg, f"{arg}_{n}")
                args.append(mapa[arg])
            else:
                args.append(arg)
        return Atom(atom.predicate, tuple(args))

    return Rule(rule.rule_id, tuple(ren(p) for p in rule.premises), ren(rule.head))


def satisfacer(premisas: tuple[Atom, ...], hechos: list[Atom], subst: dict[str, str]):
    """Genera todas las sustituciones que satisfacen las premisas, en orden"""
    if not premisas:
        yield subst
        return
    primera, resto = premisas[0], premisas[1:]
    meta = apply_atom(primera, subst)
    for hecho in hechos:
        theta = unify(meta, hecho, subst)
        if theta is not None:
            yield from satisfacer(resto, hechos, theta)


def forward_chain(kb: KnowledgeBase, query: Atom, *, max_rondas: int = 50) -> InferenceResult:
    hechos = list(kb.facts)
    nuevos: list[Atom] = []
    eventos = [
        f"Hechos iniciales: {', '.join(str(h) for h in hechos)}",
        f"Consulta: {query}",
    ]
    contador = 0

    for ronda in range(1, max_rondas + 1):
        # Foto de los hechos al empezar la ronda: lo nuevo no se usa hasta la siguiente
        base_ronda = list(hechos)
        nuevos_ronda: list[Atom] = []
        eventos.append(f"--- ronda {ronda} ---")
        for regla in kb.rules:
            contador += 1
            fresca = renombrar(regla, contador)
            for theta in satisfacer(fresca.premises, base_ronda, {}):
                cabeza = apply_atom(fresca.head, theta)
                if cabeza in hechos or cabeza in nuevos_ronda:
                    continue
                nuevos_ronda.append(cabeza)
                eventos.append(f"Dispara {regla.rule_id} {format_subst(theta)} => {cabeza}")
        if not nuevos_ronda:
            eventos.append("Sin hechos nuevos: punto fijo")
            break
        hechos.extend(nuevos_ronda)
        nuevos.extend(nuevos_ronda)
    else:
        eventos.append("Detenido: se alcanzó max_rondas")

    for hecho in hechos:
        theta = unify(query, hecho, {})
        if theta is not None:
            eventos.append(f"Consulta probada: {hecho}")
            return InferenceResult(True, theta, nuevos, eventos)
    eventos.append("Consulta NO probada")
    return InferenceResult(False, None, nuevos, eventos)
