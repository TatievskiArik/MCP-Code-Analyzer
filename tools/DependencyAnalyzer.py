import ast

class DependencyAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path

    def analyze(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=self.file_path)
        except SyntaxError:
            return [], []

        imports = []
        usages = []

        class Analyzer(ast.NodeVisitor):
            def visit_ImportFrom(self, node):
                if node.module:
                    for alias in node.names:
                        imports.append((node.module, alias.name))

            def visit_Import(self, node):
                for alias in node.names:
                    imports.append((alias.name, None))

            def visit_Name(self, node):
                usages.append(node.id)

        Analyzer().visit(tree)
        return imports, usages
