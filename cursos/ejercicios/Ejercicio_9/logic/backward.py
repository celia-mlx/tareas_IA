from __future__ import annotations

from logic.atoms import Atom, apply_atom, format_subst, unify
from logic.forward import renombrar
from logic.kb import KnowledgeBase
from logic.result import InferenceResult


def backward_chain(kb: KnowledgeBase, query: Atom, *, max_prof: int = 25) -> InferenceResult:
    """Prueba la consulta reduciéndola a hecho"""
    eventos = [f"Consulta: {query}"]
    contador = [0]
    metas_visitadas: list[Atom] = []

    def sangria(prof: int) -> str:
        return "  " * prof

    def bc_or(meta: Atom, subst: dict[str, str], prof: int, pila: tuple[str, ...]):
        """Genera sustituciones que prueban la meta: primero hechos, luego reglas en orden"""
        meta = apply_atom(meta, subst)
        clave = str(meta)
        if clave in pila:
            eventos.append(f"{sangria(prof)}ciclo: {meta} ya está en la pila de metas, se corta")
            return
        if prof > max_prof:
            eventos.append(f"{sangria(prof)}profundidad máxima en {meta}")
            return

        eventos.append(f"{sangria(prof)}meta   {meta}")
        metas_visitadas.append(meta)
        probada = False

        for hecho in kb.facts:
            theta = unify(meta, hecho, subst)
            if theta is not None:
                eventos.append(f"{sangria(prof)}hecho  {hecho}")
                probada = True
                yield theta

        for regla in kb.rules:
            contador[0] += 1
            fresca = renombrar(regla, contador[0])
            theta = unify(meta, fresca.head, subst)
            if theta is None:
                continue
            eventos.append(f"{sangria(prof)}regla  {regla.rule_id} {format_subst(theta)}")
            for respuesta in bc_and(fresca.premises, theta, prof + 1, pila + (clave,)):
                probada = True
                yield respuesta

        if not probada:
            eventos.append(f"{sangria(prof)}falla  {meta}")

    def bc_and(premisas: tuple[Atom, ...], subst: dict[str, str], prof: int, pila: tuple[str, ...]):
        if not premisas:
            yield subst
            return
        primera, resto = premisas[0], premisas[1:]
        for theta in bc_or(primera, subst, prof, pila):
            yield from bc_and(resto, theta, prof, pila)

    # Se acepta la primera prueba y no se busca más.
    encontrada = next(bc_or(query, {}, 0, ()), None)
    probada = encontrada is not None
    eventos.append("Consulta probada." if probada else "Consulta NO probada.")

    unicas: list[Atom] = []
    vistas: set[str] = set()
    for m in metas_visitadas:
        if str(m) not in vistas:
            vistas.add(str(m))
            unicas.append(m)
    return InferenceResult(probada, encontrada, unicas, eventos)
