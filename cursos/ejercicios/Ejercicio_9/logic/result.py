"""Resultado común de los dos algoritmos de inferencia"""

from __future__ import annotations

from dataclasses import dataclass, field

from logic.atoms import Atom


@dataclass
class InferenceResult:
    proved: bool
    subst: dict[str, str] | None
    # Hacia adelante: átomos nuevos derivados. Hacia atrás: metas visitadas
    inferred: list[Atom]
    events: list[str] = field(default_factory=list)
