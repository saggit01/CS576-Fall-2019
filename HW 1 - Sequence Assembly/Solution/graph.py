class DirectedGraph:
    """Abstract base class for a directed graph.

    A functional directed graph class can be obtained by inheriting from 
    this class and overriding the methods has_edge and add_edge.  All other
    methods have default implementations, which may not be the most efficient.
    These other methods should also be overriden as appropriate to improve
    efficiency.
    """
    def __init__(self, num_vertices):
        """Constructs a directed graph with num_vertices vertices and zero edges"""
        self._num_vertices = num_vertices
    
    def has_edge(self, i, j):
        """Returns True if the graph contains the directed edge (i, j), False otherwise."""
        raise NotImplementedError
        
    def add_edge(self, i, j):
        """Adds the directed edge (i, j) to the graph."""
        raise NotImplementedError
        
    def out_edges(self, i):
        """Returns a list of directed edges outgoing from vertex i."""
        return [(i, j) for j in range(self._num_vertices) if self.has_edge(i, j)]
    
    def in_edges(self, j):
        """Returns a list of directed edges incoming to vertex j."""
        return [(i, j) for i in range(self._num_vertices) if self.has_edge(i, j)]
    
    def outdegree(self, i):
        """Returns the outdegree of vertex i."""
        return len(self.out_edges(i))
    
    def indegree(self, i):
        """Returns the indegree of vertex i."""
        return len(self.in_edges(i))
    
    def degree(self, i):
        """Returns the degree of vertex i."""
        return self.indegree(i) + self.outdegree(i)
        
    def add_edges(self, edges):
        """Adds all edges from a list to the graph."""
        for i, j in edges:
            self.add_edge(i, j)
            
    def num_vertices(self):
        """Returns the number of vertices in the graph."""
        return self._num_vertices

    def num_edges(self):
        """Returns the number of edges in the graph."""
        return len(tuple(self.edges()))
    
    def edges(self):
        """Returns an iterator over the edges of the graph."""
        for i in range(self._num_vertices):
            for edge in self.out_edges(i):
                yield edge
    
    def __str__(self):
        """Returns a string representation of the graph, so that it may be printed."""
        return "DirectedGraph with %d vertices and %d edge(s):\n%s" % (self.num_vertices(),
                                                                       self.num_edges(),
                                                                       sorted(self.edges()))

class TrivialSetDirectedGraph(DirectedGraph):
    """A trivial implementation of a Directed Graph that simply stores edges in a set.
    Not meant for serious use.
    """
    
    def __init__(self, num_vertices):
        # call the next constructor in Python's Method Resolution Order
        super().__init__(num_vertices)
        # start with an empty set of edges
        self._edges = set()
    
    def has_edge(self, i, j):
        return (i, j) in self._edges
        
    def add_edge(self, i, j):
        self._edges.add((i, j))
        
class AdjacencyListDirectedGraph(DirectedGraph):
    """An implementation of a Directed Graph that uses adjacency lists to store edges."""
        
    def __init__(self, num_vertices):
        super().__init__(num_vertices)
        self._out_lists = [[] for i in range(num_vertices)]
        self._in_lists = [[] for i in range(num_vertices)]
    
    def add_edge(self, i, j):
        self._out_lists[i].append(j)
        self._in_lists[j].append(i)
    
    def has_edge(self, i, j):
        return j in self._out_lists[i]
        
    def out_edges(self, i):
        return [(i, j) for j in self._out_lists[i]]
        
    def in_edges(self, j):
        return [(i, j) for i in self._in_lists[j]]
    
    def indegree(self, i):
        return len(self._in_lists[i])
        
    def outdegree(self, i):
        return len(self._out_lists[i])
    
    
class VertexLabeledDirectedGraph(DirectedGraph):
    """A mixin class that allows for vertices in a directed graph to have labels."""
    
    def __init__(self, num_vertices):
        # call the next constructor in Python's Method Resolution Order
        super().__init__(num_vertices)
        self._vertex_labels = [None] * num_vertices

    def set_vertex_label(self, i, label):
        """Adds a label to vertex i."""
        self._vertex_labels[i] = label
       
    def vertex_label(self, i):
        """Returns the label of vertex i or None if it is not assigned a label"""
        return self._vertex_labels[i]
    

class EdgeWeightedDirectedGraph(DirectedGraph):
    """A mixin class that allows for edges in a directed graph to have weights."""
    
    def __init__(self, num_vertices):
        # call the next constructor in Python's Method Resolution Order
        super().__init__(num_vertices)
        self._edge_weights = dict()

    def add_weighted_edge(self, i, j, weight):
        """Adds an edge to the graph with the given weight."""        
        self.add_edge(i, j)
        self._edge_weights[(i, j)] = weight
       
    def edge_weight(self, i, j):
        """Returns the weight of edge (i, j) or None if it is not assigned a weight"""
        return self._edge_weights.get((i, j), None)
    
class ComponentTrackingGraph(DirectedGraph):
    """A mixin class that keeps track of the connected components of the graph."""
    
    def __init__(self, num_vertices):
        # call the next constructor in Python's Method Resolution Order
        super().__init__(num_vertices)
        # each vertex is its own component to start
        self._components = {i: [i] for i in range(num_vertices)}
        self._vertex_to_component_id = [i for i in range(num_vertices)]
    
    def add_edge(self, i, j):
        """Adds an edge to the graph and updates the connected components."""
        super().add_edge(i, j)
        if not self.are_in_same_component(i, j):
            # obtain the ids of the two components and determine which component is bigger
            big_id, small_id = self._vertex_to_component_id[i], self._vertex_to_component_id[j]
            if len(self._components[big_id]) < len(self._components[small_id]):
                big_id, small_id = small_id, big_id
                                   
            # merge smaller component into bigger
            self._components[big_id].extend(self._components[small_id])
            for k in self._components[small_id]:
                self._vertex_to_component_id[k] = big_id
            del self._components[small_id]
        
    def are_in_same_component(self, i, j):
        """Returns True if vertices i and j are in the same connected component."""
        return self._vertex_to_component_id[i] == self._vertex_to_component_id[j]
        
    def num_components(self):
        """Returns the number of connected components in the graph."""
        return len(self._components)
