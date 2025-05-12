import json
from typing import List, Dict, Tuple

def load_graph(filepath: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    arcs_raw = data.get("arcs", {})
    arcs = []
    # for source, dependencies in arcs_raw.items():
    #     for dep in dependencies:
    #         for target, dependency in dep.items():
    #             arcs.append((source, target, dependency))  # (from, to, what)
    return nodes, arcs_raw