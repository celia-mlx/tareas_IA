from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from logic.atoms import Atom, parse_atom


@dataclass(frozen=True)
class Rule:
    rule_id: str
    premises: tuple[Atom, ...]
    head: Atom


@dataclass
class KnowledgeBase:
    facts: list[Atom] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)

    def with_extra_facts(self, extra: list[Atom]) -> "KnowledgeBase":
        """Copia de la base con hechos añadidos al final (no modifica la original)"""
        return KnowledgeBase(self.facts + list(extra), list(self.rules))


def load_kb(path: str | Path) -> tuple[KnowledgeBase, list[Atom]]:
    """Lee el YAML y devuelve (base, consultas), respetando el orden del archivo"""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    facts = [parse_atom(f) for f in data.get("facts", [])]
    rules = [
        Rule(
            r["id"],
            tuple(parse_atom(p) for p in r["if"]),
            parse_atom(r["then"]),
        )
        for r in data.get("rules", [])
    ]
    raw_queries = data.get("queries")
    if raw_queries is None:
        raw_queries = [data["query"]] if "query" in data else []
    queries = [parse_atom(q) for q in raw_queries]
    return KnowledgeBase(facts, rules), queries
