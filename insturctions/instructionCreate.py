def create_insturction(nodes,arcs) -> str:

    return(f"""
    You are a code analyzer. You have been provided with a dependency graph that represents project modules and the dependencies between these modules.
    Your task is to answers questions specifically related to the modules. Your answer should help understand the functionality, importance, and relationships of the specified module within the context of the overall project.
    Dependency Graph Build:
    Nodes - a list of module names, each module is a node in the graph.
    Arcs - a list of tuples, each tuple represents a directed edge from one module to another, along with the type of dependency (example: read(module that uses), write(module that is being used), timeOut(the dependency))
    The dependency graph is described as follows:
    Nodes: {nodes}
    Arcs: {arcs}
    """)
