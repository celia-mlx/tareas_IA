from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Atom:
    predicate: str
    args: tuple[str, ...]

    def __str__(self) -> str:
        return f"{self.predicate}({', '.join(self.args)})"


_ATOM_RE = re.compile(r"^\s*(\w+)\s*\(([^)]*)\)\s*$")


def parse_atom(text: str) -> Atom:
    match = _ATOM_RE.match(text)
    if not match:
        raise ValueError(f"Átomo mal formado: {text!r}")
    args = tuple(a.strip() for a in match.group(2).split(",") if a.strip())
    return Atom(match.group(1), args)


def is_var(term: str) -> bool:
    return term[:1].islower()


def walk(term: str, subst: dict[str, str]) -> str:
    """Sigue la cadena de sustituciones hasta una constante o variable libre"""
    while is_var(term) and term in subst:
        term = subst[term]
    return term


def unify(a: Atom, b: Atom, subst: dict[str, str]) -> dict[str, str] | None:
    """Unifica dos átomos devuelve la sustitución extendida o None"""
    if a.predicate != b.predicate or len(a.args) != len(b.args):
        return None
    theta = dict(subst)
    for x, y in zip(a.args, b.args):
        x, y = walk(x, theta), walk(y, theta)
        if x == y:
            continue
        if is_var(x):
            theta[x] = y
        elif is_var(y):
            theta[y] = x
        else:
            return None
    return theta


def apply_atom(atom: Atom, subst: dict[str, str]) -> Atom:
    return Atom(atom.predicate, tuple(walk(t, subst) for t in atom.args))


def format_subst(subst: dict[str, str]) -> str:
    """Muestra solo las variables ligadas a constantes"""
    shown = {}
    for var in subst:
        value = walk(var, subst)
        if not is_var(value):
            shown[var.rsplit("_", 1)[0]] = value
    return "{" + ", ".join(f"{k}: {v}" for k, v in shown.items()) + "}"
