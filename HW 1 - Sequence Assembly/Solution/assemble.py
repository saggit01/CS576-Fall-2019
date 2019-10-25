import graph

def overlap(s1, s2):
    """The length of the longest match between the a suffix of s1 and a prefix of s2"""
    for i in range(min(len(s1), len(s2)), 0, -1):
        if s1.endswith(s2[:i]):
            return i
    return 0

def source(g):
    """Returns the first vertex in a graph that has indegree == 0"""
    for i in range(g.num_vertices()):
        if g.indegree(i) == 0:
            return i
    else:
        return None

def superstring(g):
    """Returns the superstring represented by an OverlapGraph containing a single path"""
    substrings = []
    last_overlap = 0
    i = source(g)
    while True:
        substrings.append(g.vertex_label(i)[last_overlap:])
        if g.outdegree(i) > 0:
            j = g.out_edges(i)[0][1]
            last_overlap = g.edge_weight(i, j)
            i = j
        else:
            break
    return "".join(substrings)

class OverlapGraph(graph.ComponentTrackingGraph,
                   graph.VertexLabeledDirectedGraph,
                   graph.EdgeWeightedDirectedGraph,                   
                   graph.AdjacencyListDirectedGraph):
    """A graph for representing reads and read overlaps for fragment assembly."""
    pass

def greedy_assemble(reads):
    # Construct initial read graph without any edges
    g = OverlapGraph(len(reads))
    for i, read in enumerate(reads):
        g.set_vertex_label(i, read)
        
    # Construct a queue of edges
    edges = [(i, j, overlap(reads[i], reads[j]))
             for i in range(len(reads)) for j in range(len(reads))]
    # Sort edges by decreasing weight, with lexicographical comparison of
    # read strings of edge vertices as tiebreaker              
    edges.sort(key=lambda edge: (-edge[2], reads[edge[0]], reads[edge[1]]))
    
     # Add edges one by one
    while g.num_components() > 1:
        i, j, weight = edges.pop(0)
        if (g.outdegree(i) == 0 and
            g.indegree(j) == 0 and
            not g.are_in_same_component(i, j)):
            g.add_weighted_edge(i, j, weight)

    # return the superstring represented by the path in the graph
    return superstring(g)
