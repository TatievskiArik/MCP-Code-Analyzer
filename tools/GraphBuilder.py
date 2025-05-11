import os
import json
import uuid
from .Graph import Graph
from .DependencyAnalyzer import DependencyAnalyzer

class GraphBuilder:
    def __init__(self, repo_path: str, filter_prefix: str = "src"):
        self.repo_path = repo_path
        self.filter_prefix = filter_prefix
        self.graph = Graph()

    def build(self):
        # Step 1: Create nodes
        for root, _, files in os.walk(self.repo_path):
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue
            for file in files:
                if file.endswith(".py") and not file.startswith("__init__"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.repo_path)
                    if not rel_path.startswith(self.filter_prefix):
                        continue
                    mod_name = rel_path.replace(os.sep, ".").replace(".py", "")
                    self.graph.add_node(mod_name, full_path)

        # Step 2: Create arcs
        for source_name, source_node in self.graph.nodes.items():
            analyzer = DependencyAnalyzer(source_node.path)
            imports, usages = analyzer.analyze()
            usage_set = set(usages)

            for imported_module, imported_name in imports:
                for target_name, target_node in self.graph.nodes.items():
                    if target_name.endswith(imported_module) or target_name == imported_module:
                        if imported_name is None:
                            continue
                        if imported_name in usage_set:
                            self.graph.add_arc(source_node, target_node, imported_name)

        return self.graph
    def export_graph(self) -> str:
        base_dir = os.path.abspath(".")
        output_folder = os.path.join(base_dir, "files")
        uid = str(uuid.uuid4())
        filename = f"{uid}.json"
        filepath = os.path.normpath(os.path.join(output_folder, filename))
        print(f"Saving to: {filepath}")
        # Actually save the file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.graph.to_dict(), f, indent=2)
        return filepath
