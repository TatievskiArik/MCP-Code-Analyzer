class Node:
    def __init__(self, name: str, path: str):
        self.name = name 
        self.path = path  

class Arc:
    def __init__(self, source: Node, target: Node, symbol: str):
        self.source = source
        self.target = target
        self.symbol = symbol 

class Graph:
    def __init__(self):
        self.nodes = {}
        self.arcs = []

    def add_node(self, name: str, path: str):
        node = Node(name, path)
        self.nodes[name] = node
        return node

    def add_arc(self, source: Node, target: Node, symbol: str):
        arc = Arc(source, target, symbol)
        self.arcs.append(arc)

    def to_dict(self):
        return {
            "nodes": list(self.nodes.keys()),
            "arcs": [
                {"source": arc.source.name, "target": arc.target.name, "symbol": arc.symbol}
                for arc in self.arcs
            ]
        }

